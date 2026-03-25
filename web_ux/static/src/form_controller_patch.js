/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

patch(FormController.prototype, {
    get className() {
        const result = super.className;
        const chatterPosition = session.chatter_position || "auto";
        const { size } = this.ui;

        if (chatterPosition === "down") {
            result.o_xxl_form_view = false;
            result["o_xxl_form_view h-100"] = false;
        } else if (chatterPosition === "aside" && !this.env.inDialog && size < SIZES.XXL) {
            result["o_xxl_form_view h-100"] = true;
            result.o_xxs_form_view = false;
        }
        return result;
    },
});
