from odoo import http
from odoo.http import request

class Sites(http.Controller):
    @http.route('/sites', type='http', auth='user', website=True)
    def index(self):
        sites = request.env['pisa.site'].search([])
        return request.render('pisa_sites.site_list', {
            'sites': sites,
        }) 