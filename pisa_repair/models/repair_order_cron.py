# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
from datetime import timedelta
import logging

_logger = logging.getLogger('ics_logger')

BACKOFF_BASE_MIN = 5
MAX_ATTEMPTS     = 10
BATCH_SIZE       = 50

class PisaIcsData(models.Model):
    _name = 'pisa.ics.data'
    _description = 'ICS data records'
    _order = 'id asc'

    _logger.warning("Función inicializada")

    state = fields.Selection(
        [('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')],
        default='pending',
        index=True,
        required=True
    )

    container = fields.Char(index=True)
    data = fields.Json(string='Data to send')
    response_code = fields.Integer(readonly=True)
    response_body = fields.Text(readonly=True)
    attempts = fields.Integer(default=0, readonly=True)
    last_error = fields.Text(readonly=True)
    sent_at = fields.Datetime(index=True)
    next_try_at = fields.Datetime(index=True, default=lambda self: fields.Datetime.now())

    def _get_auth_conf(self):
        Param = self.env['ir.config_parameter'].sudo()
        url = Param.get_param('ICS_Url')
        token = Param.get_param('ICS_Token')
        return url, token

    def _compute_backoff_next_try(self):
        minutes = max(1, (self.attempts or 1) ** 2 * BACKOFF_BASE_MIN)
        return fields.Datetime.now() + timedelta(minutes=minutes)

    def _send_one(self):
        self.ensure_one()
        url, token = self._get_auth_conf()

        if not url or not token:
            self.write({
                'attempts': self.attempts + 1,
                'last_error': 'Missing ICS_Url or ICS_Token',
                'next_try_at': self._compute_backoff_next_try(),
            })
            _logger.warning("[ICS][DATA] Missing URL/TOKEN for id=%s", self.id)
            return

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = self.data or []

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
            vals = {
                'response_code': resp.status_code,
                'response_body': resp.text[:2000],
            }
            if 200 <= resp.status_code < 300:
                vals.update({'state': 'sent', 'sent_at': fields.Datetime.now(), 'last_error': False})
                _logger.info("[ICS][DATA] SENT id=%s code=%s", self.id, resp.status_code)
            else:
                attempts = self.attempts + 1
                vals.update({
                    'state': 'failed' if attempts >= MAX_ATTEMPTS else 'pending',
                    'attempts': attempts,
                    'last_error': f"HTTP {resp.status_code}: {resp.text[:1000]}",
                    'next_try_at': self._compute_backoff_next_try(),
                })
                _logger.error("[ICS][DATA] HTTP error id=%s attempts=%s code=%s",
                              self.id, attempts, resp.status_code)
            self.write(vals)

        except Exception as e:
            attempts = self.attempts + 1
            self.write({
                'state': 'failed' if attempts >= MAX_ATTEMPTS else 'pending',
                'attempts': attempts,
                'last_error': str(e),
                'next_try_at': self._compute_backoff_next_try(),
            })
            _logger.exception("[ICS][DATA] Exception sending id=%s attempts=%s", self.id, attempts)

    # ---------- CRON ----------
    @api.model
    def cron_process_ics_data(self):
        now = fields.Datetime.now()
        domain = [('state', '=', 'pending'), ('next_try_at', '<=', now)]
        to_send = self.search(domain, limit=BATCH_SIZE)
        _logger.info("[ICS][DATA] Cron picked %s records", len(to_send))
        for rec in to_send:
            rec._send_one()
            self.env.cr.commit()
