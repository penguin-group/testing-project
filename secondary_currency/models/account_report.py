from odoo import models, _,api
from odoo.exceptions import UserError
from ast import literal_eval
from collections import defaultdict
from odoo.tools import get_lang, SQL
import re

NUMBER_FIGURE_TYPES = ('float', 'integer', 'monetary', 'percentage')
CURRENCIES_USING_LAKH = {'AFN', 'BDT', 'INR', 'MMK', 'NPR', 'PKR', 'LKR'}

ACCOUNT_CODES_ENGINE_SPLIT_REGEX = re.compile(r"(?=[+-])")
ACCOUNT_CODES_ENGINE_TERM_REGEX = re.compile(
    r"^(?P<sign>[+-]?)"
    r"(?P<prefix>([A-Za-z\d.]*|tag\([\w.]+\))((?=\\)|(?<=[^CD])))"
    r"(\\\((?P<excluded_prefixes>([A-Za-z\d.]+,)*[A-Za-z\d.]*)\))?"
    r"(?P<balance_character>[DC]?)$"
)
ACCOUNT_CODES_ENGINE_TAG_ID_PREFIX_REGEX = re.compile(r"tag\(((?P<id>\d+)|(?P<ref>\w+\.\w+))\)")


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _compute_formula_batch_with_engine_tax_tags(self, options, date_scope, formulas_dict, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        """ 
        [OVERRIDE] Full override of `account.report._compute_formula_batch_with_engine_tax_tags` method.

        Reason:
        - super() could not be used because we should include a variable in the SQL query that is not present in the original method
        - the value resulting from the SQL query should be compatible with the Currency Switch of the report

        Original method:
        - Location: `enterprise/account_reports/account_report.py`
        - Method: `_compute_formula_batch_with_engine_tax_tags`
        - Odoo Version: 18.0

        Modifications summary:
        - [ADDED] selected_balance variable to select the balance of the correct currency
        - [ADDED] Use the previous variable in the sum
        
        
        Report engine.

        The formulas made for this report simply consist of a tag label. When an expression using this engine is created, it also creates two
        account.account.tag objects, namely -tag and +tag, where tag is the chosen formula. The balance of the expressions using this engine is
        computed by gathering all the move lines using their tags, and applying the sign of their tag to their balance, together with a -1 factor
        if the tax_tag_invert field of the move line is True.

        This engine does not support any subformula.
        """
        # [ADDED] Start: selected_balance variable to select the balance of the correct currency
        selected_balance = 'secondary_balance' if options['currencies_selected_name'] == self.env.user.company_id.sec_currency_id.name else 'balance'
        # [ADDED] End

        self._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))
        all_expressions = self.env['account.report.expression']
        for expressions in formulas_dict.values():
            all_expressions |= expressions
        tags = all_expressions._get_matching_tags()

        query = self._get_report_query(options, date_scope)
        groupby_sql = self.env['account.move.line']._field_to_sql('account_move_line', current_groupby, query) if current_groupby else None
        tail_query = self._get_engine_query_tail(offset, limit)
        lang = get_lang(self.env, self.env.user.lang).code
        acc_tag_name = self.with_context(lang='en_US').env['account.account.tag']._field_to_sql('acc_tag', 'name')
        sql = SQL(
            """
            SELECT
                SUBSTRING(%(acc_tag_name)s, 2, LENGTH(%(acc_tag_name)s) - 1) AS formula,
                SUM(%(balance_select)s
                    * CASE WHEN acc_tag.tax_negate THEN -1 ELSE 1 END
                    * CASE WHEN account_move_line.tax_tag_invert THEN -1 ELSE 1 END
                ) AS balance,
                COUNT(account_move_line.id) AS aml_count
                %(select_groupby_sql)s

            FROM %(table_references)s

            JOIN account_account_tag_account_move_line_rel aml_tag
                ON aml_tag.account_move_line_id = account_move_line.id
            JOIN account_account_tag acc_tag
                ON aml_tag.account_account_tag_id = acc_tag.id
                AND acc_tag.id IN %(tag_ids)s
            %(currency_table_join)s

            WHERE %(search_condition)s

            GROUP BY %(groupby_clause)s

            ORDER BY %(groupby_clause)s

            %(tail_query)s
            """,
            acc_tag_name=acc_tag_name,
            select_groupby_sql=SQL(', %s AS grouping_key', groupby_sql) if groupby_sql else SQL(),
            table_references=query.from_clause,
            tag_ids=tuple(tags.ids),
            # [ADDED] Start: Use the previous variable in the sum
            balance_select=self._currency_table_apply_rate(SQL(f"account_move_line.{selected_balance}")),
            # [ADDED] End
            currency_table_join=self._currency_table_aml_join(options),
            search_condition=query.where_clause,
            groupby_clause=SQL(
                "SUBSTRING(%(acc_tag_name)s, 2, LENGTH(%(acc_tag_name)s) - 1)%(groupby_sql)s",
                acc_tag_name=acc_tag_name,
                groupby_sql=SQL(', %s', groupby_sql) if groupby_sql else SQL(),
            ),
            tail_query=tail_query,
        )

        self._cr.execute(sql)

        rslt = {formula_expr: [] if current_groupby else {'result': 0, 'has_sublines': False} for formula_expr in formulas_dict.items()}
        for query_res in self._cr.dictfetchall():

            formula = query_res['formula']
            rslt_dict = {'result': query_res['balance'], 'has_sublines': query_res['aml_count'] > 0}
            if current_groupby:
                rslt[(formula, formulas_dict[formula])].append((query_res['grouping_key'], rslt_dict))
            else:
                rslt[(formula, formulas_dict[formula])] = rslt_dict

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
        selected_balance = 'secondary_balance' if options['currencies_selected_name'] == self.env.user.company_id.sec_currency_id.name else 'balance'
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
                        'sum_if_pos': 0,
                        'sum_if_neg': 0,
                        'count_rows': 0,
                        'has_sublines': False,
                    }
            return formula_rslt

        self._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        groupby_sql = SQL.identifier('account_move_line', current_groupby) if current_groupby else None
        ct_query = self._get_currency_table(options)

        rslt = {}

        for formula, expressions in formulas_dict.items():
            try:
                line_domain = literal_eval(formula)
            except (ValueError, SyntaxError):
                raise UserError(_(
                    'Invalid domain formula in expression "%(expression)s" of line "%(line)s": %(formula)s',
                    expression=expressions.label,
                    line=expressions.report_line_id.name,
                    formula=formula,
                ))
            query = self._get_report_query(options, date_scope, domain=line_domain)

            tail_query = self._get_engine_query_tail(offset, limit)
            query = SQL(
                """
                SELECT
                    COALESCE(SUM(%(balance_select)s), 0.0) AS sum,
                    COUNT(DISTINCT account_move_line.%(select_count_field)s) AS count_rows
                    %(select_groupby_sql)s
                FROM %(table_references)s
                %(currency_table_join)s
                WHERE %(search_condition)s
                %(group_by_groupby_sql)s
                %(order_by_sql)s
                %(tail_query)s
                """,
                select_count_field=SQL.identifier(next_groupby.split(',')[0] if next_groupby else 'id'),
                select_groupby_sql=SQL(', %s AS grouping_key', groupby_sql) if groupby_sql else SQL(),
                table_references=query.from_clause,
                balance_select=self._currency_table_apply_rate(SQL(f"account_move_line.{selected_balance}")),
                currency_table_join=self._currency_table_aml_join(options),
                search_condition=query.where_clause,
                group_by_groupby_sql=SQL('GROUP BY %s', groupby_sql) if groupby_sql else SQL(),
                order_by_sql=SQL(' ORDER BY %s', groupby_sql) if groupby_sql else SQL(),
                tail_query=tail_query,
            )

            # Fetch the results.
            formula_rslt = []
            self._cr.execute(query)
            all_query_res = self._cr.dictfetchall()

            total_sum = 0
            for query_res in all_query_res:
                res_sum = query_res['sum']
                total_sum += res_sum
                totals = {
                    'sum': res_sum,
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

        selected_balance = 'secondary_balance' if options['currencies_selected_name'] == self.env.user.company_id.sec_currency_id.name else 'balance'
        # Gather the account code prefixes to compute the total from
        prefix_details_by_formula = {}  # in the form {formula: [(1, prefix1), (-1, prefix2)]}
        prefixes_to_compute = set()
        for formula in formulas_dict:
            prefix_details_by_formula[formula] = []
            for token in ACCOUNT_CODES_ENGINE_SPLIT_REGEX.split(formula.replace(' ', '')):
                if token:
                    token_match = ACCOUNT_CODES_ENGINE_TERM_REGEX.match(token)

                    if not token_match:
                        raise UserError(_("Invalid token '%(token)s' in account_codes formula '%(formula)s'", token=token, formula=formula))

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
        all_prefixes_queries: list[SQL] = []
        prefilter = self.env['account.account']._check_company_domain(self.get_report_company_ids(options))
        for prefix, excluded_prefixes in prefixes_to_compute:
            account_domain = [
                *prefilter,
            ]

            tag_match = ACCOUNT_CODES_ENGINE_TAG_ID_PREFIX_REGEX.match(prefix)

            if tag_match:
                if tag_match['ref']:
                    tag_id = self.env['ir.model.data']._xmlid_to_res_id(tag_match['ref'])
                else:
                    tag_id = int(tag_match['id'])

                account_domain.append(('tag_ids', 'in', [tag_id]))
            else:
                account_domain.append(('code', '=like', f'{prefix}%'))

            excluded_prefixes_domains = []

            for excluded_prefix in excluded_prefixes:
                excluded_prefixes_domains.append([('code', '=like', f'{excluded_prefix}%')])

            if excluded_prefixes_domains:
                account_domain.append('!')
                account_domain += osv.expression.OR(excluded_prefixes_domains)

            prefix_query = self.env['account.account']._where_calc(account_domain)
            all_prefixes_queries.append(prefix_query.select(
                SQL("%s AS prefix", [prefix, *excluded_prefixes]),
                SQL("account_account.id AS account_id"),
            ))

        # Build a map to associate each account with the prefixes it matches
        accounts_prefix_map = defaultdict(list)
        for prefix, account_id in self.env.execute_query(SQL(' UNION ALL ').join(all_prefixes_queries)):
            accounts_prefix_map[account_id].append(tuple(prefix))

        # Run main query
        query = self._get_report_query(options, date_scope)
        current_groupby_aml_sql = SQL.identifier('account_move_line', current_groupby) if current_groupby else SQL()
        tail_query = self._get_engine_query_tail(offset, limit)
        if current_groupby_aml_sql and tail_query:
            tail_query_additional_groupby_where_sql = SQL(
                """
                AND %(current_groupby_aml_sql)s IN (
                    SELECT DISTINCT %(current_groupby_aml_sql)s
                    FROM account_move_line
                    WHERE %(search_condition)s
                    ORDER BY %(current_groupby_aml_sql)s
                    %(tail_query)s
                )
                """,
                current_groupby_aml_sql=current_groupby_aml_sql,
                search_condition=query.where_clause,
                tail_query=tail_query,
            )
        else:
            tail_query_additional_groupby_where_sql = SQL()

        extra_groupby_sql =  SQL(", %s", current_groupby_aml_sql) if current_groupby_aml_sql else SQL()
        extra_select_sql = SQL(", %s AS grouping_key", current_groupby_aml_sql) if current_groupby_aml_sql else SQL()

        query = SQL(
            """
            SELECT
                account_move_line.account_id AS account_id,
                SUM(%(balance_select)s) AS sum,
                COUNT(account_move_line.id) AS aml_count
                %(extra_select_sql)s
            FROM %(table_references)s
            %(currency_table_join)s
            WHERE %(search_condition)s
            %(tail_query_additional_groupby_where_sql)s
            GROUP BY account_move_line.account_id%(extra_groupby_sql)s
            %(order_by_sql)s
            %(tail_query)s
            """,
            extra_select_sql=extra_select_sql,
            table_references=query.from_clause,
            balance_select=self._currency_table_apply_rate(SQL(f"account_move_line.{selected_balance}")),
            currency_table_join=self._currency_table_aml_join(options),
            search_condition=query.where_clause,
            extra_groupby_sql=extra_groupby_sql,
            tail_query_additional_groupby_where_sql=tail_query_additional_groupby_where_sql,
            order_by_sql=SQL('ORDER BY %s', SQL.identifier('account_move_line', current_groupby)) if current_groupby else SQL(),
            tail_query=tail_query if not tail_query_additional_groupby_where_sql else SQL(),
        )
        self._cr.execute(query)

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
            rslt_groups_by_grouping_keys = {}
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
    
    #Override base method
    def _init_options_currencies(self, options, previous_options=None):
        company_id = self.env.user.company_id
        currency_id = [company_id.currency_id, company_id.sec_currency_id]
        currency_id_list = []
        for currency in currency_id:
            currency_dict = {
                'id':currency.id,
                'name':_(currency.name)
            }
            currency_id_list.append(currency_dict)

        options['currencies'] = currency_id_list
        currency_id = previous_options.get('currencies_selected', None)
        old_currency_id = previous_options.get('currencies_selected_name', None)

        if currency_id:
            options['currencies_selected_name'] = self.env['res.currency'].browse(currency_id).name
        elif old_currency_id:
            options['currencies_selected_name'] = old_currency_id
        else:
            options['currencies_selected_name'] = self.env.company.currency_id.name


    #Override base method
    def _init_options_rounding_unit(self, options, previous_options=None):
        default = 'decimals'

        if previous_options:
            options['rounding_unit'] = previous_options.get('rounding_unit', default)
        else:
            options['rounding_unit'] = default

        currency_id = previous_options.get('currencies_selected', None)
        old_currency_id = previous_options.get('currencies_selected_name', None)

        if currency_id:
            currency_obj = self.env['res.currency'].browse(currency_id)
        elif old_currency_id:
            currency_obj = self.env['res.currency'].search([('name','=',old_currency_id)])
        else:
            currency_obj = self.env.company.currency_id

        options['rounding_unit_names'] = self._get_rounding_unit_names(currency_obj)


    #Override base method
    def _get_rounding_unit_names(self,currency_obj):
        if currency_obj:
            currency_symbol = currency_obj.symbol
        else:
            currency_symbol = self.env.company.currency_id.symbol
        currency_name = self.env.company.currency_id.name
        rounding_unit_names = [
            ('decimals', (f'.{currency_symbol}', '')),
            ('units', (f'{currency_symbol}', '')),
            ('thousands', (f'K{currency_symbol}', _('Amounts in Thousands'))),
            ('millions', (f'M{currency_symbol}', _('Amounts in Millions'))),
        ]

        if currency_name in CURRENCIES_USING_LAKH:
            rounding_unit_names.insert(3, ('lakhs', (f'L{currency_symbol}', _('Amounts in Lakhs'))))

        return dict(rounding_unit_names)
