from odoo import models, api
import requests
import logging
import json

api_cron_logger = logging.getLogger('api_cron_caller')

class ApiCronCaller(models.Model):
    _name = 'api.cron.caller'
    _description = 'API Caller for CRON'

    @api.model
    def call_external_api(self):

        params = self.env['ir.config_parameter'].sudo()
        email = params.get_param('ICS_Email')
        password = params.get_param('ICS_Password')
        host = params.get_param('ICS_Host')

        url = f'http://{host}/login'

        if not email or not password or not host:
            api_cron_logger.error('Configuration not found.')
            api_cron_logger.error(f'ICS_Email: {email}')
            api_cron_logger.error(f'ICS_Host: {host}')
            api_cron_logger.error(f'ICS_Password: {password}')
            return

        headers = {
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "email": email, 
            "password": password
        })

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=5)

            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    params.set_param('ICS_Token', token)
                    api_cron_logger.info('Token successfully updated.')
                else:
                    api_cron_logger.warning('Token not found in the response.')
            else:
                api_cron_logger.warning('Error code: %s', response.status_code)
        except Exception as e:
            api_cron_logger.error('Error while calling the API: %s', str(e))
