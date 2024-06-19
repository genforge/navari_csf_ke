// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Selling Item Price Margin", {
  refresh(frm) {},
  onload: function (frm) {
    frm.set_query("selling_price", function () {
      return {
        filters: {
          selling: 1,
        },
      };
    });
    frm.set_query("buying_price", function () {
      return {
        filters: {
          buying: 1,
        },
      };
    });
  },
});
