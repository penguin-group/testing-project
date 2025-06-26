/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class CertificatePortalForm extends Component {
    static template = "completion_certificates.CertificatePortalForm";
    static props = {
        csrfToken: String,
        partner: Object,
        purchaseOrders: Array,
    };

    setup() {
        this.state = useState({
            selectedPO: null,
            purchaseOrderLines: [],
            certificateLines: [],
            nextLineIndex: 0,
        });
    }

    async onPurchaseOrderChange(ev) {
        const selectedPOId = ev.target.value;
        this.state.selectedPO = this.props.purchaseOrders.find(po => po.id == selectedPOId) || null;
        this.state.purchaseOrderLines = [];
        if (selectedPOId) {
            // Fetch purchase order lines via AJAX
            const result = await rpc("/my/certificate/get_po_products", {
                purchase_order_id: selectedPOId,
            });
            if (result.products) {
                this.state.purchaseOrderLines = result.products;
            }
        }
        this.state.certificateLines = []; // Reset lines when PO changes
    }

    onAddLine() {
        this.state.certificateLines.push({
            lineIndex: this.state.nextLineIndex,
            purchase_line_id: "",
            description: "",
            uom: "",
            qty_processed: "",
            qty_received: "",
            date_received: "",
        });
        this.state.nextLineIndex += 1;
    }

    onLineChange(ev) {
        const index = parseInt(ev.target.dataset.index, 10);
        const field = ev.target.name || 'purchase_line_id';
        const value = ev.target.value;
        this.state.certificateLines[index][field] = value;

        if (field === 'purchase_line_id') {
            // Find the selected purchase line in purchaseOrderLines
            const pol = this.state.purchaseOrderLines.find(
                l => String(l.purchase_line_id) === String(value)
            );
            this.state.certificateLines[index].uom = pol ? pol.uom : "";
            this.state.certificateLines[index].qty_processed = pol ? pol.qty_processed : "";
        }
    }

    onRemoveLine(ev) {
        const lineIndex = parseInt(ev.target.dataset.index, 10);
        const idx = this.state.certificateLines.findIndex(l => l.lineIndex === lineIndex);
        if (idx !== -1) {
            this.state.certificateLines.splice(idx, 1);
        }
    }

    async onFormSubmit(ev) {
        ev.preventDefault();

        // Gather form data
        const form = ev.target;
        const formData = new FormData(form);

        // Build the payload
        const payload = {
            name: formData.get("name"),
            date: formData.get("date"),
            purchase_order_id: formData.get("purchase_order_id"),
            certificate_lines: this.state.certificateLines.map(line => ({
                purchase_line_id: line.purchase_line_id,
                description: line.description,
                qty_received: line.qty_received,
                date_received: line.date_received,
            })),
        };

        // Send to server
        const result = await rpc("/my/certificate/create", payload);

        if (result && result.redirect_url) {
            window.location.href = result.redirect_url;
        } else if (result && result.error) {
            alert("Error: " + result.error);
        } else {
            alert("Unknown error occurred.");
        }
    }
}

registry.category("public_components").add("completion_certificates.CertificatePortalForm", CertificatePortalForm);
