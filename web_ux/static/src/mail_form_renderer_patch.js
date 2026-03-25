/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";

patch(FormRenderer.prototype, {
    mailLayout(hasAttachmentContainer) {
        const chatterPosition = session.chatter_position || "auto";
        
        // If mail module is not installed/active, return NONE
        if (!this.mailStore) {
            return "NONE";
        }

        const xxl = this.uiService.size >= SIZES.XXL;
        const hasFile = this.hasFile ? this.hasFile() : false;
        const hasExternalWindow = this.mailPopoutService?.externalWindow;

        if (chatterPosition === "down") {
            // Force chatter below regardless of screen size
            if (hasExternalWindow && hasFile && hasAttachmentContainer) {
                return "EXTERNAL_COMBO";
            }
            return "BOTTOM_CHATTER";
        }
        
        if (chatterPosition === "aside") {
            // Force chatter beside regardless of screen size
            if (hasExternalWindow && hasFile && hasAttachmentContainer) {
                return "EXTERNAL_COMBO_XXL";
            }
            if (hasAttachmentContainer && hasFile) {
                return "COMBO";
            }
            return "SIDE_CHATTER";
        }

        // Auto mode - use default screen-size based logic
        if (hasExternalWindow && hasFile && hasAttachmentContainer) {
            return xxl ? "EXTERNAL_COMBO_XXL" : "EXTERNAL_COMBO";
        }
        if (xxl) {
            return hasAttachmentContainer && hasFile ? "COMBO" : "SIDE_CHATTER";
        }
        return "BOTTOM_CHATTER";
    },
});
