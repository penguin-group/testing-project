
import logging
import re
from ast import literal_eval
from collections import defaultdict


from odoo.addons.web.controllers.utils import clean_action
from odoo import models, fields, api, _, osv
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
from odoo.tools.float_utils import float_round
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from odoo.tools.safe_eval import expr_eval, safe_eval
from odoo.models import check_method_name

_logger = logging.getLogger(__name__)

ACCOUNT_CODES_ENGINE_SPLIT_REGEX = re.compile(r"(?=[+-])")

ACCOUNT_CODES_ENGINE_TERM_REGEX = re.compile(
    r"^(?P<sign>[+-]?)"\
    r"(?P<prefix>[A-Za-z\d.]*((?=\\)|(?<=[^CD])))"\
    r"(\\\((?P<excluded_prefixes>([A-Za-z\d.]+,)*[A-Za-z\d.]*)\))?"\
    r"(?P<balance_character>[DC]?)$"
)




class AccountReport(models.Model):
    _inherit = 'account.report'
    
    def _compute_formula_batch_with_engine_tax_tags(self, options, date_scope, formulas_dict, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        """ Report engine.

        The formulas made for this report simply consist of a tag label. When an expression using this engine is created, it also creates two
        account.account.tag objects, namely -tag and +tag, where tag is the chosen formula. The balance of the expressions using this engine is
        computed by gathering all the move lines using their tags, and applying the sign of their tag to their balance, together with a -1 factor
        if the tax_tag_invert field of the move line is True.

        This engine does not support any subformula.
        """
        self._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))
        all_expressions = self.env['account.report.expression']
        for expressions in formulas_dict.values():
            all_expressions |= expressions
        tags = all_expressions._get_matching_tags()

        currency_table_query = self._get_query_currency_table(options)
        groupby_sql = f'account_move_line.{current_groupby}' if current_groupby else None
        tables, where_clause, where_params = self._query_get(options, date_scope)
        tail_query, tail_params = self._get_engine_query_tail(offset, limit)
        if self.pool['account.account.tag'].name.translate:
            lang = self.env.user.lang or get_lang(self.env).code
            acc_tag_name = f"COALESCE(acc_tag.name->>'{lang}', acc_tag.name->>'en_US')"
        else:
            acc_tag_name = 'acc_tag.name'
        sql = f"""
            SELECT
                SUBSTRING({acc_tag_name}, 2, LENGTH({acc_tag_name}) - 1) AS formula,
                SUM(ROUND(COALESCE(account_move_line.balance, 0) * currency_table.rate, currency_table.precision)
                    * CASE WHEN acc_tag.tax_negate THEN -1 ELSE 1 END
                    * CASE WHEN account_move_line.tax_tag_invert THEN -1 ELSE 1 END
                ) AS balance,
                SUM(ROUND(COALESCE(account_move_line.balance_ms, 2))
                    * CASE WHEN acc_tag.tax_negate THEN -1 ELSE 1 END
                    * CASE WHEN account_move_line.tax_tag_invert THEN -1 ELSE 1 END
                ) AS balance_ms,
                SUM(ROUND(COALESCE(account_move_line.balance_cs, 2))
                    * CASE WHEN acc_tag.tax_negate THEN -1 ELSE 1 END
                    * CASE WHEN account_move_line.tax_tag_invert THEN -1 ELSE 1 END
                ) AS balance_cs,
                COUNT(account_move_line.id) AS aml_count
                {f', {groupby_sql} AS grouping_key' if groupby_sql else ''}

            FROM {tables}

            JOIN account_account_tag_account_move_line_rel aml_tag
                ON aml_tag.account_move_line_id = account_move_line.id
            JOIN account_account_tag acc_tag
                ON aml_tag.account_account_tag_id = acc_tag.id
                AND acc_tag.id IN %s
            JOIN {currency_table_query}
                ON currency_table.company_id = account_move_line.company_id

            WHERE {where_clause}

            GROUP BY SUBSTRING({acc_tag_name}, 2, LENGTH({acc_tag_name}) - 1)
                {f', {groupby_sql}' if groupby_sql else ''}

            {tail_query}
        """

        params = [tuple(tags.ids)] + where_params + tail_params
        self._cr.execute(sql, params)

        rslt = {formula_expr: [] if current_groupby else {'result': 0, 'has_sublines': False} for formula_expr in formulas_dict.items()}
        for query_res in self._cr.dictfetchall():

            formula = query_res['formula']
            rslt_dict = {'result': query_res['balance'], 'has_sublines': query_res['aml_count'] > 0}
            for formula_expr in formulas_dict[formula]:
                if current_groupby:
                    rslt[(formula, formula_expr)].append((query_res['grouping_key'], rslt_dict))
                else:
                    rslt[(formula, formula_expr)] = rslt_dict

        return rslt

    def _compute_formula_batch_with_engine_domain(self, options, date_scope, formulas_dict, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        """ Report engine.

        Formulas made for this engine consist of a domain on account.move.line. Only those move lines will be used to compute the result.

        This engine supports a few subformulas, each returning a slighlty different result:
        - sum: the result will be sum of the matched move lines' balances

        - sum_if_pos: the result will be the same as sum only if it's positive; else, it will be 0

        - sum_if_neg: the result will be the same as sum only if it's negative; else, it will be 0

        - count_rows: the result will be the number of sublines this expression has. If the parent report line has no groupby,
                      then it will be the number of matching amls. If there is a groupby, it will be the number of distinct grouping
                      keys at the first level of this groupby (so, if groupby is 'partner_id, account_id', the number of partners).
        """
        def _format_result_depending_on_groupby(formula_rslt):
            if not current_groupby:
                if formula_rslt:
                    # There should be only one element in the list; we only return its totals (a dict) ; so that a list is only returned in case
                    # of a groupby being unfolded.
                    return formula_rslt[0][1]
                else:
                    # No result at all
                    return {
                        'sum': 0,
                        'sum_ms':0,
                        'sum_cs':0,
                        'sum_if_pos': 0,
                        'sum_if_neg': 0,
                        'count_rows': 0,
                        'has_sublines': False,
                    }
            return formula_rslt

        self._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        groupby_sql = f'account_move_line.{current_groupby}' if current_groupby else None
        ct_query = self._get_query_currency_table(options)

        rslt = {}

        for formula, expressions in formulas_dict.items():
            line_domain = literal_eval(formula)
            tables, where_clause, where_params = self._query_get(options, date_scope, domain=line_domain)

            tail_query, tail_params = self._get_engine_query_tail(offset, limit)
            query = f"""
                SELECT
                    COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS sum,
                    COALESCE(SUM(ROUND(account_move_line.balance_ms,2 ))) AS sum_ms,
                    COALESCE(SUM(ROUND(account_move_line.balance_cs,2 ))) AS sum_cs,
                    COUNT(DISTINCT account_move_line.{next_groupby.split(',')[0] if next_groupby else 'id'}) AS count_rows
                    {f', {groupby_sql} AS grouping_key' if groupby_sql else ''}
                FROM {tables}
                JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                WHERE {where_clause}
                {f' GROUP BY {groupby_sql}' if groupby_sql else ''}
                {tail_query}
            """

            # Fetch the results.
            formula_rslt = []
            self._cr.execute(query, where_params + tail_params)
            all_query_res = self._cr.dictfetchall()

            total_sum = 0
            total_sum_ms = 0
            total_sum_cs = 0
            
            for query_res in all_query_res:
                res_sum = query_res['sum']
                if query_res.get('sum_ms')!=None:
                    res_sum_ms = query_res.get('sum_ms',0) 
                else:
                    res_sum_ms=0
                if query_res.get('sum_cs')!=None:
                    res_sum_cs = query_res.get('sum_cs',0) 
                else:
                    res_sum_cs=0
                total_sum += res_sum
                total_sum_ms += res_sum_ms
                total_sum_cs += res_sum_cs
                totals = {
                    'sum': res_sum,
                    'sum_ms': res_sum_ms,
                    'sum_cs': res_sum_cs,
                    'sum_if_pos': 0,
                    'sum_if_neg': 0,
                    'count_rows': query_res['count_rows'],
                    'has_sublines': query_res['count_rows'] > 0,
                }
                formula_rslt.append((query_res.get('grouping_key', None), totals))

            # Handle sum_if_pos, -sum_if_pos, sum_if_neg and -sum_if_neg
            expressions_by_sign_policy = defaultdict(lambda: self.env['account.report.expression'])
            for expression in expressions:
                subformula_without_sign = expression.subformula.replace('-', '').strip()
                if subformula_without_sign in ('sum_if_pos', 'sum_if_neg'):
                    expressions_by_sign_policy[subformula_without_sign] += expression
                else:
                    expressions_by_sign_policy['no_sign_check'] += expression

            # Then we have to check the total of the line and only give results if its sign matches the desired policy.
            # This is important for groupby managements, for which we can't just check the sign query_res by query_res
            if expressions_by_sign_policy['sum_if_pos'] or expressions_by_sign_policy['sum_if_neg']:
                sign_policy_with_value = 'sum_if_pos' if self.env.company.currency_id.compare_amounts(total_sum, 0.0) >= 0 else 'sum_if_neg'
                # >= instead of > is intended; usability decision: 0 is considered positive

                formula_rslt_with_sign = [(grouping_key, {**totals, sign_policy_with_value: totals['sum']}) for grouping_key, totals in formula_rslt]

                for sign_policy in ('sum_if_pos', 'sum_if_neg'):
                    policy_expressions = expressions_by_sign_policy[sign_policy]

                    if policy_expressions:
                        if sign_policy == sign_policy_with_value:
                            rslt[(formula, policy_expressions)] = _format_result_depending_on_groupby(formula_rslt_with_sign)
                        else:
                            rslt[(formula, policy_expressions)] = _format_result_depending_on_groupby([])

            if expressions_by_sign_policy['no_sign_check']:
                rslt[(formula, expressions_by_sign_policy['no_sign_check'])] = _format_result_depending_on_groupby(formula_rslt)

        return rslt
    
    
    def _compute_formula_batch_with_engine_account_codes(self, options, date_scope, formulas_dict, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        r""" Report engine.

        Formulas made for this engine target account prefixes. Each of the prefix used in the formula will be evaluated as the sum of the move
        lines made on the accounts matching it. Those prefixes can be used together with arithmetic operations to perform them on the obtained
        results.
        Example: '123 - 456' will substract the balance of all account starting with 456 from the one of all accounts starting with 123.

        It is also possible to exclude some subprefixes, with \ operator.
        Example: '123\(1234)' will match prefixes all accounts starting with '123', except the ones starting with '1234'

        To only match the balance of an account is it's positive (debit) or negative (credit), the letter D or C can be put just next to the prefix:
        Example '123D': will give the total balance of accounts starting with '123' if it's positive, else it will be evaluated as 0.

        Multiple subprefixes can be excluded if needed.
        Example: '123\(1234,1236)

        All these syntaxes can be mixed together.
        Example: '123D\(1235) + 56 - 416C'

        Note: if C or D character needs to be part of the prefix, it is possible to differentiate them of debit and credit match characters
        by using an empty prefix exclusion.
        Example 1: '123D\' will take the total balance of accounts starting with '123D'
        Example 2: '123D\C' will return the balance of accounts starting with '123D' if it's negative, 0 otherwise.
        """
        self._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        # Gather the account code prefixes to compute the total from
        prefix_details_by_formula = {}  # in the form {formula: [(1, prefix1), (-1, prefix2)]}
        prefixes_to_compute = set()
        for formula in formulas_dict:
            prefix_details_by_formula[formula] = []
            for token in ACCOUNT_CODES_ENGINE_SPLIT_REGEX.split(formula.replace(' ', '')):
                if token:
                    token_match = ACCOUNT_CODES_ENGINE_TERM_REGEX.match(token)

                    if not token_match:
                        raise UserError(_("Invalid token '%s' in account_codes formula '%s'", token, formula))

                    parsed_token = token_match.groupdict()

                    if not parsed_token:
                        raise UserError(_("Could not parse account_code formula from token '%s'", token))

                    multiplicator = -1 if parsed_token['sign'] == '-' else 1
                    excluded_prefixes_match = token_match['excluded_prefixes']
                    excluded_prefixes = excluded_prefixes_match.split(',') if excluded_prefixes_match else []
                    prefix = token_match['prefix']

                    # We group using both prefix and excluded_prefixes as keys, for the case where two expressions would
                    # include the same prefix, but exlcude different prefixes (example 104\(1041) and 104\(1042))
                    prefix_key = (prefix, *excluded_prefixes)
                    prefix_details_by_formula[formula].append((multiplicator, prefix_key, token_match['balance_character']))
                    prefixes_to_compute.add((prefix, tuple(excluded_prefixes)))

        # Create the subquery for the WITH linking our prefixes with account.account entries
        all_prefixes_queries = []
        prefix_params = []
        company_ids = [comp_opt['id'] for comp_opt in options.get('multi_company', self.env.company)]
        for prefix, excluded_prefixes in prefixes_to_compute:
            account_domain = [('company_id', 'in', company_ids), ('code', '=like', f'{prefix}%')]
            excluded_prefixes_domains = []

            for excluded_prefix in excluded_prefixes:
                excluded_prefixes_domains.append([('code', '=like', f'{excluded_prefix}%')])

            if excluded_prefixes_domains:
                account_domain.append('!')
                account_domain += osv.expression.OR(excluded_prefixes_domains)

            prefix_tables, prefix_where_clause, prefix_where_params = self.env['account.account']._where_calc(account_domain).get_sql()

            prefix_params.append(prefix)
            for excluded_prefix in excluded_prefixes:
                prefix_params.append(excluded_prefix)

            prefix_select_query = ', '.join(['%s'] * (len(excluded_prefixes) + 1)) # +1 for prefix
            prefix_select_query = f'ARRAY[{prefix_select_query}]'

            all_prefixes_queries.append(f"""
                SELECT
                    {prefix_select_query} AS prefix,
                    account_account.id AS account_id
                FROM {prefix_tables}
                WHERE {prefix_where_clause}
            """)
            prefix_params += prefix_where_params

        # Build a map to associate each account with the prefixes it matches
        accounts_prefix_map = defaultdict(list)
        self._cr.execute(' UNION ALL '.join(all_prefixes_queries), prefix_params)
        for prefix, account_id in self._cr.fetchall():
            accounts_prefix_map[account_id].append(tuple(prefix))

        # Run main query
        tables, where_clause, where_params = self._query_get(options, date_scope)

        currency_table_query = self._get_query_currency_table(options)
        extra_groupby_sql = f', account_move_line.{current_groupby}' if current_groupby else ''
        extra_select_sql = f', account_move_line.{current_groupby} AS grouping_key' if current_groupby else ''
        tail_query, tail_params = self._get_engine_query_tail(offset, limit)

        query = f"""
            SELECT
                account_move_line.account_id AS account_id,
                SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS sum,
                SUM(ROUND(account_move_line.balance_ms,2)) AS sum_ms,
                SUM(ROUND(account_move_line.balance_cs,2)) AS sum_cs,
                COUNT(account_move_line.id) AS aml_count
                {extra_select_sql}
            FROM {tables}
            JOIN {currency_table_query} ON currency_table.company_id = account_move_line.company_id
            WHERE {where_clause}
            GROUP BY account_move_line.account_id{extra_groupby_sql}
            {tail_query}
        """
        self._cr.execute(query, where_params + tail_params)

        # Parse result
        rslt = {}

        res_by_prefix_account_id = {}
        for query_res in self._cr.dictfetchall():
            # Done this way so that we can run similar code for groupby and non-groupby
            grouping_key = query_res['grouping_key'] if current_groupby else None
            account_id = query_res['account_id']
            for prefix_key in accounts_prefix_map[account_id]:
                res_by_prefix_account_id.setdefault(prefix_key, {})\
                                        .setdefault(account_id, [])\
                                        .append((grouping_key, {'result': query_res['sum'], 'has_sublines': query_res['aml_count'] > 0}))

        for formula, prefix_details in prefix_details_by_formula.items():
            rslt_key = (formula, formulas_dict[formula])
            rslt_destination = rslt.setdefault(rslt_key, [] if current_groupby else {'result': 0, 'has_sublines': False})
            for multiplicator, prefix_key, balance_character in prefix_details:
                res_by_account_id = res_by_prefix_account_id.get(prefix_key, {})

                for account_results in res_by_account_id.values():
                    account_total_value = sum(group_val['result'] for (group_key, group_val) in account_results)
                    comparator = self.env.company.currency_id.compare_amounts(account_total_value, 0.0)

                    # Manage balance_character.
                    if not balance_character or (balance_character == 'D' and comparator >= 0) or (balance_character == 'C' and comparator < 0):

                        for group_key, group_val in account_results:
                            rslt_group = {
                                **group_val,
                                'result': multiplicator * group_val['result'],
                            }

                            if current_groupby:
                                rslt_destination.append((group_key, rslt_group))
                            else:
                                rslt_destination['result'] += rslt_group['result']
                                rslt_destination['has_sublines'] = rslt_destination['has_sublines'] or rslt_group['has_sublines']

        return rslt
