import json
from odoo import http, Command
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, ValidationError, UserError
import base64


class CertificatePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'certificate_count' in counters:
            certificate_count = request.env['certificate'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
            values['certificate_count'] = certificate_count
        return values

    @http.route(['/my/certificates', '/my/certificates/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_certificates(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Certificate = request.env['certificate']
        
        domain = [('partner_id', '=', request.env.user.partner_id.id)]
        
        # This part is fine
        if date_begin and date_end:
            domain += [('date', '>=', date_begin), ('date', '<=', date_end)]
        elif date_begin:
            domain += [('date', '>=', date_begin)]
        elif date_end:
            domain += [('date', '<=', date_end)]

        certificate_count = Certificate.search_count(domain)
        
        pager = request.website.pager(
            url="/my/certificates",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=certificate_count,
            page=page,
            step=self._items_per_page
        )
        
        certificates = Certificate.search(domain, order='date desc', limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'certificates': certificates,
            'page_name': 'certificate',
            'pager': pager,
            'default_url': '/my/certificates',
        })
        return request.render("completion_certificates.portal_my_certificates", values)

    @http.route(['/my/certificate/<int:certificate_id>'], type='http', auth="user", website=True)
    def portal_certificate_detail(self, certificate_id, **kw):
        try:
            certificate_sudo = request.env['certificate'].sudo().browse(certificate_id)
            if certificate_sudo.partner_id != request.env.user.partner_id:
                raise AccessError("You do not have access to this certificate.")
            
            # Pass the sudo'd record to the template
            values = {
                'certificate': certificate_sudo,
                'page_name': 'certificate_detail',
            }
            return request.render("completion_certificates.portal_certificate_detail", values)
        except (AccessError, UserError):
            return request.redirect('/my')

    @http.route(['/my/certificate/new'], type='http', auth="user", website=True)
    def portal_certificate_new(self, **kw):
        partner_id = request.env.user.partner_id
        
        partner = {
            'id': partner_id.id,
            'name': partner_id.name,
        }

        # Get purchase orders for this partner
        purchase_order_ids = request.env['purchase.order'].search([
            ('partner_id', '=', partner_id.id),
            ('state', 'in', ['purchase', 'done'])
        ])

        purchase_orders = [{
            'id': po.id,
            'name': po.name
        } for po in purchase_order_ids]

        values = {
            'partner': partner,
            'purchase_orders': purchase_orders,
            'page_name': 'certificate_new',
        }
        return request.render("completion_certificates.portal_certificate_form", values)

    @http.route('/my/certificate/create', type='http', auth='public', csrf=True, methods=['POST'], website=True)
    def create_certificate(self, **post):
        try:
            # Get the uploaded file
            file_storage = request.httprequest.files.get('certificate_attachment')
            if file_storage:
                file_content = file_storage.read()
                filename = file_storage.filename

            # Parse certificate lines
            certificate_lines = post.get('certificate_lines')
            if certificate_lines:
                certificate_lines = json.loads(certificate_lines)

            # Create the record
            certificate = request.env['certificate'].sudo().create({
                'name': post.get('name'),
                'partner_id': post.get('partner_id'),
                'date': post.get('date'),
                'purchase_order_id': post.get('purchase_order_id'),
            })

            certificate.write({
                'line_ids': [Command.create({
                    'purchase_line_id': int(line.get('purchase_line_id')), 
                    'description': line.get('description'),
                    'qty_received': line.get('qty_received'),
                    'date_received': line.get('date_received'),
                }) for line in certificate_lines]
            })

            # Attach the file
            if file_storage:
                request.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'datas': base64.b64encode(file_content),
                    'res_model': 'certificate',
                    'res_id': certificate.id,
                    'type': 'binary',
                })

            return request.make_response(json.dumps({'redirect_url': '/my/certificate/%s' % certificate.id}), headers=[('Content-Type', 'application/json')])
        
        except (ValueError, ValidationError, UserError) as e:
            return {'error': str(e)}

    @http.route(['/my/certificate/get_po_products'], type='json', auth="user", methods=['POST'])
    def get_purchase_order_products(self, purchase_order_id, **kw):
        """AJAX endpoint to get products from selected purchase order"""
        try:
            po = request.env['purchase.order'].sudo().browse(int(purchase_order_id))
            if po.partner_id != request.env.user.partner_id:
                return {'error': 'Access denied'}
            
            products = []
            for line in po.order_line:
                products.append({
                    'purchase_line_id': line.id,
                    'id': line.product_id.id,
                    'name': line.product_id.display_name,
                    'description': line.product_id.description or '',
                    'uom': line.product_uom.name,
                    'qty_processed': line.qty_received
                })
            
            return {'products': products}
        except Exception as e:
            return {'error': str(e)}
