/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormCompiler } from "@web/views/form/form_compiler";
import { SIZES } from "@web/core/ui/ui_service";

patch(FormCompiler.prototype, {
    compileForm(el, params) {
        const res = super.compileForm(...arguments);
        const sheetNode = el.querySelector("sheet");
        if (!sheetNode) {
            return res;
        }
        const form = res.querySelector(".o_form_renderer");
        if (!form) {
            return res;
        }
        const attfClass = form.getAttribute("t-attf-class");
        if (attfClass) {
            const defaultDisplayClasses = `{{ __comp__.uiService.size < ${SIZES.XXL} ? "flex-column" : "flex-nowrap h-100" }}`;
            const customDisplayClasses = "{{ __comp__.getFormDisplayClasses ? __comp__.getFormDisplayClasses() : (__comp__.uiService.size < 6 ? \"flex-column\" : \"flex-nowrap h-100\") }}";
            form.setAttribute(
                "t-attf-class",
                attfClass.replace(defaultDisplayClasses, customDisplayClasses)
            );
        }
        return res;
    },
});
