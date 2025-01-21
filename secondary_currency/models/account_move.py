from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import format_amount, SQL

class AccountMove(models.Model):
    _inherit = 'account.move'

    company_secondary_currency_id = fields.Many2one(
        string='Company Secondary Currency',
        related='company_id.sec_currency_id', readonly=True,
    )
    invoice_secondary_currency_rate = fields.Float(
        string='Invoice Secondary Currency Rate',
        compute='_compute_invoice_secondary_currency_rate', store=True, precompute=True,
        copy=False,
        digits=0,
        tracking=True,
        help="Currency rate from company secondary currency to document currency.",
    )

    @api.depends('currency_id', 'company_secondary_currency_id', 'company_id', 'invoice_date', 'date')
    def _compute_invoice_secondary_currency_rate(self):
        for move in self:
            if move.company_currency_id != move.company_secondary_currency_id:
                move.invoice_secondary_currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=move.company_secondary_currency_id,
                    to_currency=move.company_currency_id,
                    company=move.company_id,
                    date=move.invoice_date or fields.Date.context_today(move),
                )
            else:
                move.invoice_secondary_currency_rate = 1

    def _post(self, soft=True):
        ''' Override to check the secondary balance before posting the move.
        '''
        self.line_ids._compute_secondary_balance()
        self._check_secondary_balanced()
        return super(AccountMove, self)._post(soft)
    
    def _check_secondary_balanced(self):
        ''' Assert the move is fully balanced on secondary balance.
        An error is raised if it's not the case.
        '''
        unbalanced_moves = self._get_secondary_unbalanced_moves()
        if unbalanced_moves:
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                error_msg += _(
                    "\n\n"
                    "Secondary Balance in the move (%(move)s) is not balanced.\n"
                    "The total of debits equals %(debit_total)s and the total of credits equals %(credit_total)s.\n"
                    "The difference could be due to a rounding error in the secondary currency.\n"
                    "Please adjust it manually.\n",
                    move=move.display_name,
                    debit_total=format_amount(self.env, sum_debit, move.company_id.sec_currency_id),
                    credit_total=format_amount(self.env, sum_credit, move.company_id.sec_currency_id),
                    journal=move.journal_id.name)
            raise UserError(error_msg)

    def _get_secondary_unbalanced_moves(self):
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        self.env['account.move.line'].flush_model(['secondary_balance', 'currency_id', 'move_id'])
        return self.env.execute_query(SQL('''
            SELECT line.move_id,
                   ROUND(SUM(CASE WHEN line.debit > 0 THEN line.secondary_balance ELSE 0 END), currency.decimal_places) debit,
                   ROUND(SUM(CASE WHEN line.credit > 0 THEN line.secondary_balance ELSE 0 END), currency.decimal_places) credit
              FROM account_move_line line
              JOIN account_move move ON move.id = line.move_id
              JOIN res_company company ON company.id = move.company_id
              JOIN res_currency currency ON currency.id = company.sec_currency_id
             WHERE line.move_id IN %s
          GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.secondary_balance), currency.decimal_places) != 0
        ''', tuple(moves.ids)))
