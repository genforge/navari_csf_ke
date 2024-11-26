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

    def get_tax_rate(self, item, doc):
        tax_rate = 0

        if item.get("item_tax_template"):
            try:
                tax_template = frappe.get_doc("Item Tax Template", item.get("item_tax_template"))
                if tax_template.taxes:
                    return tax_template.taxes[0].tax_rate
            except frappe.DoesNotExistError:
                frappe.log_error(
                    _("Item Tax Template {0} does not exist").format(item.get("item_tax_template")),
                )

            except Exception as e:
                frappe.log_error(e, "Error fetching tax rate for item {0}".format(item.get("item_code")))

        if doc.get("taxes_and_charges"):
            try:
                tax_template = frappe.get_doc(
                    "Sales Taxes and Charges Template" 
                    if doc.doctype == "Sales Invoice" else "Purchase Taxes and Charges Template",
                    doc.taxes_and_charges
                )
                if tax_template.taxes:
                    return tax_template.taxes[0].rate  # Return the first rate from the template

            except frappe.DoesNotExistError:
                frappe.msgprint(_("The Taxes and Charges Template '{0}' does not exist.").format(doc.taxes_and_charges))

            except Exception as e:
                frappe.log_error(e, _("Error fetching tax rate from Taxes and Charges Template"))

        return tax_rate


    @frappe.whitelist()
    def fetch_invoices(self, invoice_type, from_date, to_date, company):

        etr_field = "etr_serial_number" if invoice_type == "Sales Invoice" else "etr_invoice_number"
        party_field = "customer" if invoice_type == "Sales Invoice" else "supplier"

        invoices =  frappe.get_all(
            invoice_type,
            filters={
                "docstatus": 1,
                "is_return": 0,
                "posting_date": ["between", [from_date, to_date]],
                "company": company,
                "is_filed": 0
            },
            fields=[
                "name", 
                "posting_date", 
                "total", 
                "tax_id", 
                etr_field,
                party_field
            ],
            order_by="posting_date desc"
        )

        if not invoices:
            frappe.msgprint(_("No invoices found for the selected criteria"))
            return

        # Populate the child table
        for invoice_data in invoices:

            invoice = frappe.get_doc(invoice_type, invoice_data.name)

            for item in invoice.items:

                tax_rate = self.get_tax_rate(item, invoice)

                self.append("invoices", {
                    "document_type": invoice_type,
                    "invoice_number": invoice.name,
                    "invoice_date": invoice.posting_date,
                    "taxable_value": item.net_amount,
                    "pin_number": invoice.tax_id,
                    "tax_rate": tax_rate,
                    "etr_serial_number": invoice.get(etr_field),
                    "supplier_name": invoice.get(party_field),
                })

        frappe.msgprint(_("Invoices fetched successfully"))
