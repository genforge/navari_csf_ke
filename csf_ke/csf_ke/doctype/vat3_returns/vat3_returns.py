# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VAT3Returns(Document):

    def validate(self):
        pass

    def on_submit(self):
        pass

@frappe.whitelist()
def fetch_invoices(invoice_type, from_date, to_date, company):

    invoices =  frappe.get_all(
        invoice_type,
        filters={
            "docstatus": 1,
            "posting_date": ["between", [from_date, to_date]],
            "company": company, 
            "is_filed": 0
        },
        fields=["name", "grand_total"],
        order_by="posting_date desc"
    )

    return invoices
