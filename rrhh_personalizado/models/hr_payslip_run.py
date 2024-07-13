# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime



class PartnerXlsx(models.AbstractModel):
    _inherit = 'report.ips_rei_hr_payslip.xlsx_report'

    """
    25896: El cliente solicita que el salario imponible corresponda al salario total + haberes y salario real el que figura en el contrato
    """

    def get_salario_base(self, payslip_employee):
        # salario_base = int(sum(payslip_employee.line_ids.filtered(lambda line: line.code in ['BASIC']).mapped('total')))
        salario_base = payslip_employee.contract_id.wage
        return salario_base
   
    def get_salario_imponible(self, payslips_employee):
        salario_imponible = 0
        for payslip_employee in payslips_employee:
            monto_ausencia = self.get_monto_ausencia(payslip_employee)
            salario_imponible += self.get_payslip_gross(payslip_employee)
            salario_imponible -= sum(payslip_employee.line_ids.filtered(
                lambda x: x.code in payslip_employee.contract_id.company_id.sueldos_y_jornales_report_codigos_bonificacion_familiar).mapped('total'))
            if payslip_employee.struct_id.type_id.structure_type_tag != 'vacacion':
                salario_imponible -= monto_ausencia
        return salario_imponible

    def get_salario_real(self, payslips_employee):
        salario_real = 0
        for payslip_employee in payslips_employee:
            salario_real += self.get_salario_base(payslip_employee)

        return salario_real
