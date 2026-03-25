/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

patch(FormRenderer.prototype, {
    getFormDisplayClasses() {
        const chatterPosition = session.chatter_position || "auto";
        const xxl = this.uiService.size >= SIZES.XXL;

        if (chatterPosition === "down") {
            return "flex-column";
        }
        if (chatterPosition === "aside") {
            return "flex-nowrap h-100";
        }
        return xxl ? "flex-nowrap h-100" : "flex-column";
    },
});
