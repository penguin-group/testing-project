# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.tools import format_amount
from odoo.http import request

class SalaryAttachmentWebsite(http.Controller):

    @http.route('/salary-attachment/request', type='http', auth='user', website=True)
    def sa_request_page(self, **kw):
        return request.render('website_salary_attachment_request.sa_request_page', {})

    @http.route('/salary-attachment/defaults', type='json', auth='user', website=True, csrf=False)
    def sa_defaults(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id),
            ('company_id', '=', user.company_id.id),
        ], limit=1)

        if not emp:
            return {'ok': False, 'error': _('No employee is linked to the current user.')}

        contract = emp.sudo().contract_id
        if not contract:
            contract = emp.sudo().contract_ids.filtered(lambda c: c.state in ('open', 'pending'))[:1]
        currency = (contract.contract_currency_id if contract and contract.contract_currency_id else False) or \
                   (contract.currency_id if contract and contract.currency_id else False) or \
                   emp.company_id.currency_id or request.env.company.currency_id

        if currency:
            currency_symbol = currency.symbol or currency.name or ''
            currency_code = currency.name or ''
            currency_id = currency.id
        else:
            currency_symbol = ''
            currency_code = ''
            currency_id = False

        employee_name = emp.name or ''
        identification = getattr(emp, 'identification_id', False) or ''

        work_addr = ''
        if getattr(emp, 'address_id', False) and emp.work_contact_id:
            work_addr = emp.address_id.display_name or ''

        max_amount = 0.0
        if contract and contract.wage:
            try:
                max_amount = float(contract.wage or 0.0) * 0.4
            except Exception:
                max_amount = 0.0
        max_amount_display = format_amount(request.env, max_amount, currency) if currency else f'{max_amount:.2f}'

        return {
            'ok': True,
            'employee_id': emp.id,
            'employee_name': employee_name,
            'employee_identification_id': identification,
            'employee_work_address': work_addr,
            'contract_currency_id': currency_id,
            'contract_currency_symbol': currency_symbol,
            'contract_currency_code': currency_code,
            'max_amount': max_amount,
            'max_amount_display': max_amount_display,
            'translations': {
                'load_error': _('Unable to load employee data.'),
                'network_error': _('Network error while loading employee information.'),
                'submitting': _('Submitting...'),
                'submit_success': _('Request submitted. ID: %s'),
                'submit_error': _('The request could not be submitted.'),
                'submit_network_error': _('Network or server error.'),
                'requested_amount_label': _('Requested Amount (%s) *'),
                'amount_helper': _('You can request up to %s.'),
            },
        }

    @http.route('/salary-attachment/submit', type='json', auth='user', website=True, csrf=False)
    def sa_submit(self, **post):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id),
            ('company_id', '=', user.company_id.id),
        ], limit=1)
        if not emp:
            return {'ok': False, 'error': _('No employee is linked to the current user.')}

        try:
            amount = float(post.get('amount', 0))
        except Exception:
            amount = 0.0
        if amount <= 0:
            return {'ok': False, 'error': _('The amount must be greater than zero.')}

        frequency = (post.get('frequency') or '').strip()  # 'one_time' | 'permanent'
        if frequency not in ('one_time', 'permanent'):
            return {'ok': False, 'error': _('Please select a frequency.')}

        today = fields.Date.today()
        description = _('Salary advance request created on %s') % fields.Datetime.now()
        Att = request.env['hr.salary.attachment']
        input_type = request.env.ref(
            'l10n_py_hr_payroll.payslip_input_salary_advance',
            raise_if_not_found=False,
        )
        if not input_type:
            input_type = request.env['hr.payslip.input.type'].sudo().search(
                [('available_in_attachments', '=', True)],
                limit=1,
            )
        if not input_type:
            return {'ok': False, 'error': _('No valid attachment type was found.')}

        existing_attachments = Att.sudo().search([
            ('employee_ids', 'in', emp.id),
            ('other_input_type_id', '=', input_type.id),
            ('state', 'in', ['open', 'to_check']),
        ])
        attachment_to_reuse = False
        for attachment in existing_attachments:
            if attachment.state == 'to_check':
                attachment_to_reuse = attachment
                break
            if attachment.payslip_ids:
                attachment.sudo().action_done()
            else:
                attachment.sudo().action_cancel()
        contract = emp.sudo().contract_id
        if not contract:
            contract = emp.sudo().contract_ids.filtered(lambda c: c.state in ('open', 'pending'))[:1]
        currency = (contract.contract_currency_id if contract and contract.contract_currency_id else False) or \
                   (contract.currency_id if contract and contract.currency_id else False) or \
                   emp.company_id.currency_id or request.env.company.currency_id
        max_amount = 0.0
        if contract and contract.wage:
            try:
                max_amount = float(contract.wage or 0.0) * 0.4
            except Exception:
                max_amount = 0.0
        if max_amount and amount > max_amount + 0.0001:
            return {
                'ok': False,
                'error': _('The requested amount exceeds the allowed maximum (%s).') % (
                    format_amount(request.env, max_amount, currency) if currency else f'{max_amount:.2f}'
                ),
            }

        vals = {}
        if 'employee_ids' in Att._fields:
            vals['employee_ids'] = [(6, 0, [emp.id])]
        if 'description' in Att._fields:
            vals['description'] = description
        if 'monthly_amount' in Att._fields:
            vals['monthly_amount'] = amount
        if 'payslip_amount' in Att._fields:
            vals['payslip_amount'] = amount
        if 'other_input_type_id' in Att._fields:
            vals['other_input_type_id'] = input_type.id
        if currency:
            if 'attachment_currency_id' in Att._fields:
                vals['attachment_currency_id'] = currency.id
            if 'currency_id' in Att._fields:
                vals['currency_id'] = currency.id
        if 'date_start' in Att._fields:
            vals['date_start'] = today
        if 'state' in Att._fields:
            vals['state'] = 'to_check'

        if frequency == 'one_time':
            # ÚNICA VEZ: total_amount = payslip_amount
            if 'total_amount' in Att._fields:
                vals['total_amount'] = amount
            # opcional: si tu flujo requiere end igual a start:
            if 'date_end' in Att._fields:
                vals['date_end'] = today
            # si existe no_end_date, aseguramos False
            if 'no_end_date' in Att._fields:
                vals['no_end_date'] = False
        else:
            # PERMANENTE: sin fecha fin
            if 'no_end_date' in Att._fields:
                vals['no_end_date'] = True
            elif 'date_end' in Att._fields:
                vals['date_end'] = False

        if attachment_to_reuse:
            attachment_to_reuse.sudo().write(vals)
            att = attachment_to_reuse
        else:
            # Crear con sudo pero restringiendo al propio empleado
            att = Att.sudo().create(vals)

        return {'ok': True, 'id': att.id}
