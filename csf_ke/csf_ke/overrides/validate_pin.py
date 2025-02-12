import frappe
import re
from frappe.model.document import Document

def validate_pin(doc: Document) -> None:
    if getattr(doc, "customer_group", None):
        is_kra_mandatory = frappe.get_value(
            "Customer Group", doc.customer_group, "custom_is_kra_pin_mandatory"
        )
        if is_kra_mandatory and not getattr(doc, "tax_id", None):
            frappe.throw("KRA PIN is mandatory for this customer group.")

    if getattr(doc, "tax_id", None):
        pattern = r"^[A-Z]\d{9}[A-Z]$"
        if not re.match(pattern, doc.tax_id):
            frappe.throw("Invalid KRA PIN format. Expected A123456789B.")

        company = frappe.defaults.get_defaults().get("company")
        if not company:
            companies = frappe.get_all("Company", {}, ["name"], limit=1)
            company = companies[0].name if companies else None

        if company:
            company_tax_id = frappe.get_value("Company", company, "tax_id")
            if company_tax_id and company_tax_id == doc.tax_id:
                frappe.throw("Customer KRA PIN cannot match Company Tax ID.")
