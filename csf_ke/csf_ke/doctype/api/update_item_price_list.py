import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance
import time


def update_item_prices(doc, method):
    for item in doc.items:
        price_list = get_price_list(item.item_code)
        if price_list:
            process_existing_price_list(item, price_list)
        else:
            create_and_process_new_price_list(item)


def get_price_list(item_code):
    return frappe.db.get_value(
        "Item Price", {"item_code": item_code, "selling": 1}, "price_list"
    )


def process_existing_price_list(item, price_list):

    if frappe.db.exists("Selling Item Price Margin", {"selling_price": price_list}):
        margin_details = get_margin_details(price_list)
        if margin_details:
            new_rate = calculate_new_rate(item.item_code, margin_details)
            update_item_price(item.item_code, price_list, new_rate)


def get_margin_details(price_list):
    margin_details = {
        "margin_based_on": frappe.db.get_value(
            "Selling Item Price Margin",
            {"selling_price": price_list},
            "margin_based_on",
        ),
        "margin_type": frappe.db.get_value(
            "Selling Item Price Margin", {"selling_price": price_list}, "margin_type"
        ),
        "margin_percentage_or_amount": frappe.db.get_value(
            "Selling Item Price Margin",
            {"selling_price": price_list},
            "margin_percentage_or_amount",
        ),
    }
    return margin_details if all(margin_details.values()) else None


def calculate_new_rate(item_code, margin_details):
    margin_based_on = margin_details["margin_based_on"]
    margin_type = margin_details["margin_type"]
    margin_percentage_or_amount = margin_details["margin_percentage_or_amount"]
    rate = 0

    if margin_based_on == "Buying Price":
        buying_price = frappe.db.get_value(
            "Item Price", {"item_code": item_code, "buying": 1}, "price_list_rate"
        )
        if buying_price is not None:
            rate = apply_margin(buying_price, margin_type, margin_percentage_or_amount)
    elif margin_based_on == "Valuation Rate":
        valuation_rate = get_valuation_rate(
            item_code,
            warehouse="Stores - CKD",
            with_valuation_rate=True,
            with_serial_no=False,
        )
        if valuation_rate is not None:
            rate = apply_margin(
                valuation_rate, margin_type, margin_percentage_or_amount
            )

    return rate


def apply_margin(base_rate, margin_type, margin_value):
    if margin_type == "Percentage":
        return base_rate + (base_rate * margin_value / 100)
    else:
        return base_rate + margin_value


def update_item_price(item_code, price_list, new_rate):
    item_price_name = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list, "selling": 1},
        "name",
    )
    if item_price_name:
        try:
            frappe.db.set_value(
                "Item Price", item_price_name, "price_list_rate", new_rate
            )

        except Exception as e:
            frappe.log_error(f"Error updating Item Price: {str(e)}")
            frappe.throw(f"Error when updating Item Price: {e}")
    else:
        frappe.log_error(f"Error updating Item Price: {str(e)}")
        frappe.throw(
            f"Item Price not found for item {item_code} and price list {price_list}"
        )


def create_and_process_new_price_list(item):
    new_price_list_doc = frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item.item_code,
            "price_list": "Standard Selling",  # Specify your desired price list name
            "selling": 1,
            "price_list_rate": item.rate,  # Assuming 'rate' is the price you want to set
        }
    )

    new_price_list_doc.insert()

    time.sleep(5)  # Wait for 5 seconds before processing

    if frappe.db.exists(
        "Selling Item Price Margin", {"selling_price": new_price_list_doc.price_list}
    ):
        margin_details = get_margin_details(new_price_list_doc.price_list)
        if margin_details:
            new_rate = calculate_new_rate(item.item_code, margin_details)
            update_item_price(item.item_code, new_price_list_doc.price_list, new_rate)


@frappe.whitelist()
def get_valuation_rate(
    item_code,
    warehouse,
    posting_date=None,
    posting_time=None,
    with_valuation_rate=True,
    with_serial_no=False,
):
    stock_balance = get_stock_balance(
        item_code=item_code,
        warehouse=warehouse,
        posting_date=posting_date,
        posting_time=posting_time,
        with_valuation_rate=with_valuation_rate,
        with_serial_no=with_serial_no,
    )

    if isinstance(stock_balance, tuple):
        # Convert tuple to dictionary
        dictionary_data = {index: value for index, value in enumerate(stock_balance)}
        # Retrieve valuation rate from dictionary if it exists
        valuation_rate = dictionary_data.get(1)
        if valuation_rate is not None:
            # Return only the valuation rate
            return valuation_rate
        else:
            frappe.throw("Valuation rate not found in stock balance")
    else:
        frappe.throw("Invalid stock balance format")
