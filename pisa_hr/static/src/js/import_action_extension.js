/** @odoo-module **/

import { ImportAction } from "@base_import/import_action/import_action";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ImportAction.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    async openAttendanceWizard() {
        try {
            const action = {
                type: 'ir.actions.act_window',
                res_model: 'parse.attendance.file.wizard',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: this.props.context || {}
            };

            this.actionService.doAction(action);
        } catch (error) {
            console.error('Error opening attendance wizard:', error);
        }
    }
});