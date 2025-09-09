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
        wage_types = {'monthly': 'M', 'hourly': 'J'}
        wage_days = {'monthly': 30, 'hourly': 26}
        
        self.patronal_number = contract.branch_id.mtess_patronal_number or ""
        self.identification_number = employee.identification_id or ""
        self.wage_type = wage_types.get(contract.wage_type, 'M')
        self.wage = contract.wage / wage_days.get(contract.wage_type, 30) if contract.wage else 0
        self.hours_january = year_hours['january']
        self.salary_january = year_salaries['january']
        self.hours_february = year_hours['february']
        self.salary_february = year_salaries['february']
        self.hours_march = year_hours['march']
        self.salary_march = year_salaries['march']
        self.hours_april = year_hours['april']
        self.salary_april = year_salaries['april']
        self.hours_may = year_hours['may']
        self.salary_may = year_salaries['may']
        self.hours_june = year_hours['june']
        self.salary_june = year_salaries['june']
        self.hours_july = year_hours['july']
        self.salary_july = year_salaries['july']
        self.hours_august = year_hours['august']
        self.salary_august = year_salaries['august']
        self.hours_september = year_hours['september']
        self.salary_september = year_salaries['september']
        self.hours_october = year_hours['october']
        self.salary_october = year_salaries['october']
        self.hours_november = year_hours['november']
        self.salary_november = year_salaries['november']
        self.hours_december = year_hours['december']
        self.salary_december = year_salaries['december']
        self.overtime_hours_50 = self._get_quantity_by_code('OVERTIME_DAY_PY')
        self.overtime_total_50 = self._get_total_by_code(['OVERTIME_DAY_PY'])
        self.overtime_hours_100 = self._get_quantity_by_code('OVERTIME_NIGHT_PY')
        self.overtime_total_100 = self._get_total_by_code(['OVERTIME_NIGHT_PY'])
        self.year_end_bonus = self._get_total_by_code(['AGUINALDO_PY', 'AGUINALDO_PROP_PY'])
        self.benefits = self._get_total_by_code(['NOTICE_PAY_PY', 'SEVERANCE_PY'])
        self.family_allowance = self._get_total_by_code(['FAMILY_ALLOW_PY'])
        self.vacation_pay = self._get_total_by_code(['VACATION_PROP_PY'])
        self.hours_total = sum(year_hours.values())
        self.salaries_total = sum(year_salaries.values())
        self.total = self.salaries_total + self.year_end_bonus + self.benefits + self.family_allowance + self.vacation_pay
        
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
            salaries.append(SalaryReportSalary(self.env, contract_payslips, year=self.start_date.year))
    
        return salaries
