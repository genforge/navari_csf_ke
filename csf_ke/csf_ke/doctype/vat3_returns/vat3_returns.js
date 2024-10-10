// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

 frappe.ui.form.on("VAT3 Returns", {
 	buying: function(frm) {
 	    if (frm.doc.buying) {
 	        frm.set_value('selling', 0);
 	    }
 	},
 	selling: function(frm) {
 	    if (frm.doc.selling) {
 	        frm.set_value('buying', 0);
 	    }
 	},
    fetch_invoices: function(frm) {
        frappe.call({
            method: 'csf_ke.csf_ke.doctype.vat3_returns.vat3_returns.fetch_invoices',
            args: {
                buying: frm.doc.buying,
                selling: frm.doc.selling,
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company
            },
            callback: function(r) {

                if (r.message) {

                    frm.clear_table('vat3_returns_invoices');

                    r.message.forEach(function(invoice) {

                        let row = frm.add_child('vat3_returns_invoices');
                        row.document_type = frm.doc.selling ? "Sales Invoice" : "Purchase Invoice";
                        row.invoice_number = invoice.name;
                        row.invoice_date = invoice.posting_date;
                        row.invoice_amount = invoice.grand_total;
                });
                frm.refresh_field('vat3_returns_invoices');
                }
            }
        });
    },
 });
 