/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WebsiteAppointment = publicWidget.Widget.extend({
    selector: '#appointment-detail',
    events: {
        'click #load_slots': '_onLoadSlots',
        'click .slot-btn': '_onSelectSlot',
    },

    async _onLoadSlots(ev) {
        ev.preventDefault();
        const serviceId = this.el.dataset.serviceId;
        const providerSelect = this.el.querySelector('#provider_id');
        const peopleSelect = this.el.querySelector('#num_people');
        const dateInput = this.el.querySelector('#date_from');
        if (!dateInput || !dateInput.value) {
            return;
        }
        const providerId = providerSelect ? providerSelect.value : null;
        const numPeople = peopleSelect ? parseInt(peopleSelect.value) : 1;
        const dateFrom = `${dateInput.value}T00:00:00`;

        const slots = await rpc(`/appointments/${serviceId}/slots`, {
            provider_id: providerId,
            date_from: dateFrom,
        });

        const container = this.el.querySelector('#slots');
        if (!container) return;
        container.innerHTML = '';
        for (const s of slots) {
            const col = document.createElement('div');
            col.className = 'col-auto';
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-primary slot-btn';
            btn.dataset.start = s.start;
            btn.dataset.available = s.available ?? '';
            const label = new Date(s.start).toLocaleString();
            const suffix = (typeof s.available === 'number') ? ` (${s.available} left)` : '';
            btn.textContent = label + suffix;
            col.appendChild(btn);
            container.appendChild(col);
        }

        const info = this.el.querySelector('#available_info');
        if (info) info.textContent = '';
    },

    _onSelectSlot(ev) {
        ev.preventDefault();
        const start = ev.currentTarget.dataset.start;
        const available = parseInt(ev.currentTarget.dataset.available || '0');
        const peopleSelect = this.el.querySelector('#num_people');
        const numPeople = peopleSelect ? parseInt(peopleSelect.value) : 1;

        const info = this.el.querySelector('#available_info');
        if (typeof available === 'number' && !Number.isNaN(available)) {
            if (info) {
                info.textContent = available >= numPeople
                    ? `Available seats: ${available}`
                    : `Not enough seats (${available} left)`;
            }
            if (available < numPeople) {
                return;
            }
        }
        const serviceId = this.el.dataset.serviceId;
        const providerSelect = this.el.querySelector('#provider_id');
        const providerId = providerSelect ? providerSelect.value : '';

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/appointments/${serviceId}/book`;

        const inputProvider = document.createElement('input');
        inputProvider.type = 'hidden';
        inputProvider.name = 'provider_id';
        inputProvider.value = providerId;
        form.appendChild(inputProvider);

        const inputStart = document.createElement('input');
        inputStart.type = 'hidden';
        inputStart.name = 'slot_start';
        inputStart.value = start;
        form.appendChild(inputStart);

        document.body.appendChild(form);
        form.submit();
    },
});

