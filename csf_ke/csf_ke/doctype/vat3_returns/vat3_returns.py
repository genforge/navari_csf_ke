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
def fetch_invoices(buying, selling, from_date, to_date, company):

    if buying == '1':
        invoice_type = "Purchase Invoice"
    elif selling == '1':
        invoice_type = "Sales Invoice"

    invoices =  frappe.get_all(
        invoice_type,
        filters={
            "docstatus": 1,
            "posting_date": ["between", [from_date, to_date]],
            "company": company, 
            "is_filed": 0
        },
        fields=["name", "grand_total"],
    )

    frappe.msgprint(str(invoices))

    return invoices
