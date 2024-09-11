from odoo import api, fields, models, exceptions
import datetime, pytz, logging
from odoo.addons.rrhh_asistencias.controllers import controllers as c
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Marcadores(models.Model):
    _name = 'rrhh_asistencias.marcadores'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Nombre del marcador', required=True)
    company_id = fields.Many2one('res.company', string='Compañía')
    codigo_interno = fields.Char('Código interno')
    ip_address = fields.Char('Dirección IP', required=True)
    port = fields.Integer('Puerto', default=4370, required=True)
    usuario = fields.Char('Usuario')
    device_password = fields.Integer('Password')
    active = fields.Boolean(string='Active', default=True)
    connection_error_message = fields.Char(string="Mensaje de Conexión", required=False, )

    def send_email_alert(self, error):
        self.ensure_one()
        to_emails = ", ".join(self.message_follower_ids.mapped('email'))
        self.connection_error_message = "Falló la conexión con el reloj biométrico. Error: " + str(error)
        template = self.env.ref('rrhh_asistencias.error_message_email_template')
        template.send_mail(self.id, force_send=True, email_values={'email_to': to_emails})
    
    def test_connection(self):
        self.ensure_one()
        connection_success = False
        self.connection_error_message = ""
        try:
            conn = c.ConnectToDevice(self.ip_address, self.port, self.device_password)
            if conn:
                connection_success = True
        except (Exception) as error:
            self.send_email_alert(error)
        finally:
            message = "Conexión %s con el reloj %s" % (('EXITOSA' if connection_success else 'FALLIDA'), self.name)

            connection_message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success' if connection_success else 'danger',
                    'sticky': False,
                }
            }
            return connection_message

    def get_attendances(self):
        # rrhh_asistencias/models/marcadores.py
        ids_unicos = self.env['rrhh_asistencias.marcaciones'].search([('id_unico_marcacion', '!=', False)]).mapped(
            'id_unico_marcacion')
        for this in self:
            try:
                with c.ConnectToDevice(this.ip_address, this.port, this.device_password) as conn:
                    if conn:
                        _logger.info('Obteniendo las marcaciones del reloj ' + this.name)
                        attendances = conn.get_attendance()
                        _logger.info('Marcaciones obtenidas del reloj ' + this.name)
                        for attendance in attendances:
                            fecha_hora_real = pytz.timezone('America/Asuncion').localize(attendance.timestamp)
                            fecha_hora_utc = fecha_hora_real.astimezone(pytz.timezone('UTC'))

                            id_unico = attendance.user_id + str(attendance.timestamp)
                            if id_unico not in ids_unicos:
                                _logger.info('Procesando marcación ' + id_unico)
                                self.env['rrhh_asistencias.marcaciones'].create({
                                    'id_unico_marcacion': id_unico,
                                    'id_marcacion': attendance.user_id,
                                    'id_marcador': this.id,
                                    'raw_fecha_hora': datetime.datetime.strftime(fecha_hora_utc, '%Y-%m-%d %H:%M:%S'),
                                })
                                self._cr.commit()
                                ids_unicos.append(id_unico)
                        # conn.clear_attendance()
            except (Exception) as error:
                self.send_email_alert(error)
    # def button_obtener_marcaciones(self):
    #     zk = zklib.ZKLib(self.ip_address, int(self.port))
    #     ret = zk.connect()
    #     if ret == True:
    #         zk.disableDevice()
    #         attendance = zk.getAttendance()
    #         for i in attendance:
    #             fecha_hora = i[2]
    #             hora = fecha_hora.hour + fecha_hora.minute / 60
    #             marcacion = {
    #                 'id_marcador': self.id,
    #                 'id_marcacion': i[0],
    #                 'raw_fecha_hora': fecha_hora,
    #                 'fecha': datetime.strftime(fecha_hora, '%Y-%m-%d'),
    #                 'hora': hora
    #             }
    #             if str(fecha_hora) > "2019-10-21 07:16:17":
    #                 self.env['interfaces_payroll.marcaciones'].create(marcacion)
    #         zk.clearAttendance()
    #         zk.enableDevice()
    #         zk.disconnect()
    #

    def obtener_marcaciones_cron(self):
        marcadores = self.env['rrhh_asistencias.marcadores'].search([('active', '=', True)])
        for i in marcadores:
            i.get_attendances()
        return

    def crear_asistencias_cron(self):
        marcadores = self.env['rrhh_asistencias.marcadores'].search([('active', '=', True)])
        for marcador in marcadores:
            try:
                marcaciones = self.env['rrhh_asistencias.marcaciones']
                marcaciones_nuevas = marcaciones.search([
                    ('marcacion_procesada','=',False),
                    ('asistencia_creada','=',False),
                    ('id_marcador', '=', marcador.id)
                ])
                marcaciones_a_reprocesar = marcaciones.search([
                    ('marcacion_procesada','=',True),
                    ('asistencia_creada','=',False),
                    ('id_marcador', '=', marcador.id)
                ])
                marcaciones_nuevas = marcaciones_nuevas.filtered(lambda x:x.employee_id)
                marcaciones_a_reprocesar = marcaciones_a_reprocesar.filtered(lambda x:x.employee_id)

                marcaciones_nuevas.create_attendances()
                marcaciones_a_reprocesar.create_attendances()
            except (Exception) as error:
                _logger.error(f"Error al crear asistencia desde el marcador: {marcador.name}: {str(error)}")
                marcador.send_email_alert(error)
