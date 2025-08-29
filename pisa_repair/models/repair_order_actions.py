from odoo import models, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
from odoo.tools import format_datetime
from datetime import datetime, timezone
import logging
from odoo.addons.queue_job.exception import RetryableJobError

ics_logger = logging.getLogger('ics_logger')

class RepairOrderActions(models.Model):
    _inherit = 'repair.order'

    def action_next_state(self):
        self.ensure_one()

        if self.state == 'under_repair' and self.is_in_repair and not (self.repair_note or '').strip():
            raise UserError(_("You must fill in the Repair Note before moving to the next stage."))
        
        
        self = self.with_context(skip_custom_write=True)

        next_states = {
            'draft': 'confirmed',
            'confirmed': 'under_repair',
            'under_repair': 'ready_for_deployment',
            'ready_for_deployment': 'done',
        }

        if self.state == 'done':
            raise UserError(_("The repair order is already in the final state."))
        if self.state not in next_states:
            raise UserError(_("The transition to the next state is invalid."))

        previous_state = self.state  
        required_fields_valid = self._validate_required_fields()

        if not required_fields_valid:
            next_state = next_states[self.state]
        else:
            next_state = 'done'

        # Assign tags based on the state
        tag_transitions = {
            'confirmed': {
                'add': 'pisa_repair.confirmed',
                'remove': 'pisa_repair.open',
            },
            'under_repair': {
                'add': 'pisa_repair.pending_of_diagnosis',
                'remove': 'pisa_repair.confirmed',
            },
            'ready_for_deployment': {
                'add': 'pisa_repair.ready_for_deployment',
                'remove': 'pisa_repair.pending_of_diagnosis,pisa_repair.under_repair,pisa_repair.under_diagnosis,pisa_repair.external_service_repair'
            },
            'done': {
                'add': 'pisa_repair.done',
                'remove': 'pisa_repair.confirmed,pisa_repair.ready_for_deployment',
            },
        }

        if required_fields_valid and previous_state == 'under_repair':
            tag_transitions['done'] = {
                'add': 'pisa_repair.scrapped',
                'remove': 'pisa_repair.pending_of_diagnosis,pisa_repair.under_repair,pisa_repair.under_diagnosis,pisa_repair.external_service_repair'
            }
        
        # If under_warranty is checked and the next state is 'under_repair', remove all tags and add "external_service_repair"
        if self.under_warranty and next_state == 'under_repair':
            self.write({'tag_ids': [(5, 0, 0)]})
            self._manage_tags(tag_to_add_xmlid='pisa_repair.external_service_repair')
        else:
            tag_data = tag_transitions.get(next_state, {})
            self._manage_tags(tag_to_add_xmlid=tag_data.get('add'), tag_to_remove_xmlid=tag_data.get('remove'))        

        if next_state == 'done':
            stock_moves = self.move_ids.filtered(lambda m: m.state == 'assigned')
            for move in stock_moves:
                move.write({'state': 'done'})

        self.state = next_state if not required_fields_valid else self.state


    def action_start_diagnosis(self):
        tag_to_add_xmlid = 'pisa_repair.under_diagnosis'
        tag_to_remove_xmlid = 'pisa_repair.pending_of_diagnosis'
        self._manage_tags(tag_to_add_xmlid=tag_to_add_xmlid, tag_to_remove_xmlid=tag_to_remove_xmlid)


    def action_start_repair(self):
        
        tag_to_remove_xmlid = 'pisa_repair.under_diagnosis'
        tag_to_add_xmlid = 'pisa_repair.under_repair'
        self._manage_tags(tag_to_add_xmlid=tag_to_add_xmlid, tag_to_remove_xmlid=tag_to_remove_xmlid)


    def action_create_sale_order(self):
        """Executes Odoo's original function and adds the 'Quotation Created' tag,
        only if there is a diagnostic_note."""

        for record in self:
            if not (record.diagnostic_note or "").strip():
                raise ValidationError(_("You must fill in the Diagnostic Note before creating a quotation."))
            
        result = super().action_create_sale_order() # Call Odoo's original function


        if isinstance(result, dict) and result.get("res_id"):
            sale_order = self.env['sale.order'].browse(result['res_id'])
            tag_not_consolidated = self.env.ref("pisa_repair.crm_tag_not_consolidated", raise_if_not_found=False)
            if tag_not_consolidated:
                sale_order.write({'tag_ids': [(4, tag_not_consolidated.id)]})

        tag_to_add_xmlid = 'pisa_repair.quotation_created'
        tag_to_remove_xmlid = 'pisa_repair.under_diagnosis'
        self._manage_tags(tag_to_add_xmlid=tag_to_add_xmlid, tag_to_remove_xmlid=tag_to_remove_xmlid)

        return result
    
    def action_repair_cancel(self):
        """Extends the cancellation function to remove all tags and add only 'Cancelled'."""
        res = super().action_repair_cancel()  # Call Odoo's original cancel function

        for record in self:
            # Remove all existing tags
            record.write({'tag_ids': [(5, 0, 0)]})
            
            # Add the "Cancelled" tag
            tag_to_add_xmlid = 'pisa_repair.cancel'
            record._manage_tags(tag_to_add_xmlid=tag_to_add_xmlid)

        return res

    def _manage_tags(self, tag_to_add_xmlid=None, tag_to_remove_xmlid=None):
        if tag_to_remove_xmlid and isinstance(tag_to_remove_xmlid, str):
            tag_to_remove_xmlid = [tag.strip() for tag in tag_to_remove_xmlid.split(',')]

        tags_to_add = self.env.ref(tag_to_add_xmlid, raise_if_not_found=False) if tag_to_add_xmlid else None
        tags_to_remove = [self.env.ref(tag_xmlid, raise_if_not_found=False) for tag_xmlid in tag_to_remove_xmlid] if tag_to_remove_xmlid else []
        
        updates = []
        removed_tags = []  # List of actually removed tags

        # Check tags to remove
        for tag in tags_to_remove:
            if tag and tag.id in self.tag_ids.ids:
                updates.append((3, tag.id))
                removed_tags.append(tag.name) # Only add actually removed tags
        
        if tags_to_add:
            updates.append((4, tags_to_add.id))

            # Register in history if we are in "under_repair"
            if self.state == 'under_repair':
                self.env['repair.order.tag.history'].create({
                    'repair_order_id': self.id,
                    'tag_id': tags_to_add.id,
                    'user_id': self.env.user.id,
                })

                # If nothing was removed, show the tags that remain in the order
                tags_removed_text = ', '.join(removed_tags) if removed_tags else self._compute_current_tags()

                message = f"{tags_removed_text} ➝ {tags_to_add.name} / Tags"

                self.message_post(
                    body=message,
                    author_id=self.env.user.partner_id.id,
                    subtype_xmlid="mail.mt_note"
                )

        if updates:
            self.write({'tag_ids': updates})

    def _compute_current_tags(self):
        """Returns the current tags in the order as a comma-separated string."""
        return ', '.join(self.tag_ids.mapped('name'))

    def _validate_required_fields(self):
        if self.state == 'confirmed' and self.env.user.has_group('pisa_repair.group_mining'):
            if not self.initial_state:
                raise ValidationError(_("The 'Initial State' field is mandatory. You must select an option."))
             
            if self.performed_steps_rel_ids and not all(self.performed_steps_rel_ids.mapped('completed')):
                raise ValidationError(_("All steps in 'Performed Steps Relation' must be completed before proceeding."))
            
            if not self.evidence_image:
                raise ValidationError(_("The 'Failure Evidence' field is mandatory. You must upload an image."))
            
            if self.needs_rest and not self.end_rest:
                raise ValidationError(_("You cannot proceed while the miner is in rest mode. Please ensure all necessary conditions are met before continuing."))

            if not self.extraction:
                self.write({'state': 'done'})
                return True
            

        if self.state == 'under_repair' and self.env.user.has_group('pisa_repair.group_micro'):
            if self.scrapped:
                self.write({'state': 'done'})
                return True

        return False

            
        

    def action_open_validation_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ticket Validation'),
            'res_model': 'ticket.validation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_repair_order_id': self.id,
            }
        }
    
    def get_miner_counts_by_container(self, container_name):
        """
        Obtiene el total de mineros en el contenedor, la cantidad de mineros válidos
        (sin órdenes en estados inválidos y sin estar marcados como 'scrapped'),
        así como el hashrate nominal y el consumo teórico.
        """

        allowed_states = ('draft', 'confirmed', 'ready_for_deployment', 'done')

        query = """
            WITH relevant_lots AS (
                SELECT 
                    sl.id AS lot_id,
                    pt.miner_hashrate_nominal,
                    pt.miner_theoretical_consumption
                FROM stock_lot sl
                JOIN product_product pp ON sl.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE sl.container ILIKE %s
            ),
            lots_with_invalid_orders AS (
                SELECT DISTINCT lot_id
                FROM repair_order
                WHERE lot_id IS NOT NULL
                AND state NOT IN %s
            ),
            lots_with_scrapped_orders AS (
                SELECT DISTINCT lot_id
                FROM repair_order
                WHERE lot_id IS NOT NULL
                AND scrapped IS TRUE
            ),
            valid_lots AS (
                SELECT *
                FROM relevant_lots
                WHERE lot_id NOT IN (
                    SELECT lot_id FROM lots_with_invalid_orders
                    UNION
                    SELECT lot_id FROM lots_with_scrapped_orders
                )
            )
            SELECT
                (SELECT COUNT(*) FROM relevant_lots) AS total_miners,
                (SELECT COUNT(*) FROM valid_lots) AS valid_miners,
                COALESCE(SUM(valid_lots.miner_hashrate_nominal), 0) AS hashrate_nominal,
                COALESCE(SUM(valid_lots.miner_theoretical_consumption), 0) AS theoretical_consumption
            FROM valid_lots;
        """

        self.env.cr.execute(query, [f'%{container_name}%', allowed_states])
        result = self.env.cr.fetchone()

        return {
            'total_miners': result[0],
            'valid_miners': result[1],
            'hashrate_nominal': result[2],
            'theoretical_consumption': result[3],
        }


    
    def _perform_state_update_to_ics(self, container=None):
        param = self.env['ir.config_parameter'].sudo()
        url = param.get_param('ICS_Url')
        token = param.get_param('ICS_Token')

        if not url or not token:
            ics_logger.warning("URL or TOKEN not found")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            container = container or self.lot_id.container
            if not container:
                ics_logger.warning("Container not found")
                return

            ALL_STATES = ['draft', 'confirmed', 'under_repair', 'ready_for_deployment', 'done', 'cancel']
            IGNORED_TAGS = ["Open", "In Progress", "Ready for Deployment", "Done", "Cancelled"]

            grouped_data = self.env['repair.order'].read_group(
                domain=[('lot_id.container', 'ilike', container)],
                fields=['state'],
                groupby=['state']
            )
            state_summary = {g['state']: g.get('state_count', 0) for g in grouped_data}
            for state in ALL_STATES:
                state_summary.setdefault(state, 0)

            counts = self.get_miner_counts_by_container(container)
            ics_logger.info(
                "Total mineros: %s - Válidos: %s - Hashrate Nominal: %s - Consumo Teórico: %s",
                counts['total_miners'],
                counts['valid_miners'],
                counts['hashrate_nominal'],
                counts['theoretical_consumption']
            )

            for state in ALL_STATES:
                state_summary.setdefault(state, 0)

            self.env.cr.execute("""
                SELECT rt.name, COUNT(*) AS count
                FROM repair_order_repair_tags_rel rrel
                JOIN repair_order ro ON rrel.repair_order_id = ro.id
                JOIN stock_lot sl ON ro.lot_id = sl.id
                JOIN repair_tags rt ON rrel.repair_tags_id = rt.id
                WHERE sl.container ILIKE %s
                AND rt.name NOT IN %s
                GROUP BY rt.name
            """, [f'%{container}%', tuple(IGNORED_TAGS)])
            tag_rows = dict(self.env.cr.fetchall())

            all_tags = self.env['repair.tags'].search([
                ('name', 'not in', IGNORED_TAGS)
            ]).mapped('name')

            tag_summary = {tag: tag_rows.get(tag, 0) for tag in all_tags}

            data = [{
                "Container": container,
                "CreatedAt": datetime.now(timezone.utc).isoformat(),
                "TotalMiners": counts['valid_miners'],
                "HashrateNominal": counts['hashrate_nominal'],
                "TheoreticalConsumption": counts['theoretical_consumption'],
                "Status": state_summary,
                "Tags": tag_summary
            }]

            post_response = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
            post_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            ics_logger.warning(f"[ICS] Failed to POST to ICS for container {container}: {e}")
            raise RetryableJobError(f"Temporary ICS POST failure: {e}")

    def _send_state_update_to_ics(self, container=None):
        ics_logger.info("Enqueuing ICS job for RO %s", self.name)
        (
            self.sudo()
            .with_delay(
                description=f"ICS sync for {self.lot_id.container}",
                channel="root.ics",
                priority=30,
                max_retries=15
            )
            ._perform_state_update_to_ics(container)
        )
