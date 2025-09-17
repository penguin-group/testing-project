from odoo import _


class SummaryReportData:
    """
    Aggregates salaries for a given period.
    """

    def __init__(self, env, start_date, end_date):
        self.env = env
        self.year = start_date.year
        self.summary = self._load_summary()

    def _load_summary(self):
        employes_report = self.env['hr.reports.mtess'].search([
            ('report_type', '=', 'employees'),
            ('year', '=', self.year),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        salaries_report = self.env['hr.reports.mtess'].search([
            ('report_type', '=', 'salaries'),
            ('year', '=', self.year),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        employees_data = employes_report.data if employes_report else {}
        salaries_data = salaries_report.data if salaries_report else {}
        if not employees_data or not salaries_data:
            raise ValueError(_("Both employee and salary reports must be generated for the selected year and company."))
        data = self.build_summary(employees_data, salaries_data)
        return data


    def build_summary(self, employees, salaries):
        # row_config structure:
        # description, data_type, to_count, incremental_field, is_date
        row_config = [
            ('CANTIDAD O NÚMERO DE TRABAJADORES', 'employess', True, None, False),
            ('TOTAL DE HORAS INCLUYENDO HORAS EXTRAS', 'salaries', False, 'total_h', False),
            ('TOTAL DE SALARIO INCLUYENDO LOS BENEFICIOS', 'salaries', False, 'total_s', False),
            ('CANTIDAD DE ENTRADAS O INGRESOS DE PERSONAL', 'employees', True, 'fechaentrada', True),
            ('CANTIDAD DE SALIDAS O EGRESOS DE PERSONAL', 'employees', True, 'fecha_salida', True)
        ]
        summary = []
        patronal_number = employees[0]["Nropatronal"] if employees else salaries[0]["Nropatronal"]
        for order, config in enumerate(row_config):
            data_rows = employees if config[1] == 'employees' else salaries
            incremental_field = config[3]
            to_count = config[2]
            is_date = config[4]
            summary.append(self.build_summary_row(patronal_number, self.year, order+1, data_rows, incremental_field, to_count, is_date))
        
        return summary
        
    def build_summary_row(self, patronal_number, year, order, data_rows, incremental_field, to_count, is_date):
        row = {
            "Nropatronal": patronal_number,
            "anho": year,
            "supjefesvarones": 0,
            "supjefesmujeres": 0,
            "empleadosvarones": 0,
            "empleadosmujeres": 0,
            "obrerosvarones": 0,
            "obrerosmujeres": 0,
            "menoresvarones": 0,
            "menoresmujeres": 0,
            "orden": order,
        }
        for data_row in data_rows:
            employee = self.env['hr.employee'].browse(data_row.get("odoo_id"))
            is_worker = employee.structure_type_id.wage_type == 'hourly' if employee.structure_type_id else False
            sexo = 'M' if employee.gender == 'male' else 'F',
            age = employee._get_age()
            is_minor = age > 0 and age < 18
            is_manager = employee.job_id.is_manager if employee.job_id else False

            value = 0
            
            if to_count:
                if is_date:
                    date_str = data_row.get(incremental_field)
                    if date_str and int(date_str[:4]) == year:
                        value = 1
                else:
                    value = 1
            else:
                value = data_row.get(incremental_field, 0)

            if is_manager:  # jefe
                if sexo == "M":
                    row["supjefesvarones"] += value
                else:
                    row["supjefesmujeres"] += value
            elif is_worker:  # obrero
                if sexo == "M":
                    row["obrerosvarones"] += value
                else:
                    row["obrerosmujeres"] += value
            else:  # empleados
                if sexo == "M":
                    row["empleadosvarones"] += value
                else:
                    row["empleadosmujeres"] += value

            # menores
            if is_minor:
                if sexo == "M":
                    row["menoresvarones"] += value
                else:
                    row["menoresmujeres"] += value

        return row
    
