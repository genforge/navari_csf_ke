# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SellingItemPriceMargin(Document):

    def before_save(self):

        self.check_date_overlap()

    def check_date_overlap(self):

        existing_records = frappe.get_all(
            "Selling Item Price Margin",
            filters={
                "docstatus": 1,
                "selling_price": self.selling_price,
                "name": ("!=", self.name),
                "start_date": ("<=", self.start_date),
                "end_date": (">=", self.end_date),
            },
            fields=["name", "selling_price", "start_date", "end_date"],
        )

        items = [item.item_code for item in self.items if self.items]
        
        for record in existing_records:

            sipm = frappe.get_doc("Selling Item Price Margin", record.name)

            for item in sipm.items:
                if item.item_code in items:
                    overlap_details = _("Selling price: {0} (From: {1}, To: {2})").format(
                        record["selling_price"], record["start_date"], record["end_date"]
                    )
                    frappe.throw(
                        _("Item '{0}' already exists in another record with the same selling price. Date overlap:\n{1}").format(
                            item.item_code, overlap_details
                        )
                    )
                else:
                    continue
