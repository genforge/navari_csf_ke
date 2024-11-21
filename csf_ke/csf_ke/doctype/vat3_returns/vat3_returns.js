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
 	from_date: function(frm){
 	    if (frm.doc.from_date) {
 	        let fromDate = new Date(frm.doc.from_date);
 	        let endOfMonth = new Date(fromDate.getFullYear(), fromDate.getMonth() + 1, 0);
 	        frm.set_value('to_date', endOfMonth.toISOString().split('T')[0]);
 	    }
 	},
    fetch_invoices: function(frm) {
        frappe.call({
            method: 'fetch_invoices',
            doc: frm.doc,
            args: {
                invoice_type: frm.doc.selling ? "Sales Invoice" : "Purchase Invoice",
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company
            },
            callback: function(r) {
                frm.refresh_field('invoices');
            },
            error: function(err) {
                frappe.msgprint(__('There was an error fetching invoices.'));
            }
        });
    },
 });
 