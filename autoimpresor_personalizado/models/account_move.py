from locale import currency
from odoo import models, api, fields, exceptions,_
from odoo.exceptions import UserError,ValidationError
import qrcode
import base64,hashlib
from io import BytesIO
import logging
_logger = logging.getLogger(__name__)
import re


class AccountMove(models.Model):
    _inherit = 'account.move'

    qr_codigo_bancos = fields.Binary(string="QR Code", compute="generate_qr_codigo_bancos")
    # company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    # partner_id = fields.Many2one('res.partner', required=True)
    # ref = fields.Char(required=True)
    # invoice_date = fields.Date(required=True)

    def action_post(self):
        for record in self:
            if record.move_type in ['in_invoice']:
                # Verificamos si el campo "ref" está en blanco
                if not record.ref:
                    raise exceptions.ValidationError('El campo "Numero de Factura" es requerido.')

                # Verificamos si el total de la factura es menor o igual a cero
                if record.amount_total <= 0:
                    raise exceptions.ValidationError('El total de la factura no puede ser cero.')
        return super(AccountMove, self).action_post()      

    #se sobrescribe validacion de campo de numero de factura
    #solo controlara cuando el campo diario sea de proveedores nacionales de tipo 2 
    #con otros tipos no tomara en cuenta el formato del numero de factura
    def check_timbrado_nro_factura(self):
        for this in self:
            if this.timbrado_proveedor != this.timbrado_id.name: this.timbrado_proveedor = this.timbrado_id.name
            if this.move_type in ['in_invoice'] and this.timbrado_proveedor and this.ref:
                if this.journal_id.id == 2:
                    patron = re.compile(r'^(\d{3}-){2}\d{7}$')
                    if not patron.match(this.ref):
                        raise exceptions.ValidationError('El nro de factura no tiene el formato adecuado (xxx-xxx-xxxxxxx)')
        


    def generate_qr_codigo_bancos(self):
        # datos_bancos = """
        #     Bank Name: Banco Continental S.A.\n
        #     Bank Address: Avda. Mcal López N°3233 - Asunción - Paraguay\n
        #     Swift Code: BCNAPYPAXXX\n
        #     Company: Penguin Infraestructure S.A.\n
        #     Beneficiary Account: 12632518705\n
        #     Currency: USD\n
        #     Address: 1461, Gumersindo Sosa, Asunción, PY\n
        #     ----------------------------------------------\n
        #     Bank Name: Arival Bank Corp.\n
        #     Bank Address: 1250 Ponce de León Ave. Suite 1005, San Juan, PR 00907\n
        #     Company: Penguin Infraestructure S.A.\n
        #     Beneficiary Account: 120110063231\n
        #     Currency: USD\n
        #     Address: 1461, Gumersindo Sosa, Asunción, Asunción, Asunción, PY\n
        #     ---------------------------------------------\n
        #     Bank Name: Capital Union Bank\n
        #     Bank Address: Club Financial Center, Lyford Cay - PO Box AP59223 - Nassau, Bahamas\n
        #     Company: Penguin Infraestructure Sociedad Anonima\n
        #     Beneficiary Account: 6550597 2001\n
        #     Currency: USD\n
        #     Address: 1461, Gumersindo Sosa, Asunción, Asunción, Asunción, PY\n    

                
        #     """
        html_content = """
                    {{ datos_banco }}
                """
        html_content = re.sub(r'{{ datos_banco }}', str(self.company_id.datos_banco).replace('<br>', '\n'), html_content)
        # Define una regex pattern para coincidir con las etiquetas HTML
        html_tags_pattern = re.compile(r'<.*?>')
        plain_text = re.sub(html_tags_pattern, '', html_content)

        # print(plain_text)
        # print(type(self.company_id.datos_banco))
        for i in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # data_to_encode = f"{self.company_id.datos_banco}"

            qr.add_data(plain_text)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            i.qr_codigo_bancos = qr_image