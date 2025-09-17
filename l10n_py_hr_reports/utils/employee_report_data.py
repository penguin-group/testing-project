class EmployeeReportEmployee:
    """
    A plain Python object representing one employee for reports.
    """

    def __init__(self, employee, contract):
        partner = employee._get_related_partners()[0]
        birth_date = employee.birthday.strftime("%Y-%m-%d") if employee.birthday else None
        age = employee._get_age()
        is_minor = age > 0 and age < 18
        
        self.data = self.employee_to_json(employee, contract, partner, birth_date, is_minor)

    def employee_to_json(self, employee, contract, partner, birth_date, is_minor):
        data = {
            "odoo_id": employee.id,
            "Nropatronal": contract.branch_id.mtess_patronal_number or "",
            "Documento": employee.identification_id or "",
            "Nombre": partner.firstname or "",
            "Apellido": partner.lastname or "",
            "Sexo": 'M' if employee.gender == 'male' else 'F',
            "Estadocivil": self._get_marital_status(employee.marital),
            "Fechanac": employee.birthday.strftime("%Y-%m-%d") if employee.birthday else "",
            "Nacionalidad": employee.country_id.name or "",
            "Domicilio": self._get_address(employee),
            "Fechanacmenor": birth_date if is_minor else "",
            "hijosmenores": employee.children or 0,
            "cargo": employee.job_id.name or "",
            "profesion": employee.profession or "",
            "fechaentrada": contract.date_start.strftime("%Y-%m-%d"),
            "horariotrabajo": contract.resource_calendar_id.name if is_minor and contract.resource_calendar_id else "",
            "menorescapa": contract.date_start.strftime("%Y-%m-%d") if is_minor else "",
            "menoresescolar": employee.minor_employee_school_status or "",
            "fechasalida": contract.date_end.strftime("%Y-%m-%d") if contract.date_end else "",
            "motivosalida": contract.end_reason or "",
            "Estado": "Activo" if not contract.date_end else "Inactivo",
        }
        return data
    
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

        # contracts in the period
        contracts = Contract.search([
            ('date_start', '<=', self.end_date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', self.start_date)
        ])

        employees = []
        for contract in contracts.filtered(lambda c: c.employee_id):
            emp = contract.employee_id
            employee = EmployeeReportEmployee(emp, contract)
            employees.append(employee.data)
        return employees
