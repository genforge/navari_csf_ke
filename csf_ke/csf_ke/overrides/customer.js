frappe.ui.form.on("Customer", {
  refresh: function (frm) {
    set_kra_pin_required(frm);
  },
});

function set_kra_pin_required(frm) {
  if (!frm.doc.customer_group) return;

  frappe.call({
    method: "frappe.client.get_value",
    args: {
      doctype: "Customer Group",
      filters: { name: frm.doc.customer_group },
      fieldname: "custom_is_kra_pin_mandatory",
    },
    callback: function (r) {
      frm.set_df_property(
        "tax_id",
        "reqd",
        !!(r.message && r.message.custom_is_kra_pin_mandatory)
      );
    },
  });
}
