import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance
import time
from datetime import datetime, date

def update_item_prices(doc, method):
    if doc.doctype == "Purchase Invoice" and not doc.update_stock:
        return

    currency = doc.currency

    for item in doc.items:
        price_list = get_price_list(item.item_code, currency)
        if price_list:
            process_existing_price_list(item, price_list)
        else:
            create_and_process_new_price_list(item, currency)

def get_price_list(item_code, currency):
    price_list = frappe.db.get_value(
        "Item Price", {"item_code": item_code, "selling": 1, "currency": currency}, "price_list"
    )
    frappe.log_error(f"Fetched price list for item {item_code} with currency {currency}: {str(price_list)[:135]}")
    return price_list

def process_existing_price_list(item, price_list):
    margin_details = get_margin_details(price_list)
    if margin_details:
        new_rate = calculate_new_rate(item.item_code, margin_details)
        update_item_price(item.item_code, price_list, new_rate, item.uom)
    else:
        frappe.log_error(f"No margin details found for price list {str(price_list)[:135]}")

def get_margin_details(price_list):
    margin_details = frappe.db.get_value(
        "Selling Item Price Margin",
        {"selling_price": price_list},
        ["margin_based_on", "margin_type", "margin_percentage_or_amount", "buying_price"],
        as_dict=True,
    )
    return margin_details if margin_details and all(margin_details.values()) else None

def calculate_new_rate(item_code, margin_details):
    margin_based_on = margin_details["margin_based_on"]
    margin_type = margin_details["margin_type"]
    margin_percentage_or_amount = margin_details["margin_percentage_or_amount"]
    buying_price = margin_details["buying_price"]
    rate = 0

    if margin_based_on == "Buying Price":
        filters = {"item_code": item_code, "buying": 1, "price_list": buying_price}
        buying_price_rate = frappe.db.get_value("Item Price", filters, "price_list_rate")

        # Fetch the buying price from the item
        item_buying_rate = frappe.db.get_value("Item", {"item_code": item_code}, "last_purchase_rate")

        # Use the higher rate
        if item_buying_rate and buying_price_rate:
            higher_rate = max(item_buying_rate, buying_price_rate)
        elif item_buying_rate:
            higher_rate = item_buying_rate
        elif buying_price_rate:
            higher_rate = buying_price_rate
        else:
            frappe.log_error(f"No buying price found for item {item_code} and price list {str(buying_price)[:135]}")
            return 0

        rate = apply_margin(higher_rate, margin_type, margin_percentage_or_amount)
    
    return rate

def apply_margin(base_rate, margin_type, margin_value):
    if margin_type == "Percentage":
        return base_rate + (base_rate * margin_value / 100)
    else:
        return base_rate + margin_value

def update_item_price(item_code, price_list, new_rate, stock_uom=None, currency=None):
    def update_rate(item_price_name, new_rate):
        batch_no = frappe.db.get_value("Item Price", item_price_name, "batch_no")
        valid_from = frappe.db.get_value("Item Price", item_price_name, "valid_from")
        valid_upto = frappe.db.get_value("Item Price", item_price_name, "valid_upto")
        item_uom = frappe.db.get_value("Item Price", item_price_name, "uom")
        old_rate = frappe.db.get_value("Item Price", item_price_name, "price_list_rate")

        current_date = datetime.now().date()

        if batch_no:
            return

        if valid_upto:
            if isinstance(valid_upto, str):
                valid_upto = datetime.strptime(valid_upto, "%Y-%m-%d").date()
            if valid_upto < current_date:
                return

        if valid_from:
            if isinstance(valid_from, str):
                valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
            if valid_from > current_date:
                return

        if new_rate <= old_rate:
            return

        try:
            frappe.db.set_value(
                "Item Price", item_price_name, "price_list_rate", new_rate
            )
        except Exception as e:
            frappe.log_error(f"Error updating Item Price {item_price_name}: {str(e)[:135]}")

    filters = {
        "item_code": item_code,
        "price_list": price_list,
        "selling": 1,
    }

    item_prices = frappe.get_list(
        "Item Price",
        filters=filters,
        fields=["name"],
    )


    item = frappe.get_doc("Item", item_code)

    if item_prices:
        for item_price in item_prices:
            update_rate(item_price["name"], new_rate)
    else:
        try:
            new_item_price_doc = frappe.get_doc(
                {
                    "doctype": "Item Price",
                    "item_code": item_code,
                    "price_list": price_list,
                    "selling": 1,
                    "price_list_rate": new_rate,
                    "uom": item.uom,
                }
            )
            new_item_price_doc.insert()
        except Exception as e:
            frappe.log_error(f"Error creating new Item Price for item {item_code}: {str(e)[:135]}")

def create_and_process_new_price_list(item, currency):
    new_item_price = frappe.db.get_single_value("New Item Price", "new_item_price")

    new_price_list_doc = frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item.item_code,
            "uom": item.uom,
            "price_list": new_item_price,
            "selling": 1,
            "price_list_rate": item.rate,
            "currency": currency,
        }
    )

    try:
        new_price_list_doc.insert()
    except Exception as e:
        frappe.log_error(f"Error creating new price list for item {item.item_code}: {str(e)[:135]}")
        return

    if frappe.db.exists(
        "Selling Item Price Margin", {"selling_price": new_price_list_doc.price_list}
    ):
        margin_details = get_margin_details(new_price_list_doc.price_list)
        if margin_details:
            new_rate = calculate_new_rate(item.item_code, margin_details)
            update_item_price(
                item.item_code,
                new_price_list_doc.price_list,
                new_rate,
            )
        else:
            frappe.log_error(f"No margin details found for new price list {str(new_price_list_doc.price_list)[:135]}")
