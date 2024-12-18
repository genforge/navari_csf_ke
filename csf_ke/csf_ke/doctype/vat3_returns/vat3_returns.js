// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

 frappe.ui.form.on("VAT3 Returns", {
 	from_date: function(frm){
 	    if (frm.doc.from_date) {
 	        let fromDate = new Date(frm.doc.from_date);
 	        let endOfMonth = new Date(fromDate.getFullYear(), fromDate.getMonth() + 1, 0);
 	        frm.set_value('to_date', endOfMonth.toISOString().split('T')[0]);
 	    }
 	},
    fetch_invoices: function(frm) {

        frm.set_df_property('fetch_invoices', 'disabled', true);
        
        frappe.dom.freeze();

        frm.clear_table('invoices');

        frappe.call({
            method: 'fetch_invoices',
            doc: frm.doc,
            args: {
                invoice_type: frm.doc.return_type == "Selling" ? "Sales Invoice" : "Purchase Invoice",
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                company: frm.doc.company,
                tax_template: frm.doc.tax_template || null
            },
            callback: function(r) {
                frm.refresh_field('invoices');

                frm.set_df_property('fetch_invoices', 'disabled', false);

                frappe.dom.unfreeze();

            },
            error: function(err) {
                frappe.msgprint(__('There was an error fetching invoices.'));

                frm.set_df_property('fetch_invoices', 'disabled', false);

                frappe.dom.unfreeze();
            }
        });
    },
 });
 