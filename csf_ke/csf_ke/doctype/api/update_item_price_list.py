import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance
import time
from datetime import datetime, date


def update_item_prices(doc, method):
    """
    Main function triggered on a specific document event e.g., on_submit.
    Params: `doc` and `method`
    For each item in the document, retrieve the price list
    If a price list exists, process it else create and process a new price list
    """

    if doc.doctype == "Purchase Invoice" and not doc.update_stock:
        return

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
    """
    Update the item price based on predefined margin details
    Params: `item` and `price_list`
    Check if there are margin details for the price list
    If margin details exist, calculate the new rate
    Update the item price with the new rate
    """

    if frappe.db.exists("Selling Item Price Margin", {"selling_price": price_list}):
        margin_details = get_margin_details(price_list)
        if margin_details:
            new_rate = calculate_new_rate(item.item_code, margin_details)
            update_item_price(item.item_code, price_list, new_rate)


def get_margin_details(price_list):
    """
    Get the margin details for the price list
    Params: `price_list`
    Check if there are margin details for the price list
    If margin details exist, return the details
    Else return None
    """

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
        "warehouse": frappe.db.get_value(
            "Selling Item Price Margin", {"selling_price": price_list}, "warehouse"
        ),
    }
    return margin_details if all(margin_details.values()) else None


def calculate_new_rate(item_code, margin_details):
    """
    Calculate the new rate based on the margin details
    Params: `item_code` and `margin_details`
    Check if the margin based on is buying price
    If buying price, retrieve the buying price and apply the margin
    Check if the margin based on is valuation rate
    If valuation rate, retrieve the valuation rate and apply the margin
    Return the new rate
    """

    margin_based_on = margin_details["margin_based_on"]
    margin_type = margin_details["margin_type"]
    margin_percentage_or_amount = margin_details["margin_percentage_or_amount"]
    warehouse = margin_details["warehouse"]
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
            warehouse=warehouse,
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
    """
    Update the item price with the new rate checking for batch number and valid dates
    Params: `item_code`, `price_list` and `new_rate`
    Retrieve the name of the item price
    Check for batch number and valid dates
    If batch number exists, throw an error
    If `valid_upto` is in the past, throw an error
    If `valid_from` is in the future, throw an error
    If none of the conditions are met, update the item price with the new rate
    """

    item_price_name = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list, "selling": 1},
        "name",
    )

    # Check for batch number and valid dates
    batch_no = frappe.db.get_value("Item Price", item_price_name, "batch_no")
    valid_from = frappe.db.get_value("Item Price", item_price_name, "valid_from")
    valid_upto = frappe.db.get_value("Item Price", item_price_name, "valid_upto")
    old_rate = frappe.db.get_value("Item Price", item_price_name, "price_list_rate")

    current_date = datetime.now().date()

    if batch_no:
        frappe.throw("Cannot update batched price")

    if valid_upto:
        if isinstance(valid_upto, str):
            valid_upto = datetime.strptime(valid_upto, "%Y-%m-%d").date()
        if valid_upto < current_date:
            frappe.throw("Cannot update price after valid_upto")

    if valid_from:
        if isinstance(valid_from, str):
            valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
        if valid_from > current_date:
            frappe.throw("Cannot update price before valid_from")

    if new_rate <= old_rate:
        return

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
    """
    Create a new price list and process it
    Params: `item`
    Create a new Item Price document with the item details and desired price list.
    Wait for 5 seconds before further processing.
    Check if margin details exist for the new price list.
    If margin details exist, calculate the new rate using calculate_new_rate.
    Update the item price with the new rate using update_item_price.
    """
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
