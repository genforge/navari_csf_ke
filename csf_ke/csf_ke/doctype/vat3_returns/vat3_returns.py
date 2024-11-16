# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VAT3Returns(Document):

	def validate(self):
		pass

	def on_submit(self):
		self.mark_invoices_as_filed(is_filed=1)

	def on_cancel(self):
		self.mark_invoices_as_filed(is_filed=0)

	def mark_invoices_as_filed(self, is_filed):

		doctype_map = {
			"Sales Invoice": "Sales Invoice",
			"Purchase Invoice": "Purchase Invoice",
		}

		for invoice in self.invoices:
			if invoice.document_type in doctype_map:
				invoice_doc = frappe.get_doc(doctype_map[invoice.document_type], invoice.invoice_number)
				invoice_doc.is_filed = is_filed
				invoice_doc.save()


@frappe.whitelist()
def fetch_invoices(invoice_type, from_date, to_date, company):
	if invoice_type == "Sales Invoice":
		fields = ["name", "posting_date", "total", "tax_id", "etr_serial_number", "customer"]
	elif invoice_type == "Purchase Invoice":
		fields = ["name", "posting_date", "total", "tax_id", "etr_invoice_number", "supplier"]

	invoices =  frappe.get_all(
		invoice_type,
		filters={
			"docstatus": 1,
			"posting_date": ["between", [from_date, to_date]],
			"company": company,
			"is_filed": 0
		},
		fields=fields,
		order_by="posting_date desc"
	)

	return invoices
