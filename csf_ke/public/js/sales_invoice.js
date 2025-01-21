frappe.ui.form.on("Sales Invoice Item", {
    item_code: function (frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        
        if (child.item_code) {
            frappe.call({
                method: "csf_ke.csf_ke.utils.get_tims_hscode.get_tims_hscode_for_item",
                args: {
                    item_code: child.item_code,
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "tims_hscode", r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, "tims_hscode", null);
                        // frappe.msgprint({
                        //     title: __("HS Code Missing"),
                        //     message: __("HS Code is not set for the selected item."),
                        //     indicator: "orange",
                        // });
                    }
                },
            });
        } else {
            frappe.model.set_value(cdt, cdn, "tims_hscode", null);
        }
    },
});
