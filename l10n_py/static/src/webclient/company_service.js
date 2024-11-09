/** @odoo-module **/

import { companyService as baseCompanyService } from "@web/webclient/company_service"

const originalStart = baseCompanyService.start;

baseCompanyService.start = async function(env, { user, router, action }) {
    const result = originalStart.call(this, env, { user, router, action });
    var in_paraguay = false;
    
    // Fetch in_paraguay result
    try {
        var in_paraguay = await env.services.orm.call("res.company", "in_paraguay", [false]);
    } catch (error) {
        console.error("Error fetching in_paraguay result:", error);
    }

    // Update the context with the awaited result
    user.updateContext({ in_paraguay: in_paraguay });

    return result;
};
