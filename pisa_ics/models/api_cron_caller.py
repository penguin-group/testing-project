from odoo import models, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ApiCronCaller(models.Model):
    _name = 'api.cron.caller'
    _description = 'API Caller for CRON'

    @api.model
    def call_external_api(self):
        params = self.env['ir.config_parameter'].sudo()
        email = params.get_param('ICS_Email')
        password = params.get_param('ICS_Password')
        host = params.get_param('ICS_Host')

        url = f'{host}/login'

        if not email or not password or not host:
            _logger.warning("Incomplete ICS parameters: host=%s, email=%s", host, email)
            return

        headers = {
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "email": email, 
            "password": password
        })

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=5, verify=False)

            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    params.set_param('ICS_Token', token)
                    _logger.info("ICS token updated successfully.")
                else:
                    _logger.warning("No token received in the response.")
            else:
                _logger.error("Error authenticating with ICS: %s - %s", response.status_code, response.text)

        except Exception as e:
            _logger.exception("Error connecting to ICS API: %s", e)