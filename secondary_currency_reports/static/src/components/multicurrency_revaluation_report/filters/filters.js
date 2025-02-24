import { AccountReport } from "@account_reports/components/account_report/account_report";
import { AccountReportFilters } from "@account_reports/components/account_report/filters/filters";
import { patch } from "@web/core/utils/patch";

export class MulticurrencyRevaluationReportFilters extends AccountReportFilters {
    static template = "account_reports.MulticurrencyRevaluationReportFilters";

    //------------------------------------------------------------------------------------------------------------------
    // Custom filters
    //------------------------------------------------------------------------------------------------------------------
    async filterCurrency(currency) {
        currency.selected = !currency.selected;

        this.controller.options.currencies_selected = parseInt(currency.id);
        this.controller.options.currencies_selected_name = currency.name;

        await this.controller.reload('currencies', this.controller.options);
    }
}

AccountReport.registerCustomComponent(MulticurrencyRevaluationReportFilters);
