from odoo import api, models, fields, _
from odoo.tools.misc import xlsxwriter
import io
import base64

from odoo.exceptions import UserError


class HrPayrollPaymentReportWizard(models.TransientModel):
    _inherit = 'hr.payroll.payment.report.wizard'

    export_format = fields.Selection(selection_add=[('xlsx', 'Excel')], ondelete={'xlsx': 'set default'})

    def generate_payment_report(self):
        super().generate_payment_report()

        salary_payment_bank = self.env['ir.config_parameter'].get_param("res_config_settings.salary_payment_bank")

        if self.export_format == 'xlsx' and salary_payment_bank == 'interfisa':
            output = io.BytesIO()

            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Payslip Batch')
            header_format = workbook.add_format({'bold': True, 'align': 'center'})
            align_left_format = workbook.add_format({'align': 'left'})
            align_right_format = workbook.add_format({'align': 'right'})
            headers = [('Nro. Documento'), ('Nombre y Apellido'), ('Monto del pago'), ('Cuenta credito')]

            worksheet.write_row(0, 0, headers, header_format)
            worksheet.set_column(0, 0, 20)  # Nro. Documento
            worksheet.set_column(1, 1, 50)  # Nombre y Apellido
            worksheet.set_column(2, 2, 20)  # Monto del pago
            worksheet.set_column(3, 3, 20)  # Cuenta credito

            index = 1
            for slip in self.payslip_ids:
                employee_document_id = slip.employee_id.identification_id
                employee_name = slip.employee_id.name
                amount_to_be_paid = slip.net_wage
                employee_bank_account = slip.employee_id.bank_account_id.acc_number

                if not all([employee_document_id, employee_name, amount_to_be_paid, employee_bank_account]):
                    raise UserError(_(f"The employee {employee_name} may not have all the necessary fields filled.\nPlease, verify the following information: employee's name, identification number, bank account details, and the payslip amount."))

                worksheet.write(index, 0, employee_document_id, align_left_format)
                worksheet.write(index, 1, employee_name, align_left_format)
                worksheet.write(index, 2, amount_to_be_paid, align_right_format)
                worksheet.write(index, 3, employee_bank_account, align_right_format)
                index += 1

            workbook.close()
            xlsx_data = output.getvalue()
            payment_report = base64.encodebytes(xlsx_data)
            self._write_file(payment_report, '.xlsx')
