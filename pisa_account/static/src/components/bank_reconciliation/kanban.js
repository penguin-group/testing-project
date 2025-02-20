/** @odoo-module **/
import { BankRecKanbanController } from "@account_accountant/components/bank_reconciliation/kanban";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";

patch(BankRecKanbanController.prototype, {
    async onWillStartAfterLoad() {
        // Call the original method first
        await super.onWillStartAfterLoad?.();

        // Check for the additional group
        const hasGroupFinance = await user.hasGroup("pisa_account.group_account_sr_finance");

        // Update hasGroupReadOnly if the user is in either group
        this.hasGroupReadOnly = this.hasGroupReadOnly || hasGroupFinance;
    }
});
