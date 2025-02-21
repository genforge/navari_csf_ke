# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VATWithholding(Document):
	
	def before_insert(self):
		self.set_missing_values()
		

	def set_missing_values(self):
		self.currency = "KES"
		self.company = frappe.defaults.get_user_default("Company")
		self.customer = frappe.get_value("Customer", {'tax_id': self.withholder_pin}, "name")
		self.voucher_no = frappe.get_value("Sales Invoice", {'etr_invoice_number': self.invoice_no}, "name")
		self.withholding_account = frappe.get_value("Company", self.company, "default_debitors_withholding_account")

	def on_submit(self):
		if not self.withholding_account:
			frappe.throw("Please set the withholding account")
		self.create_journal_entry(self, "on_submit", submit_journal_entry=self.submit_journal_entry)

	@staticmethod
	def create_journal_entry(doc, method, *args, **kwargs):

		customer_receivable_account = frappe.get_value("Company", doc.company, "default_receivable_account")

		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"posting_date": doc.certificate_date,
			"company": doc.company,
			"voucher_type": "Journal Entry",
			"cheque_no": doc.wht_certificate_no,
			"cheque_date": doc.certificate_date,
			"remark": f"VAT Withholding Acknowledgment - Cert No: {doc.wht_certificate_no}",
			"accounts": [
				{
					"account": doc.withholding_account,
					"debit_in_account_currency": doc.vat_withholding_amount,
					"party_type": "",
					"party": "",
					"reference_type": "",
					"reference_name": "",
				},
				{
					"account": customer_receivable_account,
					"credit_in_account_currency": doc.vat_withholding_amount,
					"party_type": "Customer",
					"party": doc.customer,
				}
			]
		})

		je.insert()

		if kwargs.get("submit_journal_entry"):
			je.submit()
