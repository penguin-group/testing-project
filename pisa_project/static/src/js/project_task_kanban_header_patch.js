/** @odoo-module */

import { ProjectTaskKanbanHeader } from '@project/views/project_task_kanban/project_task_kanban_header';
import { patch } from '@web/core/utils/patch';
import { user } from "@web/core/user";

patch(ProjectTaskKanbanHeader.prototype, {
    async onWillStart() {
        if (this.props.list.isGroupedByStage) { // no need to check it if not grouped by stage
            this.isProjectManager = await user.hasGroup('project.group_project_manager') 
                || await user.hasGroup('pisa_project.group_project_team_manager');
        }
    }
});