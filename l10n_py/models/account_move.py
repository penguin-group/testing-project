import logging
from odoo import api, fields, models, _
from odoo.tools import index_exists
from odoo.exceptions import ValidationError, UserError
import hashlib
import qrcode
from io import BytesIO
import base64
import re
import math

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'   

    invoice_currency_rate = fields.Float(
        string='Invoice Currency Rate',
        compute='_compute_invoice_currency_rate', store=True, precompute=True,
        copy=False,
        digits=0,
        tracking=True,
        help="Currency rate from company currency to document currency.",
    )
    supplier_invoice_authorization_id = fields.Many2one(
        'invoice.authorization',
        string='Supplier Invoice Authorization',
        domain="[('document_type', 'in', ['in_invoice', 'in_refund'])]"
    )
    supplier_invoice_authorization_start_date = fields.Date(
        related='supplier_invoice_authorization_id.start_date',
        string='Supplier Invoice Authorization Start Date',
        readonly=True,
    )
    supplier_invoice_authorization_end_date = fields.Date(
        related='supplier_invoice_authorization_id.end_date',
        string='Supplier Invoice Authorization End Date',
        readonly=True,
    )
    is_local_supplier = fields.Boolean(string="Local Supplier", related="journal_id.local_suppliers")
    qr_code = fields.Binary(string="QR Code", compute="generate_qr_code")
    delivery_note_number = fields.Char(string="Delivery Note Number")
    related_invoice_number = fields.Char(string="Related Invoice Number")
    foreign_invoice = fields.Boolean(string='Foreign Invoice')
    import_clearance = fields.Boolean(string='Import Clearance', default=False)
    import_invoice_ids = fields.Many2many(
        'account.move', 
        'account_move_import_invoice_ids', 
        'account_move_master', 
        'account_move_helper',
        string='Import Invoices', domain=[
            ('foreign_invoice', '=', True),
            ('state', '=', 'posted'),
            ('move_type', '=', 'in_invoice'),
        ]
    )
    res90_identification_type = fields.Selection([('11', 'RUC'), ('12', 'Identity card'), ('13', 'Passport'), (
        '14', "Foreigner's ID card"), ('15', 'Unnamed'), ('16', 'Diplomatic'), ('17', 'Tax ID')],
                                                 default='11')
    res90_type_receipt = fields.Selection([('101', 'Self-invoicing'),
                                               ('102', 'Public Passenger Transport Ticket'),
                                               ('103', 'Sales Invoice'),
                                               ('104', 'Resimple ticket'),
                                               ('105', 'Lottery Tickets, Games of Chance'),
                                               ('106', 'Ticket or air transportation ticket'),
                                               ('107', 'Import clearance'),
                                               ('108', 'Entrance to public shows'),
                                               ('109', 'Bill'),
                                               ('110', 'Credit note'),
                                               ('111', 'Debit note'),
                                               ('112', 'Cash register machine ticket'),
                                               ('201', 'Proof of expenses for credit purchases'),
                                               ('202', 'Legalized proof of foreign residence'),
                                               ('203', 'Proof of income from credit sales'),
                                               ('204', 'Proof of income from Public, Religious or Public Benefit Entities'),
                                               ('205', 'Account statement - Electronic ticketing'),
                                               ('206', 'Account statement - IPS'),
                                               ('207', 'Account statement - TC/TD'),
                                               ('208', 'Salary Settlement'),
                                               ('209', 'Other expenditure vouchers'),
                                               ('210', 'Other proof of income'),
                                               ('211', 'Bank transfers or money orders / Deposit slip'),
                                               ])
    res90_number_invoice_authorization = fields.Char(string='Invoice Authorization No.')
    res90_imputes_vat = fields.Boolean(string="Impute VAT", default=True)
    res90_imputes_ire = fields.Boolean(string="IRE charges")
    res90_imputes_irp_rsp = fields.Boolean(string="Charges IRP/RSP")
    res90_not_imputes = fields.Boolean(string="Does not impute", default=False)
    res90_associated_voucher_number = fields.Char(string="Associated voucher number")
    res90_associated_receipt_stamping = fields.Char(string="Associated receipt stamp number")
    exclude_res90 = fields.Boolean(string="Exclude from Resolution 90",
                                   help="The records of this journal will not be included in resolution 90")
    journal_entry_number = fields.Integer(string='Journal Entry Number', index=True)

    # === Fields por PY Reports === #
    amount_exempt = fields.Monetary(
        string='Exempt amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_base10 = fields.Monetary(
        string='Base VAT 10% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_vat10 = fields.Monetary(
        string='VAT 10% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_base5 = fields.Monetary(
        string='Base VAT 5% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_vat5 = fields.Monetary(
        string='VAT 5% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_taxable_imports = fields.Monetary(
        string='Taxable imports amount',
        compute='_compute_fields_for_py_reports',
    )

    @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_date')
        # Override to include buying/selling rates
    def _compute_invoice_currency_rate(self):
        buy = ['out_invoice',
               'out_refund',
               'out_receipt',
               ]
        sell = ['entry',
               'in_invoice',
               'in_refund',
               'in_receipt',
               ]
        for move in self:
            rate_type = 'buy' if move.move_type in buy else 'sell'
            if move.is_invoice(include_receipts=True):
                if move.currency_id:
                    conversion_method = self.env['res.currency']._get_conversion_rate
                    move.invoice_currency_rate = conversion_method(
                        from_currency=move.company_currency_id,
                        to_currency=move.currency_id,
                        company=move.company_id,
                        date=move.invoice_date or fields.Date.context_today(move),
                        rate_type=rate_type,
                    )
                else:
                    move.invoice_currency_rate = 1

    def _compute_fields_for_py_reports(self):
        for record in self:
            if record.move_type == "in_invoice" and record.import_clearance:
                # Handle import clearance invoices
                record.amount_vat10 = sum(record.line_ids.filtered(lambda l: l.display_type =='product' and l.account_id.vat_import and 0 in l.tax_ids.mapped('amount')).mapped("balance"))
                record.amount_base10 = record.amount_vat10 * 10
                record.amount_base5 = 0
                record.amount_vat5 = 0
                record.amount_exempt = 0
                record.amount_taxable_imports = record.amount_base10
            else:
                record.amount_base10 = sum(record.line_ids.filtered(lambda l: l.display_type =='product' and 10 in l.tax_ids.mapped('amount')).mapped("balance"))
                record.amount_vat10 = sum(record.line_ids.filtered(lambda l: l.display_type =='tax' and l.tax_line_id and l.tax_line_id.amount == 10).mapped("balance"))
                record.amount_base5 = sum(record.line_ids.filtered(lambda l: l.display_type =='product' and 5 in l.tax_ids.mapped('amount')).mapped("balance"))
                record.amount_vat5 = sum(record.line_ids.filtered(lambda l: l.display_type =='tax' and l.tax_line_id and l.tax_line_id.amount == 5).mapped("balance"))
                record.amount_exempt = sum(record.line_ids.filtered(lambda l: l.display_type =='product' and 0 in l.tax_ids.mapped('amount')).mapped("balance"))
                record.amount_taxable_imports = 0 

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self._get_supplier_invoice_authorization()
        return super()._onchange_partner_id()

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        self._get_supplier_invoice_authorization()

    def _get_supplier_invoice_authorization(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund'] and record.is_local_supplier and record.invoice_date:
                record.supplier_invoice_authorization_id =  self.env['invoice.authorization'].search([
                                                                ('document_type', 'in', ['in_invoice', 'in_refund']), 
                                                                ('partner_id', '=', record.partner_id.id),
                                                                ('active', '=', True),
                                                                ('end_date', '>=', record.invoice_date)
                                                            ], order="end_date", limit=1)
            else:
                record.supplier_invoice_authorization_id = False
    
    def edit_currency_rate(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'invoice.edit.currency.rate',
                'view_mode': 'form',         
                'view_id': self.env.ref('l10n_py.invoice_edit_currency_rate_view_form').id,      
                'target': 'new',
                'context': {'active_id': self.id}
            }

    def button_cancel_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.cancel',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_py.invoice_cancel_form').id,
            'target': 'new',
            'context': {'active_id': self.id}
        }

    def cancel_invoice(self):
        for invoice in self.filtered(lambda i: i.move_type in ['out_invoice', 'out_refund']):
            invoice.validate_invoice_authorization()
            if invoice.state != 'draft':
                invoice.button_draft()
            invoice.button_cancel()
    
    def validate_invoice_authorization(self):
        if self.move_type in ['out_invoice', 'out_refund'] and self.name and self.name != '/':
            inv_auth = self.journal_id.invoice_authorization_id
            if inv_auth:
                number = int(self.name.split('-')[-1])
                establishment_number = self.name.split('-')[0]
                expedition_point_number = self.name.split('-')[1]
                if expedition_point_number != inv_auth.expedition_point_number:
                    raise ValidationError(
                        _('The expedition point number does not match the active invoice authorization.')
                    )
                if establishment_number != inv_auth.establishment_number:
                    raise ValidationError(
                        _('The establishment number does not match the active invoice authorization.')
                    )
                if number > inv_auth.final_invoice_number:
                    raise ValidationError(
                        _('The active invoice authorization has reached its invoice final number.')
                    )
                date = self.invoice_date or fields.Date.today()
                if date > inv_auth.end_date:
                    raise ValidationError(
                        _('The invoice date cannot be later than the invoice authorization’s end date.')
                    )
                if date < inv_auth.start_date:
                    raise ValidationError(
                        _('The invoice date cannot be earlier than the invoice authorization’s start date.')
                    )
                return
            else:
                raise ValidationError(
                    _('There is no invoice authorization.')
                )
        else:
            return

    def validate_empty_vat(self):
        for record in self:
            if not record.partner_id.vat:
                raise ValidationError(_("The customer does not have an assigned VAT. Please add it."))
        return

    @api.onchange('invoice_line_ids')
    @api.depends('invoice_line_ids', 'journal_id')
    def validate_line_count(self):
        for record in self:
            if record.journal_id.max_lines != 0:
                if len(record.invoice_line_ids) > record.journal_id.max_lines:
                    raise ValidationError(
                        _("The maximum number of lines supported in the invoice has been reached."))
        return

    def validate_supplier_invoice_number(self):
        if self.ref and self.is_local_supplier:
            pattern = re.compile(r'^(\d{3}-){2}\d{7}$')
            if not pattern.match(self.ref):
                raise ValidationError(
                    _('The invoice number does not have the correct format (xxx-xxx-xxxxxxx)')
                )

    def generate_token(self):
        secret_phrase = str(self.id) + "amakakeruriunohirameki"
        return hashlib.sha256(secret_phrase.encode('utf-8')).hexdigest()
    
    def generate_qr_code(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            route = f"/invoice/check?invoice_id={record.id}&token={record.generate_token()}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"{base_url}{route}")
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            record.qr_code = qr_image

    def format_self_printer_line(self, line=False):
        """Format the line for self-printer to fit a character limit."""
        limit = 50
        if not line:
            return False
        else:
            limited_lines = []
            current_line = ''
            count = 0
            for char in line:
                count += 1
                current_line += char
                if count == limit:
                    limited_lines.append(current_line)
                    current_line = ''
                    count = 0
            if current_line:
                limited_lines.append(current_line)
            return limited_lines

    def format_amount(self, amount, currency=False, lang=False):
        if not amount:
            amount = 0
        if not lang:
            lang_str = self._context.get('lang')
        else:
            lang_str = lang
        if not currency:
            currency_id = self.env.company.currency_id
        else:
            currency_id = currency

        lang_id = self.env['res.lang'].search([('code', '=', lang_str)], limit=1)

        if lang_id and currency_id:
            fmt = f"%.{currency_id.decimal_places}f"
            return lang_id.format(fmt, amount, grouping=True)
        else:
            return f'{amount:.6f}'

    def amount_to_text(self, amount, currency):
        words = currency.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount).upper()
        return words

    def action_post(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund']:
                record.validate_supplier_invoice_number()
        result = super(AccountMove, self).action_post()
        for record in self:
            if record.move_type in ['out_invoice', 'out_refund']:
                record.validate_empty_vat()
                record.validate_invoice_authorization()
                record.validate_line_count()
            if record.move_type in ['out_invoice', 'out_refund']:
                record.write({'res90_number_invoice_authorization': record.journal_id.invoice_authorization_id.name})
            elif record.move_type in ['in_invoice', 'in_refund']:
                supplier_invoice_authorization = False
                if record.supplier_invoice_authorization_id:
                    supplier_invoice_authorization = record.supplier_invoice_authorization_id.name
                record.write({'res90_number_invoice_authorization': supplier_invoice_authorization or ''})
        return result


    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can more easily see the next step of the workflow. """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices can be printed"))
        self.filtered(lambda inv: not inv.action_invoice_sent).write({'mark_invoice_as_sent': True})
        return self.env.ref('l10n_py.invoice_report_action').report_action(self)

    
    @api.onchange('journal_id')
    @api.depends('journal_id')
    def onchangeCompany(self):
        for i in self:
            if i.journal_id.res90_imputes_irp_rsp_default:
                i.res90_imputes_irp_rsp = True

    @api.onchange('journal_id')
    @api.depends('journal_id')
    def assign_voucher_type(self):
        for i in self:
            if i.journal_id:
                if i.journal_id.res90_type_receipt:
                    i.res90_type_receipt = i.journal_id.res90_type_receipt
                elif i.move_type in ['out_invoice', 'in_invoice']:
                    i.res90_type_receipt = '109'
                elif i.move_type in ['out_refund', 'in_refund']:
                    i.res90_type_receipt = '110'
                else:
                    i.res90_type_receipt = None

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def assign_id_type(self):
        for i in self:
            if i.partner_id:
                if not i.partner_id.vat:
                    i.res90_identification_type = '15'
                else:
                    pattern = "^[0-9]+-[0-9]$"
                    if re.match(pattern, i.partner_id.vat) and i.partner_id.vat != '44444401-7':
                        i.res90_identification_type = '11'
                    elif re.match(pattern, i.partner_id.vat) and i.partner_id.vat == '44444401-7':
                        i.res90_identification_type = '15'
                    else:
                        pattern = "^[0-9]+$"
                        if re.match(pattern, self.partner_id.vat):
                            i.res90_identification_type = '12'
                        else:
                            i.res90_identification_type = '15'

    def get_id_type(self):
        result = 15
        if self.res90_identification_type:
            return int(self.res90_identification_type)
        if self.import_clearance:
            result = 17
        return result

    def get_identification(self):
        id = self.partner_id.vat
        if id and len(id.split('-')) > 1:
            id = id.split('-')[0]
        if self.import_clearance:
            id = self.import_invoice_ids.mapped('partner_id').vat
            if id and len(id.split('-')) > 1:
                id = id.split('-')[0]
        return id or '44444401'

    def get_name_partner(self):
        result = self.partner_id.name
        if self.import_clearance:
            result = self.import_invoice_ids.mapped('partner_id').name
        return result

    def get_receipt_type(self):
        if self.res90_type_receipt:
            return int(self.res90_type_receipt)
        elif self.move_type in ['in_invoice', 'out_invoice']:
            return 109
        elif self.move_type in ['in_refund', 'out_refund']:
            return 110
        else:
            return ''

    def get_receipt_date(self):
        return self.date.strftime('%d/%m/%Y')

    def get_stamped(self):
        result = 0
        if not self.import_clearance:
            if self.res90_number_invoice_authorization:
                try:
                    result = int(self.res90_number_invoice_authorization)
                except:
                    raise ValidationError(
                        "The value " + self.res90_number_invoice_authorization + " in the field of No. Stamped seat " + self.name + " cannot be processed, please check if it is correct")
        return result

    def get_receipt_number(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            return self.name
        elif self.move_type in ['in_invoice', 'in_refund']:
            return self.ref
        else:
            return ''

    def get_amount10(self):
        amount10 = self.amount_base10 + self.amount_vat10
        if self.import_clearance:
            amount10 = 11 * self.amount_vat10
        return round(amount10)

    def get_amount5(self):
        amount5 = self.amount_base5 + self.amount_vat5
        return round(amount5)

    def get_exempt_amount(self):
        amount0 = self.amount_exempt
        if self.import_clearance:
            amount0 = 0
        return round(amount0)

    def get_total_amount(self):       
        amount = abs(self.amount_total_signed)
        if self.import_clearance:
            amount = self.get_amount10()
        return round(amount)

    def get_sale_condition(self):
        if self.invoice_date_due > self.invoice_date:
            return 2
        return 1

    def get_foreign_currency_operation(self):
        if self.import_clearance:
            return 'S'
        if self.currency_id and self.currency_id.name == 'PYG':
            return 'N'
        elif self.currency_id and self.currency_id.name != 'PYG':
            return 'S'
        else:
            return 'N'

    def get_imput_vat(self):
        if self.get_imput_vat:
            return 'S'
        return 'N'

    def get_imput_ire(self):
        if self.res90_imputes_ire:
            return 'S'
        return 'N'

    def get_impute_irp_rsp(self):
        if self.res90_imputes_irp_rsp:
            return 'S'
        return 'N'

    def get_no_impute(self):
        if self.res90_not_imputes:
            return 'S'
        return 'N'

    def get_associated_voucher_number(self):
        if self.res90_associated_voucher_number:
            return self.res90_associated_voucher_number
        return ''

    def get_associated_receipt_stamping(self):
        if self.res90_associated_receipt_stamping:
            return self.res90_associated_receipt_stamping
        return ''

    # Function executed by a scheduled action to fill rg90 fields
    @api.model
    def rg90_remission_fields(self):
        credit_note_customers = self.env['account.move'].search(
            [('move_type', '=', 'out_refund'), ('reversed_entry_id', '!=', False)])
        for cn in credit_note_customers:
            authorization = ''
            if cn.reversed_entry_id.journal_id and cn.reversed_entry_id.journal_id.invoice_authorization_id:
                authorization = cn.reversed_entry_id.journal_id.invoice_authorization_id.name
            if not cn.reversed_entry_id.res90_associated_voucher_number or not cn.reversed_entry_id.res90_associated_receipt_stamping:
                cn.reversed_entry_id.sudo().write({
                    'res90_associated_voucher_number': cn.name,
                    'res90_associated_receipt_stamping': authorization
                })
            authorization = ''
            if cn.journal_id and cn.journal_id.invoice_authorization_id:
                authorization = cn.journal_id.invoice_authorization_id.name

            if not cn.res90_associated_voucher_number or not cn.res90_associated_receipt_stamping:
                cn.sudo().write({
                    'res90_associated_voucher_number': cn.reversed_entry_id.name or '',
                    'res90_associated_receipt_stamping': authorization
                })

        credit_note_suppliers = self.env['account.move'].search(
            [('move_type', '=', 'in_refund'), ('reversed_entry_id', '!=', False)])
        for cn in credit_note_suppliers:
            authorization = ''
            if cn.reversed_entry_id.supplier_invoice_authorization_id:
                authorization = cn.reversed_entry_id.supplier_invoice_authorization_id.name

            if not cn.reversed_entry_id.res90_associated_voucher_number or not cn.reversed_entry_id.res90_associated_receipt_stamping:
                cn.reversed_entry_id.sudo().write({
                    'res90_associated_voucher_number': cn.name,
                    'res90_associated_receipt_stamping': authorization
                })
            authorization = ''
            if cn.supplier_invoice_authorization_id:
                authorization = cn.supplier_invoice_authorization_id.name

            if not cn.res90_associated_voucher_number or not cn.res90_associated_receipt_stamping:
                cn.sudo().write({
                    'res90_associated_voucher_number': cn.reversed_entry_id.name,
                    'res90_associated_receipt_stamping': authorization
                })

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if any(self.mapped('foreign_invoice')) and self.mapped('invoice_line_ids.tax_ids') and any(self.mapped('invoice_line_ids.tax_ids.amount')):
            raise ValidationError('A Foreign Invoice (Import) should only have Exempts as taxes')
        return res

    def set_journal_entry_numbers(self):
        for company in self.env['res.company'].sudo().search([]):
            self.env.cr.execute("SELECT id FROM account_move WHERE company_id=%s AND state='posted' ORDER BY date,name,id" % company.id)
            account_move_ids = [x[0] for x in self.env.cr.fetchall()]
            sql_querys = ''
            journal_entry_number = 1
            for account_move_id in account_move_ids:
                sql_querys += 'UPDATE account_move SET journal_entry_number=%s WHERE id=%s AND (journal_entry_number!=%s OR journal_entry_number IS NULL);' % (
                    journal_entry_number, account_move_id, journal_entry_number
                )
                journal_entry_number += 1
            if sql_querys:
                self.env.cr.execute(sql_querys)
            else:
                _logger.info(f"Te company {company.name} has no journal entries. Skipped.")

    def action_print(self):
        for record in self:
            if not record.move_type in ['out_invoice', 'out_refund']:
                raise ValidationError(_("Only customer invoices can be printed"))
        return super(AccountMove, self).action_print()


