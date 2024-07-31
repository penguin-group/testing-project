from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    """
    Esta clase obtiene el nombre de las cuentas analiticas desde: analytic_distribution
    y las concatena en la variable: analytic_account_names
    """

    analytic_account_names = fields.Char(
        compute='_compute_analytic_account_names',
        string='Analytic Account Names'
    )

    def _extract_ids_and_percentages(self, analytic_distribution):
        """
        Extrae y devuelve listas de IDs de cuentas analíticas y porcentajes para dos recorridos.
        """
        first_pass_ids = []
        second_pass_ids = []
        percentages = []

        if isinstance(analytic_distribution, dict):
            for ids_str, percentage in analytic_distribution.items():
                ids = ids_str.split(',')
                if len(ids) > 1:
                    try:
                        # Primer recorrido: tomar todos los primeros IDs
                        first_id = int(ids[0].strip())
                        first_pass_ids.append(first_id)

                        # Segundo recorrido: tomar todos los segundos IDs (si existen)
                        second_id = int(ids[1].strip()) if len(ids) > 1 else None
                        if second_id:
                            second_pass_ids.append(second_id)
                        
                        percentages.append(float(percentage))  # Convertir a float
                    except ValueError as e:
                        _logger.error("Error processing analytic_distribution: %s", str(e))

                    _logger.info("Current first_pass_ids: %s, second_pass_ids: %s, percentages: %s", first_pass_ids, second_pass_ids, percentages)
                else:
                    try:
                        # Tomar el ID único
                        unique_id = int(ids[0].strip())
                        first_pass_ids.append(unique_id)
                        percentages.append(float(percentage))  # Convertir a float
                    except ValueError as e:
                        _logger.error("Error processing analytic_distribution: %s", str(e))

                    _logger.info("Current first_pass_ids: %s, percentages: %s", first_pass_ids, percentages)
        else:
            _logger.error("Unsupported type for analytic_distribution: %s", type(analytic_distribution))
        
        _logger.info("Final first_pass_ids: %s, second_pass_ids: %s, percentages: %s", first_pass_ids, second_pass_ids, percentages)
        return first_pass_ids, second_pass_ids, percentages

    def _get_analytic_account_names(self, analytic_account_ids, percentages):
        """
        Devuelve los nombres de las cuentas analíticas con sus porcentajes formateados.
        """
        account_names = []
        for account_id, perc in zip(analytic_account_ids, percentages):
            if account_id:
                account = self.env['account.analytic.account'].browse(account_id)
                account_names.append(f"{perc}% {account.name}")
        
        formatted_names = ' | '.join(account_names)
        _logger.info("Generated analytic account names: %s", formatted_names)
        return formatted_names

    @api.depends('analytic_distribution')
    def _compute_analytic_account_names(self):
        for line in self:
            _logger.info("Processing line ID: %s with analytic_distribution: %s", line.id, line.analytic_distribution)
            if line.analytic_distribution:
                try:
                    # Obtener los IDs de las cuentas analíticas y sus porcentajes
                    first_pass_ids, second_pass_ids, percentages = self._extract_ids_and_percentages(line.analytic_distribution)

                    # Obtener los nombres de las cuentas analíticas formateados para los dos recorridos
                    first_pass_names = self._get_analytic_account_names(first_pass_ids, percentages)
                    second_pass_names = self._get_analytic_account_names(second_pass_ids, percentages) if second_pass_ids else ''

                    # Concatenar los resultados y guardarlos en analytic_account_names
                    line.analytic_account_names = f"{first_pass_names} | {second_pass_names}" if second_pass_names else first_pass_names
                except Exception as e:
                    _logger.error("Error processing analytic distribution for line ID %s: %s", line.id, str(e))
                    line.analytic_account_names = ''
            else:
                _logger.debug("No analytic distribution found for line ID: %s", line.id)
                line.analytic_account_names = ''
