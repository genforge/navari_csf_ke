# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from .vat3_returns import fetch_invoices


class TestVAT3Returns(FrappeTestCase):
	
    def setUp(self):
        # test company
        self.company = "Test Company"
        self.currency = "KES"

        self.sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer",
            "company": self.company,
            "currency": self.currency,
            "party_account_currency": self.currency,
            "docstatus": 1,
            "posting_date": "2024-01-01",
            "sales_order": "Test Sales Order",
            "is_filed": 0,
            "grand_total": 1000
        }).insert()

        self.purchase_invoice = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": "Test Supplier",
            "company": self.company,
            "currency": self.currency,
            "party_account_currency": self.currency,
            "docstatus": 1,
            "posting_date": "2024-01-01",
            "is_filed": 0,
            "grand_total": 1000
        }).insert()

        self.vat3_returns = frappe.get_doc({
            "doctype": "VAT3 Returns",
            "company": self.company,
            "from_date": "2024-01-01",
            "to_date": "2024-01-31",
            "invoices": [
                {
                    "document_type": "Sales Invoice",
                    "invoice_number": self.sales_invoice.name,
                },
                {
                    "document_type": "Purchase Invoice",
                    "invoice_number": self.purchase_invoice.name,
                }
            ]
        }).insert()


    def tearDown(self):
        # Clean up test data
        frappe.delete_doc("VAT3 Returns", self.vat3_returns.name)
        frappe.delete_doc("Sales Invoice", self.sales_invoice.name)
        frappe.delete_doc("Purchase Invoice", self.purchase_invoice.name)


    def test_mark_invoices_as_filed_on_submit(self):
        self.vat3_returns.submit()

        self.sales_invoice.reload()
        self.assertEqual(self.sales_invoice.is_filed, 1, "Sales Invoice should be filed")

        self.purchase_invoice.reload()
        self.assertEqual(self.purchase_invoice.is_filed, 1, "Purchase Invoice should be filed")


    def test_mark_invoices_as_filed_on_cancel(self):
        self.vat3_returns.submit()
        self.vat3_returns.cancel()

        self.sales_invoice.reload()
        self.assertEqual(self.sales_invoice.is_filed, 0, "Sales Invoice should not be filed")

        self.purchase_invoice.reload()
        self.assertEqual(self.purchase_invoice.is_filed, 0, "Purchase Invoice should not be filed")


    def test_fetch_invoices(self):

        fetched_invoices = fetched_invoices(
            invoice_type="Sales Invoice",
            from_date="2024-01-01",
            to_date="2024-01-31",
            company=self.company
        )

        self.assertEqual(len(fetched_invoices), 1, "There should be one fetched Sales Invoice")
        self.assertEqual(fetched_invoices[0].get("name"), self.sales_invoice.name, "Fetched Sales Invoice should match the created Sales Invoice")

