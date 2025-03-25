/** @odoo-module **/
import { BankRecGlobalInfo } from "@account_accountant/components/bank_reconciliation/global_info";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";

patch(BankRecGlobalInfo.prototype, {
    setup() {
        // Call the original setup function
        super.setup?.();

        // Extend onWillStart to check for the additional group
        onWillStart(async () => {
            const hasGroupFinance = await user.hasGroup("pisa_account.group_account_sr_finance");
            this.hasGroupReadOnly = this.hasGroupReadOnly || hasGroupFinance;
        });
    }
});
