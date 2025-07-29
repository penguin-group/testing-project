/** @odoo-module */

import { ProjectTaskKanbanRenderer } from '@project/views/project_task_kanban/project_task_kanban_renderer';
import { patch } from '@web/core/utils/patch';
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(ProjectTaskKanbanRenderer.prototype, {
    setup() {
        super.setup();

        onWillStart(async () => {
            this.isProjectManager = await user.hasGroup('project.group_project_manager') 
                || await user.hasGroup('pisa_project.group_project_team_manager');
        });
    }
});