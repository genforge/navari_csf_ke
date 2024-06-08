# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SellingItemPriceMargin(Document):

    def validate(self):

        # Check if the price list is of type selling
        if not frappe.get_value("Price List", self.selling_price, "selling") == 1:
            frappe.throw(_("Selling Price must be of type Selling"))

    def before_submit(self):

        self.check_date_overlap()

    def check_date_overlap(self):

        existing_records = frappe.get_all(
            "Selling Item Price Margin",
            filters={
                "docstatus": 1,
                "name": ("!=", self.name),
                "start_date": ("<=", self.start_date),
                "end_date": (">=", self.end_date),
            },
            fields=["name"],
        )

        if len(existing_records) > 0:
            frappe.throw(
                _("Date overlap exists between {0} adn {1}").format(
                    self.start_date, self.end_date
                )
            )
