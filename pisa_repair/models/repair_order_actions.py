from odoo import models, _
from odoo.exceptions import UserError, ValidationError
import logging

ics_logger = logging.getLogger('ics_logger')

class RepairOrderActions(models.Model):
    _inherit = 'repair.order'

    def action_next_state(self):
        self.ensure_one()        

        
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
        
        if self.scrapped:
            return {
                "type": "ir.actions.act_window",
                "res_model": "repair.donate.component.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {"active_id": self.id},
        }

        previous_state = self.state  
        required_fields_valid = self._validate_required_fields()

        if not required_fields_valid:
            next_state = next_states[self.state]
        else:
            next_state = 'done'


        # Pending to receive to Received
        try:
            tag_pending = self.env.ref('pisa_repair.pending_to_receive', raise_if_not_found=False)
        except Exception:
            tag_pending = None

        if (
            self.state == 'confirmed'
            and self.env.user.has_group('pisa_repair.group_micro')
            and tag_pending
            and tag_pending.id in self.tag_ids.ids
        ):
            self._manage_tags(
                tag_to_add_xmlid='pisa_repair.received',
                tag_to_remove_xmlid='pisa_repair.pending_to_receive,pisa_repair.not_received'
            )
            self.message_post(
                body=_("Unit received in micro stock."),
                subtype_xmlid="mail.mt_note",
            )

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

    
    def action_mark_pending_to_receive(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("This action is only available when the order is In Progress (confirmed)."))
        if not self.extraction:
            raise UserError(_("Mark 'Will Extraction Be Necessary' first."))
        
        required_fields_valid = self._validate_required_fields()
        
        if not required_fields_valid:
            self._manage_tags(
                tag_to_add_xmlid='pisa_repair.pending_to_receive',
                tag_to_remove_xmlid='pisa_repair.not_received'
            )

            self.message_post(
                body=_("The unit is pending to be received."),
                subtype_xmlid="mail.mt_note",
            )

        return True
    
    def action_mark_not_received(self):
        self.ensure_one()

        if self.state != 'confirmed':
            raise UserError(_("This action is only available when the order is In Progress (confirmed)."))

        if not self.env.user.has_group('pisa_repair.group_micro'):
            raise UserError(_("Only Micro can mark this as not received."))

        self._manage_tags(
            tag_to_add_xmlid='pisa_repair.not_received',
            tag_to_remove_xmlid='pisa_repair.pending_to_receive'
        )
        self.message_post(
            body=_("Unit was not received by Micro."),
            subtype_xmlid="mail.mt_note",
        )
        return True

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
    