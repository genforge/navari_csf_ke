// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("New Item Price", {
	refresh(frm) {
        frm.set_query("new_item_price", function () {
            return {
              filters: {
                selling: 1,
              },
            };
          });
	},
});
