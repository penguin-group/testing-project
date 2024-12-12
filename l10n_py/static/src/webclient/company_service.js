/** @odoo-module **/

import { companyService as baseCompanyService } from "@web/webclient/company_service"
import { user } from "@web/core/user";

const originalStart = baseCompanyService.start;

baseCompanyService.start = async function(env, {router, action }) {
    const result = originalStart.call(this, env, {router, action });
    var in_paraguay = false;
    
    // Fetch in_paraguay result
    try {
        in_paraguay = await env.services.orm.call("res.company", "in_paraguay", [false]);
    } catch (error) {
        console.error("Error fetching in_paraguay result:", error);
    }

    // Update the context with the awaited result
    user.updateContext({ in_paraguay: in_paraguay });
    
    // Reload the menu  
    env.services.menu.reload();

    return result;
};
