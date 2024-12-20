from odoo import models, api, fields

class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'

    def _tracking_value_format_model(self, model):
        """ Return structure and formatted data structure to be used by chatter
        to display tracking values. Order it according to asked display, aka
        ascending sequence (and field name).

        Override reason: Change the float field types to string to allow 12 decimal places

        :return list: for each tracking value in self, their formatted display
          values given as a dict;
        """
        if not self:
            return []

        # fetch model-based information
        if model:
            TrackedModel = self.env[model]
            tracked_fields = TrackedModel.fields_get(self.field_id.mapped('name'), attributes={'string', 'type'})
            model_sequence_info = dict(TrackedModel._mail_track_order_fields(tracked_fields)) if model else {}
        else:
            tracked_fields, model_sequence_info = {}, {}

        # generate sequence of trackings
        fields_sequence_map = dict(
            {
                tracking.field_info['name']: tracking.field_info.get('sequence', 100)
                for tracking in self.filtered('field_info')
            },
            **model_sequence_info,
        )
        # generate dict of field information, if available
        fields_col_info = (
            tracked_fields.get(tracking.field_id.name) or {
                'string': tracking.field_info['desc'] if tracking.field_info else self.env._('Unknown'),
                'type': tracking.field_info['type'] if tracking.field_info else 'char',
            } for tracking in self
        )

        formatted = [
            {
                'changedField': col_info['string'],
                'id': tracking.id,
                'fieldName': tracking.field_id.name or (tracking.field_info['name'] if tracking.field_info else 'unknown'),
                'fieldType': self._get_field_type(col_info['type']),
                'newValue': {
                    'currencyId': tracking.currency_id.id,
                    'value': self._format_value(col_info['type'], tracking._format_display_value(col_info['type'], new=True)[0]),
                },
                'oldValue': {
                    'currencyId': tracking.currency_id.id,
                    'value': self._format_value(col_info['type'], tracking._format_display_value(col_info['type'], new=False)[0]),
                },
            }
            for tracking, col_info in zip(self, fields_col_info)
        ]
        formatted.sort(
            key=lambda info: (fields_sequence_map.get(info['fieldName'], 100), info['fieldName']),
            reverse=False,
        )
        return formatted

    def _get_field_type(self, field_type):
        """ Return the field type, setting certain types to 'string'."""
        if field_type in {'float', 'monetary'}:
            return 'string'
        return field_type

    def _format_value(self, field_type, value):
        """Format the value based on the field type."""
        if field_type in {'float', 'monetary'} and value is not None:
            return '{:.12f}'.format(float(value))  # Ensure value is a float and format it
        return value