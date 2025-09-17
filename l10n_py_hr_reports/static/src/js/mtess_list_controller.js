/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        this.action = useService("action");
        super.setup();
    },

    onGenerateButtonClick() {
        console.log("Generate Reports button clicked");
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'hr.reports.mtess.wizard',
            name: 'Generate MTESS Reports',
            views: [[false, 'form']],
            target: 'new',
        });
    }
});