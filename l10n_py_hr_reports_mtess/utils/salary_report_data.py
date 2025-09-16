from datetime import date, timedelta


class SalaryReportSalary:
    """
    A plain Python object representing one salary for reports.
    """

    MONTHS = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ]

    def __init__(self, env, payslips, year):
        self.env = env
        self.payslips = payslips
        contract = payslips['contract_id']
        employee = contract.employee_id
        year_hours = self._get_year_hours(year, employee)
        year_salaries = self._get_year_salaries()
        
        self.salaries = self.payroll_to_json(employee, contract, year_hours, year_salaries)

        
    def payroll_to_json(self, employee, contract, year_hours, year_salaries):
        wage_types = {'monthly': 'M', 'hourly': 'J'}
        wage_days = {'monthly': 30, 'hourly': 26}

        data = {
            "odoo_id": employee.id,
            "Nropatronal": contract.branch_id.mtess_patronal_number or "",
            "documento": employee.identification_id or "",
            "formadepago": wage_types.get(contract.wage_type, 'M'),
            "importeunitario": contract.wage / wage_days.get(contract.wage_type, 30) if contract.wage else 0,

            "h_ene": year_hours['january'],
            "s_ene": year_salaries['january'],
            "h_feb": year_hours['february'],
            "s_feb": year_salaries['february'],
            "h_mar": year_hours['march'],
            "s_mar": year_salaries['march'],
            "h_abr": year_hours['april'],
            "s_abr": year_salaries['april'],
            "h_may": year_hours['may'],
            "s_may": year_salaries['may'],
            "h_jun": year_hours['june'],
            "s_jun": year_salaries['june'],
            "h_jul": year_hours['july'],
            "s_jul": year_salaries['july'],
            "h_ago": year_hours['august'],
            "s_ago": year_salaries['august'],
            "h_set": year_hours['september'],
            "s_set": year_salaries['september'],
            "h_oct": year_hours['october'],
            "s_oct": year_salaries['october'],
            "h_nov": year_hours['november'],
            "s_nov": year_salaries['november'],
            "h_dic": year_hours['december'],
            "s_dic": year_salaries['december'],

            "h_50": self._get_quantity_by_code('OVERTIME_DAY_PY'),
            "s_50": self._get_total_by_code(['OVERTIME_DAY_PY']),
            "h_100": self._get_quantity_by_code('OVERTIME_NIGHT_PY'),
            "s_100": self._get_total_by_code(['OVERTIME_NIGHT_PY']),

            "Aguinaldo": self._get_total_by_code(['AGUINALDO_PY', 'AGUINALDO_PROP_PY']),
            "Beneficios": self._get_total_by_code(['NOTICE_PAY_PY', 'SEVERANCE_PY']),
            "Bonificaciones": self._get_total_by_code(['FAMILY_ALLOW_PY']),
            "Vacaciones": self._get_total_by_code(['VACATION_PROP_PY']),

            "total_h": sum(year_hours.values()),
            "total_s": sum(year_salaries.values()),
            "totalgeneral": sum(year_salaries.values())
                            + self._get_total_by_code(['AGUINALDO_PY', 'AGUINALDO_PROP_PY'])
                            + self._get_total_by_code(['NOTICE_PAY_PY', 'SEVERANCE_PY'])
                            + self._get_total_by_code(['FAMILY_ALLOW_PY'])
                            + self._get_total_by_code(['VACATION_PROP_PY']),
        }
        return data

    
    def _get_year_hours(self, year, employee):
        hours = {}
        for month in range(1, 13):
            hours[self.MONTHS[month - 1]] = self._get_worked_hours(year, month, employee)
        return hours

    def _get_year_salaries(self):
        salaries = {}
        for month in range(1, 13):
            salaries[self.MONTHS[month - 1]] = self._get_salary(month)
        return salaries
    
    def _get_worked_hours(self, year, month, employee, overtime=False):
        check_in_dt = f"{year}-{month:02d}-01 00:00:00"
        check_out_dt = f"{self._get_last_day_of_month(year, month)} 23:59:59"
        domain = [
            ('employee_id', '=', employee.id),
            ('check_in', '>=', check_in_dt),
            ('check_out', '<=', check_out_dt)
        ]
        attendances = self.env['hr.attendance'].search(domain)
        if overtime:
            hours = sum(attendances.mapped('validated_overtime_hours'))
        else:
            hours = sum(attendances.mapped('worked_hours')) 
        return hours

    def _get_last_day_of_month(self, year, month):
        """
        Returns the last day of the specified month and year.
        """
        if month == 12:
            next_month_first_day = date(year + 1, 1, 1)
        else:
            next_month_first_day = date(year, month + 1, 1)

        last_day = next_month_first_day - timedelta(days=1)
        return last_day

    def _get_payslip(self, month):
        for payslip in self.payslips:
            if payslip.date_from.month == month:
                return payslip
        return None

    def _get_salary(self, month):
        payslip = self._get_payslip(month)
        if not payslip:
            return 0
        return sum(line.total for line in payslip.line_ids if line.code == 'BASIC')

    def _get_quantity_by_code(self, code):
        return sum(self.payslips.line_ids.filtered(lambda line: line.code == code).mapped('quantity'))

    def _get_total_by_code(self, code):
        return sum(self.payslips.line_ids.filtered(lambda line: line.code in code).mapped('total'))


class SalaryReportData:
    """
    Aggregates salaries for a given period.
    """

    def __init__(self, env, start_date, end_date):
        self.env = env
        self.start_date = start_date
        self.end_date = end_date
        self.salaries = self._load_salaries()

    def _load_salaries(self):
        salaries = []
        payslips = self.env['hr.payslip'].search([
            ('date_from', '<=', self.end_date),
            ('date_to', '>=', self.start_date)
        ])
        contracts = payslips.mapped('contract_id')
        for contract in contracts:
            contract_payslips = payslips.filtered(lambda p: p.contract_id.id == contract.id)
            salaries.append(SalaryReportSalary(self.env, contract_payslips, year=self.start_date.year).salaries)
    
        return salaries
