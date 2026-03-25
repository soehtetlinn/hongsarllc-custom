/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { session } from "@web/session";
import { onMounted, onPatched } from "@odoo/owl";

patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.stickyColumnsCount = Math.max(0, parseInt(session.list_sticky_columns, 10) || 0);

        const updateStickyWidths = () => this._updateStickyColumnWidths();
        onMounted(updateStickyWidths);
        onPatched(updateStickyWidths);
    },
    get hasStickyColumns() {
        return this.stickyColumnsCount > 0;
    },
    _updateStickyColumnWidths() {
        if (!this.hasStickyColumns || !this.tableRef?.el) {
            return;
        }
        const table = this.tableRef.el;
        const headerCells = table.querySelectorAll("thead tr:first-child th.o_sticky_column");
        headerCells.forEach((cell, index) => {
            const width = cell.offsetWidth;
            table.style.setProperty(`--sticky-col-${index}-width`, `${width}px`);
        });
    },
    getColumnClass(column) {
        const result = super.getColumnClass(column);
        if (!this.hasStickyColumns) {
            return result;
        }
        const index = this.columns.findIndex((c) => c.id === column.id && c.name === column.name);
        if (index >= 0 && index < this.stickyColumnsCount) {
            return `${result} o_sticky_column o_sticky_column_${index}`;
        }
        return result;
    },
    getCellClass(column, record) {
        const result = super.getCellClass(column, record);
        if (!this.hasStickyColumns) {
            return result;
        }
        const index = this.columns.findIndex((c) => c.id === column.id && c.name === column.name);
        if (index >= 0 && index < this.stickyColumnsCount) {
            return `${result} o_sticky_column o_sticky_column_${index}`;
        }
        return result;
    },
});
