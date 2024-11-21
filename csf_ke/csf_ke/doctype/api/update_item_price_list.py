import frappe
from frappe import _
from datetime import date

def update_item_prices(doc, method):
    """
    Update item prices based on the margins defined in Selling Item Price Margin
    when a Purchase Invoice is submitted and stock is updated.

    Args:
        doc (Document): The Purchase Invoice or Purchase Receipt document.
        method (str): The method triggering this function.
    """
    if doc.doctype == "Purchase Invoice" and not doc.update_stock:
        return

    currency = doc.currency
    price_list = doc.buying_price_list

    for item in doc.items:
        # Fetch margin entries based on the currency and buying price list
        margin_entries = get_margin_entries(currency, price_list)
        if not margin_entries:
            frappe.log_error(f"No margin entries found")
            return

        for margin_entry in margin_entries:
            selling_price_list = margin_entry['selling_price']
            buying_price = margin_entry['buying_price']

            # Fetch margin details for the selling price list
            margin_details = get_margin_details(selling_price_list)

            if margin_details:
                # Check if the item already has an item price for the selling price list
                existing_item_price = check_existing_item_price(item.item_code, selling_price_list, item.uom)

                # Update or create price list based on the fetched margins
                if existing_item_price:
                    # Validate batch_no and date range before updating
                    if not existing_item_price.get("batch_no") and validate_date_range(
                        existing_item_price.get("valid_from"),
                        existing_item_price.get("valid_upto")
                    ):
                        process_existing_price_list(item, selling_price_list, margin_details, existing_item_price['price_list_rate'])
                else:
                    create_and_process_new_price_list(item, selling_price_list, margin_details, currency)
            else:
                frappe.log_error(f"No margin details found for selling price list {selling_price_list}")

def get_margin_entries(currency, price_list):
    """
    Retrieve margin entries from Selling Item Price Margin where currency and buying price match.

    Args:
        currency (str): The currency of the Purchase Invoice.
        price_list (str): The buying price list associated with the Purchase Invoice.

    Returns:
        list: List of margin entries matching the criteria.
    """
    return frappe.db.get_all(
        "Selling Item Price Margin",
        filters={
            "currency": currency,
            "buying_price": price_list,
            "disabled": 0,
            "start_date": ["<=", date.today()],
            "end_date": [">=", date.today()]
        },
        fields=["selling_price", "buying_price"]
    )

def get_margin_details(selling_price_list):
    """
    Retrieve margin details for a given selling price list from Selling Item Price Margin.

    Args:
        selling_price_list (str): The selling price list to fetch margin details for.

    Returns:
        dict: Dictionary containing margin details or None if not found.
    """
    return frappe.db.get_value(
        "Selling Item Price Margin",
        {"selling_price": selling_price_list},
        ["margin_based_on", "margin_type", "margin_percentage_or_amount", "buying_price"],
        as_dict=True
    )

def check_existing_item_price(item_code, price_list, uom):
    """
    Check if the item has an existing price record for the specified price list and UOM.

    Args:
        item_code (str): The code of the item to check.
        price_list (str): The price list to check against.
        uom (str): The unit of measure for the item.

    Returns:
        dict: Existing item price record or None if not found.
    """
    existing_item_price = frappe.db.get_all(
        "Item Price",
        filters={"item_code": item_code, "price_list": price_list, "uom": uom},
        fields=["name", "price_list_rate", "batch_no", "valid_from", "valid_upto"],
        limit=1
    )
    return existing_item_price[0] if existing_item_price else None

def process_existing_price_list(item, selling_price_list, margin_details, existing_rate):
    """
    Update the existing item price list if the new rate is higher than the existing rate.

    Args:
        item (Document): The item document from the Purchase Invoice.
        selling_price_list (str): The selling price list to update.
        margin_details (dict): The margin details to use for rate calculation.
        existing_rate (float): The current rate of the existing item price.
    """
    buying_price_list = margin_details['buying_price']

    # Fetch the actual buying price rate
    buying_price_rate = frappe.db.get_value(
        "Item Price",
        {"price_list": buying_price_list, "item_code": item.item_code, "buying": 1},
        "price_list_rate"
    )

    if not buying_price_rate:
        frappe.log_error(f"Buying price rate not found for {buying_price_list} and item {item.item_code}")
        return

    # Update selling price if the new rate is higher
    if item.rate > buying_price_rate:
        new_rate = calculate_new_rate(item.rate, margin_details)
        if new_rate > existing_rate:
            update_item_price(item.item_code, selling_price_list, new_rate, item.uom)
        else:
            frappe.log_error(f"New rate is not higher for item {item.item_code}")
    else:
        frappe.log_error(f"Item rate is lower than the buying price for item {item.item_code}")

def create_and_process_new_price_list(item, selling_price_list, margin_details, currency):
    """
    Create a new item price record if none exists and apply the margins.

    Args:
        item (Document): The item document from the Purchase Invoice.
        selling_price_list (str): The selling price list to create.
        margin_details (dict): The margin details to use for rate calculation.
        currency (str): The currency of the Purchase Invoice.
    """
    new_rate = calculate_new_rate(item.rate, margin_details)

    try:
        new_item_price_doc = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": item.item_code,
            "price_list": selling_price_list,
            "selling": 1,
            "price_list_rate": new_rate,
            "uom": item.uom,
            "currency": currency
        })
        new_item_price_doc.insert()
    except Exception as e:
        frappe.log_error(f"Error creating new Item Price for item {item.item_code}: {str(e)[:135]}")

def calculate_new_rate(purchase_rate, margin_details):
    """
    Calculate the new rate based on the margin details.

    Args:
        purchase_rate (float): The purchase rate of the item.
        margin_details (dict): The margin details to use for rate calculation.

    Returns:
        float: The calculated new rate.
    """
    margin_based_on = margin_details["margin_based_on"]
    margin_type = margin_details["margin_type"]
    margin_value = margin_details["margin_percentage_or_amount"]

    if margin_based_on == "Buying Price":
        if margin_type == "Percentage":
            new_rate = purchase_rate + (purchase_rate * margin_value / 100)
        else:
            new_rate = purchase_rate + margin_value
        return new_rate
    return purchase_rate

def update_item_price(item_code, price_list, new_rate, uom):
    """
    Update the price of an existing item price record.

    Args:
        item_code (str): The code of the item to update.
        price_list (str): The price list to update.
        new_rate (float): The new rate to set.
        uom (str): The unit of measure for the item.
    """
    try:
        frappe.db.set_value(
            "Item Price",
            {"item_code": item_code, "price_list": price_list, "uom": uom},
            "price_list_rate",
            new_rate
        )
    except Exception as e:
        frappe.log_error(f"Error updating Item Price for {item_code}: {str(e)[:135]}")


def validate_date_range(valid_from, valid_to):
    """
    Validate if the current date falls within the valid_from and valid_to range.

    Args:
        valid_from (date): The starting validity date.
        valid_to (date): The ending validity date.

    Returns:
        bool: True if valid_from and valid_to are valid or not provided, False otherwise.
    """
    today = date.today()

    if valid_from and valid_to:
        return valid_from <= today <= valid_to
    elif valid_from:
        return valid_from <= today
    elif valid_to:
        return today <= valid_to
    return True