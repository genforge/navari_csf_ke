import frappe

@frappe.whitelist()
def get_tims_hscode_for_item(item_code):

    item_tims_hscode = frappe.get_all(
        "Item Tax",
        filters={"parent": item_code, "parenttype": "Item"},
        fields=["tims_hscode"],
        limit_page_length=1,
    )

    if item_tims_hscode and item_tims_hscode[0].get("tims_hscode"):
        return item_tims_hscode[0]["tims_hscode"]
    
    return None 