import logging
from odoo import models, fields, api
from itertools import islice


_logger = logging.getLogger(__name__)


def grouper(iterable, n):
    """
    Collect data into fixed-length chunks or blocks
    """
    it = iter(iterable)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            return
        yield chunk


class AccountMove(models.Model):
    _inherit = 'account.move'

    def migrate_timbrado(self, company):
        _logger.info("DATOS DE TIMBRADOS...")
        
        try:
            timbrado_fields = [
                    ("name", "name"),
                    ("tipo_documento", "document_type"),
                    ("inicio_vigencia", "start_date"),
                    ("fin_vigencia", "end_date"),
                    ("nro_establecimiento", "establishment_number"),
                    ("nro_punto_expedicion", "expedition_point_number"),
                    ("rango_inicial", "initial_invoice_number"),
                    ("rango_final", "final_invoice_number"),
                    ("active", "active"),
                    ("nro_autorizacion", "self_printer_authorization"),
                ]
                
            timbrados = self.env['interfaces_timbrado.timbrado'].sudo().search([('company_id', '=', company.id)])
            for timbrado in timbrados:
                inv_auth = self.env['invoice.authorization'].sudo().search([('name', '=', timbrado.name)])
                if not inv_auth:
                    d = {}
                    for f in timbrado_fields:
                        d.update({f[1]: timbrado[f[0]]})
                    d.update({'company_id': company.id})
                    inv_auth = self.env['invoice.authorization'].sudo().create(d)
                    _logger.info(f"Creado invoice.authorization {inv_auth.id}/{inv_auth.name}")
                else:
                    _logger.info(f"Ya existía invoice.authorization {inv_auth.id}/{inv_auth.name}")
                
                timbrado.journal_id.sudo().write({'invoice_authorization_id': inv_auth.id})
                _logger.info(f"Relacionado con el Diario {timbrado.journal_id.name}")

            return True
        
        except Exception as e:
            _logger.error(str(e))
            return False

    def migrate_timbrado_proveedores(self):
        _logger.info("Timbrados de proveedores...")
        
        try:
            supplier_timbrado_fields = [
                ("name", "name"),
                ("inicio_vigencia", "start_date"),
                ("fin_vigencia", "end_date"),
            ]
            timbrados = self.env['proveedores_timbrado.timbrado'].sudo().search([])
            cnt = 0
            for timbrado in timbrados:
                cnt += 1
                _logger.info(f"{int(cnt/len(timbrados)*100)}%. Timbrado de proveedor {timbrado.name} {cnt}/{len(timbrados)}")
                if timbrado.name and len(timbrado.name) == 8: # only set relation to inv auth with the correct format
                    inv_auth = self.env['invoice.authorization'].sudo().search([('name', '=', timbrado.name)])
                    if not inv_auth:
                        d = {}
                        for f in supplier_timbrado_fields:
                            d.update({f[1]: timbrado[f[0]]})
                        d.update({'company_id': False, 'document_type': 'in_invoice', 'partner_id': timbrado.partner_id.id})
                        inv_auth = self.env['invoice.authorization'].create(d)
                        _logger.info(f"Creado invoice.authorization de proveedor {timbrado.partner_id.name} {inv_auth.id}/{inv_auth.name}")
                        # Set related field in account.move records
                        all_company_ids = self.env['res.company'].search([]).ids
                        invoices = self.env['account.move'].with_context(allowed_company_ids=all_company_ids).search([('timbrado_id', '=', timbrado.id), ('move_type', 'in', ['in_invoice', 'in_refund']), ('es_factura_exterior', '=', False)])
                        invoices.sudo().write({'supplier_invoice_authorization_id': inv_auth.id})
                        _logger.info(f"Relacionado con las facturas {', '.join(invoices.mapped(lambda r: r.ref or r.name or str(r.id)))}")
                        self.env.cr.commit()
                    else:
                        _logger.info(f"invoice.authorization {inv_auth.name} existente.")
                else:
                    _logger.info("El timbrado no tiene el formato correcto. No se pudo registrar.")
            return True
        except Exception as e:
            _logger.error(str(e))
            return False

    def migrate_autoimpresor(self, company):
        _logger.info("Autoimpresor...")
        try:
            for journal in self.env['account.journal'].sudo().search([('company_id', '=', company.id), ('type', '=', 'sale')]):
                journal.sudo().write({
                    'payment_info': company.datos_banco,
                    'invoice_footer': journal.pie_factura,
                    'show_qr': journal.mostrar_qr,
                    'max_lines': journal.max_lineas, 
                    })
                _logger.info(f"Actualizado el diario {journal.name}.")
            account_moves = self.env['account.move'].sudo().search([]).filtered(lambda x: (x.nro_nota_remision or x.nro_factura_relacionada) and x.company_id.id == company.id)
            for move in account_moves:
                _logger.info(f"Actualizando datos de documentos relacionados en {move.name}")
                move.sudo().write({
                    'delivery_note_number': move.nro_nota_remision,
                    'related_invoice_number': move.nro_factura_relacionada
                })
            return True
        except Exception as e:
            _logger.error(str(e))
            return False

    def migrate_rg90(self, company):
        _logger.info("RG90...")
        try:
            for journal in self.env['account.journal'].sudo().search([('company_id', '=', company.id)]):
                journal.sudo().write({
                    'exclude_res90': journal.excluir_res90,
                    'res90_imputes_irp_rsp_default': company.res90_imputa_irp_rsp_defecto, 
                    })
                _logger.info(f"Diario {journal.name}.")
            
            cnt = 0
            account_moves = self.env['account.move'].sudo().search([]).filtered(lambda x: (x.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']) and x.company_id.id == company.id)
            # Process account_moves in groups of 50
            for group in grouper(account_moves, 50):
                for move in group:
                    cnt += 1
                    _logger.info(f"{int(cnt/len(account_moves)*100)}%. Datos de RG90 {move.name or str(move.id)} {cnt}/{len(account_moves)}")
                    move.sudo().write({
                        'res90_number_invoice_authorization': move.res90_nro_timbrado,
                        'res90_type_receipt': move.res90_tipo_comprobante,
                        'res90_identification_type': move.res90_tipo_identificacion,
                        'res90_imputes_vat': move.res90_imputa_iva,
                        'res90_imputes_ire': move.res90_imputa_ire,
                        'res90_imputes_irp_rsp': move.res90_imputa_irp_rsp,
                        'res90_not_imputes': move.res90_no_imputa,
                        'res90_associated_voucher_number': move.res90_nro_comprobante_asociado,
                        'res90_associated_receipt_stamping': move.res90_timbrado_comprobante_asociado,
                        'exclude_res90': move.excluir_res90,
                    })
                self.env.cr.commit()
            return True
        except Exception as e:
            _logger.error(str(e))
            return False
    
    def migrate_data(self):
        result = []
        result.append(self.migrate_timbrado_proveedores())
        for company in self.env['res.company'].sudo().search([]):
            _logger.info(f"MIGRANDO DATOS DE LA COMPAÑÍA {company.name}")
            result.append(self.migrate_timbrado(company))
            result.append(self.migrate_autoimpresor(company))
            result.append(self.migrate_rg90(company))

        if all(result):
            _logger.info("El proceso de migración se completó exitosamente.")
        else:
            _logger.error("Hubo errores en el proceso. Revisar el Log.")
        


