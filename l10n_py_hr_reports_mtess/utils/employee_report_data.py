class EmployeeReportEmployee:
    """
    A plain Python object representing one employee for reports.
    """

    def __init__(self, employee, contract):
        partner = employee._get_related_partners()[0]
        birth_date = employee.birthday.strftime("%Y-%m-%d") if employee.birthday else None
        age = employee._get_age()
        is_minor = age > 0 and age < 18
        
        self.patronal_number = contract.branch_id.mtess_patronal_number or ""
        self.identification_number = employee.identification_id or ""
        self.first_name = partner.firstname or ""
        self.last_name = partner.lastname or ""
        self.gender = 'M' if employee.gender == 'male' else 'F'
        self.marital_status = self._get_marital_status(employee.marital)
        self.birth_date = employee.birthday.strftime("%Y-%m-%d") or None
        self.nationality = employee.country_id.name or ""
        self.address = self._get_address(employee)
        self.minor_birth_date = birth_date if is_minor else ""
        self.minor_children = employee.children or 0
        self.job_title = employee.job_id.name or ""
        self.profession = employee.profession or ""
        self.date_start = contract.date_start.strftime("%Y-%m-%d")
        self.work_schedule = contract.resource_calendar_id.name if is_minor and contract.resource_calendar_id else ""
        self.minor_date_start = contract.date_start.strftime("%Y-%m-%d") if is_minor else ""
        self.minor_school_status = employee.minor_employee_school_status or ""
        self.date_end = contract.date_end.strftime("%Y-%m-%d") if contract.date_end else ""
        self.end_reason = contract.end_reason or ""

    def _get_marital_status(self, odoo_marital):
        """Map Odoo marital status to report values."""
        mapping = {
            'single': 'S',
            'married': 'C',
            'divorced': 'D',
            'widowed': 'V',
        }
        return mapping.get(odoo_marital, '')

    def _get_address(self, employee):
        """Construct a full address string from the employee's address fields."""
        parts = [
            employee.private_state_id.name or "",
            employee.private_city or "",
            employee.private_street or "",
        ]
        return " + ".join(part for part in parts if part).strip()



class EmployeeReportData:
    """
    Aggregates employees and their contracts for a given period.
    """

    def __init__(self, env, start_date, end_date):
        self.env = env
        self.start_date = start_date
        self.end_date = end_date
        self.employees = self._load_employees()

    def _load_employees(self):
        Contract = self.env['hr.contract']

        # contracts overlapping the period
        contracts = Contract.search([
            ('date_start', '<=', self.end_date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', self.start_date)
        ])

        employees = []
        for contract in contracts.filtered(lambda c: c.employee_id):
            emp = contract.employee_id
            employees.append(EmployeeReportEmployee(emp, contract))
        return employees
