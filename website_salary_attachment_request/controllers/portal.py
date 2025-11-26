from odoo import http, _, fields
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import format_amount


class SalaryAttachmentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'my_salary_attachments_count' in counters:
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id),
                ('company_id', '=', request.env.user.company_id.id),
            ], limit=1)
            if employee and request.env.user.has_group('base.group_user'):
                attachment_count = request.env['hr.salary.attachment'].sudo().search_count([
                    ('employee_ids', 'in', employee.id),
                ])
            else:
                attachment_count = 0
            values['my_salary_attachments_count'] = attachment_count
        return values

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', request.env.user.id),
            ('company_id', '=', request.env.user.company_id.id),
        ], limit=1)
        values['show_salary_attachment_app'] = bool(employee)
        values['my_salary_attachments_count'] = 0
        if employee:
            attachment_count = request.env['hr.salary.attachment'].sudo().search_count([
                ('employee_ids', 'in', employee.id),
            ])
            values['my_salary_attachments_count'] = attachment_count
        return values

    @http.route(['/my/salary-attachments', '/my/salary-attachments/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_salary_attachments(self, page=1, sortby='date', **kw):
        values = self._prepare_portal_layout_values()
        if not values.get('show_salary_attachment_app'):
            return request.redirect('/my')
        sortby = kw.get('sortby', sortby)
        try:
            page = int(kw.get('page', page))
        except (ValueError, TypeError):
            page = 1

        employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', request.env.user.id),
            ('company_id', '=', request.env.user.company_id.id),
        ], limit=1)
        Attachment = request.env['hr.salary.attachment'].sudo()
        domain = [('employee_ids', 'in', employee.id)]

        sort_options = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Description'), 'order': 'description asc'},
            'state': {'label': _('Status'), 'order': 'state asc'},
        }
        if sortby not in sort_options:
            sortby = 'date'
        order = sort_options[sortby]['order']

        attachment_count = Attachment.search_count(domain)
        pager = portal_pager(
            url='/my/salary-attachments',
            total=attachment_count,
            page=page,
            step=self._items_per_page,
        )
        attachments = Attachment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        lang_code = getattr(request.lang, 'code', None) or request.context.get('lang') or request.env.lang
        state_field = Attachment.with_context(lang=lang_code).fields_get(['state']).get('state', {})
        state_selection = dict(state_field.get('selection', []))

        state_css_map = {
            'to_check': 'text-bg-warning',
            'open': 'text-bg-success',
            'close': 'text-bg-info',
            'cancel': 'text-bg-danger',
        }

        state_order_map = {'open': 0, 'close': 1, 'cancel': 2, 'to_check': 3}

        attachment_lines = []
        for advance in attachments:
            amount = getattr(advance, 'payslip_amount', False) or getattr(advance, 'monthly_amount', 0.0)
            currency = getattr(advance, 'attachment_currency_id', False) or getattr(advance, 'currency_id', False) or advance.company_id.currency_id or request.env.company.currency_id
            amount_display = format_amount(request.env, amount, currency) if currency else f'{amount:.2f}'
            create_dt = advance.create_date and fields.Datetime.context_timestamp(request.env.user, advance.create_date)
            create_display = create_dt.strftime('%Y-%m-%d %H:%M') if create_dt else ''
            start_display = fields.Date.to_string(advance.date_start) if advance.date_start else ''
            date_sort = advance.date_start or (advance.create_date and advance.create_date.date()) or fields.Date.today()
            attachment_lines.append({
                'id': advance.id,
                'description': advance.description or _('Salary advance'),
                'state': advance.state,
                'state_label': state_selection.get(advance.state, advance.state),
                'state_class': state_css_map.get(advance.state, 'text-bg-secondary'),
                'start_display': start_display,
                'create_display': create_display,
                'amount_display': amount_display,
                'currency_id': currency.id if currency else False,
                'state_sort': state_order_map.get(advance.state, 99),
                'date_sort': date_sort,
            })

        attachment_lines.sort(key=lambda line: line['date_sort'], reverse=True)
        attachment_lines.sort(key=lambda line: line['state_sort'])

        values.update({
            'attachments': attachment_lines,
            'page_name': 'salary_attachments',
            'pager': pager,
            'sortby': sortby,
            'sort_options': sort_options,
            'default_url': '/my/salary-attachments',
            'portal_docs_entry_props': {
                'icon': '/sale_subscription/static/src/img/subscription.svg',
                'color_class': 'bg-success-subtle text-success-emphasis',
                'title': _('Salary Attachments'),
                'subtitle': _('Submit and monitor your salary attachment requests'),
                'url': '/my/salary-attachments',
                'count': attachment_count,
            },
            'my_salary_attachments_count': attachment_count,
        })
        return request.render('website_salary_attachment_request.portal_my_salary_attachments', values)

