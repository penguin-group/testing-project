from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class IPSReportSalary:
    """
    A plain Python object representing one employee for IPS reports.
    """

    def __init__(self, env, year, month, contract_payslips):
        self.env = env
        self.year = year
        self.month = month
        
        contract = contract_payslips[0]['contract_id']
        employee = contract.employee_id

        self.employee = employee
        self.contract = contract
        self.contract_payslips = contract_payslips
        
        self.salary = self._payroll_to_list()

    
    def _payroll_to_list(self):
        partner = self.employee._get_related_partners()[0]

        employee_item = [
            self.contract.branch_id.ips_patronal_number or "", # Nro. Patronal
            "", # Nro. Asegurado
            self.employee.identification_id or "", # C.I.N°
            partner.lastname, # Apellido
            partner.firstname, # Nombre
            "E", # Categoría
            self._get_worked_days(), # Días Trab.
            self._get_salary(), # Salario
            str(self.month) + str(self.year), # Mes/Año
            0, # Cód. Actividad
            self._get_salary(net=True), # Salario Real
        ]

        return employee_item
    
    def _get_worked_days(self):
        start_date = date(self.year, self.month, 1)
        end_date = start_date + relativedelta(day=31)
        domain = [
            ('employee_id', '=', self.employee.id),
            ('check_in', '>=', start_date.strftime("%Y-%m-%d %H:%M:%S")),
            ('check_out', '<=', end_date.strftime("%Y-%m-%d 23:59:59"))
        ]
        attendances = self.env['hr.attendance'].search(domain)

        dates = attendances.mapped('check_in')
        worked_days = len(set(d.date() for d in dates))

        return worked_days

    def _get_salary(self, net=False):
        if not self.contract_payslips:
            return 0
        code = 'NET' if net else 'BASIC' 
        lines = self.contract_payslips.line_ids.filtered(lambda l: l.code == code)
        return self._get_total_in_pyg(lines)

    def _get_total_in_pyg(self, payslip_lines):
        totals = []
        pyg_currency = self.env.ref('base.PYG')
        for line in payslip_lines:
            if line.currency_id == pyg_currency:
                totals.append(line.total)
            else:
                total = line.currency_id._convert(
                    line.total,
                    pyg_currency,
                    self.env.company,
                    line.slip_id.date,
                )
                totals.append(total)
        return sum(totals)



class IPSReportData:
    """
    Aggregates salaries for a given period.
    """

    def __init__(self, env, year, month):
        self.env = env
        self.year = year
        self.month = month
        self.salaries = self._load_salaries()

    def _load_salaries(self):
        salaries = []
        start_date = date(self.year, self.month, 1)
        end_date = start_date + relativedelta(day=31)
        payslips = self.env['hr.payslip'].search([
            ('date_from', '<=', start_date),
            ('date_to', '>=', end_date)
        ])
        contracts = payslips.mapped('contract_id')
        for contract in contracts:
            contract_payslips = payslips.filtered(lambda p: p.contract_id.id == contract.id)
            salaries.append(IPSReportSalary(self.env, self.year, self.month, contract_payslips).salary)
    
        return salaries
