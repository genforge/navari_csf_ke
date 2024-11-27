# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SellingItemPriceMargin(Document):

    def before_submit(self):

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
            fields=["selling_price", "start_date", "end_date"],
        )

        if existing_records:
            overlap_details = [
                _("Selling price: {0} (From: {1}, To: {2})").format(
                    rec["selling_price"], rec["start_date"], rec["end_date"]
                )
                for rec in existing_records
            ]
            frappe.throw(
                _("Date overlap exists for the same selling price with the following records:\n{0}")
                .format("\n".join(overlap_details))
            )
