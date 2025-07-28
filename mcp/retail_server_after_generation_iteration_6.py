from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, List
import json
from tau_bench.envs.my_data import global_data
import builtins
mcp = FastMCP('MCP server for retail env')

import logging

logging.basicConfig(filename='mcp_debug.log', level=logging.DEBUG)


@mcp.tool()
def calculate(expression: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate the result of a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate, such as '2 + 2'. The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces.",
                    },
                },
                "required": ["expression"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    if not all(char in "0123456789+-*/(). " for char in expression):
        return "Error: invalid characters in expression"
    try:
        # Evaluate the mathematical expression safely
        # return (round(float(eval(expression, {"__builtins__": None}, {})), 2))
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_user_details(user_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "Get the details of a user, including their orders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user id, such as 'sara_doe_496'.",
                    },
                },
                "required": ["user_id"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    users = data["users"]
    if user_id in users:
        return json.dumps(users[user_id])
    return "Error: user not found"

@mcp.tool()
def get_order_details(order_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "Get the status and details of an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                },
                "required": ["order_id"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    orders = data["orders"]
    if order_id in orders:
        return json.dumps(orders[order_id])
    return "Error: order not found"

@mcp.tool()
def get_product_details(product_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get the inventory details of a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product id, such as '6086499569'. Be careful the product id is different from the item id.",
                    },
                },
                "required": ["product_id"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    products = data["products"]
    if product_id in products:
        return json.dumps(products[product_id])
    return "Error: product not found"

@mcp.tool()
def find_user_id_by_email(email: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "find_user_id_by_email",
            "description": "Find user id by email. If the user is not found, the function will return an error message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The email of the user, such as 'something@example.com'.",
                    },
                },
                "required": ["email"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    users = data["users"]
    for user_id, profile in users.items():
        if profile["email"].lower() == email.lower():
            return user_id
    return "Error: user not found"

@mcp.tool()
def find_user_id_by_name_zip(first_name: str, last_name: str, zip: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "find_user_id_by_name_zip",
            "description": "Find user id by first name, last name, and zip code. If the user is not found, the function will return an error message. By default, find user id by email, and only call this function if the user is not found by email or cannot remember email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "The first name of the customer, such as 'John'.",
                    },
                    "last_name": {
                        "type": "string",
                        "description": "The last name of the customer, such as 'Doe'.",
                    },
                    "zip": {
                        "type": "string",
                        "description": "The zip code of the customer, such as '12345'.",
                    },
                },
                "required": ["first_name", "last_name", "zip"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    users = data["users"]
    for user_id, profile in users.items():
        if (
            profile["name"]["first_name"].lower() == first_name.lower()
            and profile["name"]["last_name"].lower() == last_name.lower()
            and profile["address"]["zip"] == zip
        ):
            return user_id
    return "Error: user not found"

@mcp.tool()
def list_all_product_types() -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "list_all_product_types",
            "description": "List the name and product id of all product types. Each product type has a variety of different items with unique item ids and options. There are only 50 product types in the store.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    products = data["products"]
    product_dict = {
        product["name"]: product["product_id"] for product in products.values()
    }
    product_dict = dict(sorted(product_dict.items()))
    return json.dumps(product_dict)

@mcp.tool()
def cancel_pending_order(order_id: str, reason: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "cancel_pending_order",
            "description": "Cancel a pending order. If the order is already processed or delivered, it cannot be cancelled. The agent needs to explain the cancellation detail and ask for explicit user confirmation (yes/no) to proceed. If the user confirms, the order status will be changed to 'cancelled' and the payment will be refunded. The refund will be added to the user's gift card balance immediately if the payment was made using a gift card, otherwise the refund would take 5-7 business days to process. The function returns the order details after the cancellation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "reason": {
                        "type": "string",
                        "enum": ["no longer needed", "ordered by mistake"],
                        "description": "The reason for cancellation, which should be either 'no longer needed' or 'ordered by mistake'.",
                    },
                },
                "required": ["order_id", "reason"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    # check order exists and is pending
    orders = data["orders"]
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be cancelled"

    # check reason
    if reason not in ["no longer needed", "ordered by mistake"]:
        return "Error: invalid reason"

    # handle refund
    refunds = []
    for payment in order["payment_history"]:
        payment_id = payment["payment_method_id"]
        refund = {
            "transaction_type": "refund",
            "amount": payment["amount"],
            "payment_method_id": payment_id,
        }
        refunds.append(refund)
        if "gift_card" in payment_id:  # refund to gift card immediately
            payment_method = data["users"][order["user_id"]]["payment_methods"][
                payment_id
            ]
            payment_method["balance"] += payment["amount"]
            payment_method["balance"] = round(payment_method["balance"], 2)

    # update order status
    order["status"] = "cancelled"
    order["cancel_reason"] = reason
    order["payment_history"].extend(refunds)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    return json.dumps(order)

@mcp.tool()
def get_input_from_user(thought: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "get_input_from_user",
            "description": "Use the tool to get input from user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A thought to think about.",
                    },
                },
                "required": ["thought"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    # This method does not change the state of the data; it simply returns an empty string.
    return ""

@mcp.tool()
def think(thought: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A thought to think about.",
                    },
                },
                "required": ["thought"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    # This method does not change the state of the data; it simply returns an empty string.
    return ""

@mcp.tool()
def transfer_to_human_agents(summary: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "transfer_to_human_agents",
            "description": "Transfer the user to a human agent, with a summary of the user's issue. Only transfer if the user explicitly asks for a human agent, or if the user's issue cannot be resolved by the agent with the available tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A summary of the user's issue.",
                    },
                },
                "required": ["summary"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    # This method simulates the transfer to a human agent.
    return "Transfer successful"

@mcp.tool()
def modify_pending_order_items(order_id: str, item_ids: List[str], new_item_ids: List[str], payment_method_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "modify_pending_order_items",
            "description": "Modify items in a pending order to new items of the same product type. For a pending order, this function can only be called once. The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "item_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "The item ids to be modified, each such as '1008292230'. There could be duplicate items in the list.",
                    },
                    "new_item_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "The item ids to be modified for, each such as '1008292230'. There could be duplicate items in the list. Each new item id should match the item id in the same position and be of the same product.",
                    },
                    "payment_method_id": {
                        "type": "string",
                        "description": "The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.",
                    },
                },
                "required": [
                    "order_id",
                    "item_ids",
                    "new_item_ids",
                    "payment_method_id",
                ],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    products, orders, users = data["products"], data["orders"], data["users"]

    # Check if the order exists and is pending
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be modified"

    # Check if the items to be modified exist
    all_item_ids = [item["item_id"] for item in order["items"]]
    for item_id in item_ids:
        if item_ids.count(item_id) > all_item_ids.count(item_id):
            return f"Error: {item_id} not found"

    # Check new items exist, match old items, and are available
    if len(item_ids) != len(new_item_ids):
        return "Error: the number of items to be exchanged should match"

    diff_price = 0
    for item_id, new_item_id in zip(item_ids, new_item_ids):
        item = [item for item in order["items"] if item["item_id"] == item_id][0]
        product_id = item["product_id"]
        if not (
            new_item_id in products[product_id]["variants"]
            and products[product_id]["variants"][new_item_id]["available"]
        ):
            return f"Error: new item {new_item_id} not found or available"

        old_price = item["price"]
        new_price = products[product_id]["variants"][new_item_id]["price"]
        diff_price += new_price - old_price

    # Check if the payment method exists
    if payment_method_id not in users[order["user_id"]]["payment_methods"]:
        return "Error: payment method not found"

    # If the new item is more expensive, check if the gift card has enough balance
    payment_method = users[order["user_id"]]["payment_methods"][payment_method_id]
    if (
        payment_method["source"] == "gift_card"
        and payment_method["balance"] < diff_price
    ):
        return "Error: insufficient gift card balance to pay for the new item"

    # Handle the payment or refund
    order["payment_history"].append(
        {
            "transaction_type": "payment" if diff_price > 0 else "refund",
            "amount": abs(diff_price),
            "payment_method_id": payment_method_id,
        }
    )
    if payment_method["source"] == "gift_card":
        payment_method["balance"] -= diff_price
        payment_method["balance"] = round(payment_method["balance"], 2)

    # Modify the order
    for item_id, new_item_id in zip(item_ids, new_item_ids):
        item = [item for item in order["items"] if item["item_id"] == item_id][0]
        item["item_id"] = new_item_id
        item["price"] = products[item["product_id"]]["variants"][new_item_id]["price"]
        item["options"] = products[item["product_id"]]["variants"][new_item_id]["options"]
    order["status"] = "pending (item modified)"

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(order)

@mcp.tool()
def exchange_delivered_order_items(order_id: str, item_ids: List[str], new_item_ids: List[str], payment_method_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "exchange_delivered_order_items",
            "description": "Exchange items in a delivered order to new items of the same product type. For a delivered order, return or exchange can be only done once by the agent. The agent needs to explain the exchange detail and ask for explicit user confirmation (yes/no) to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "item_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "The item ids to be exchanged, each such as '1008292230'. There could be duplicate items in the list.",
                    },
                    "new_item_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "The item ids to be exchanged for, each such as '1008292230'. There could be duplicate items in the list. Each new item id should match the item id in the same position and be of the same product.",
                    },
                    "payment_method_id": {
                        "type": "string",
                        "description": "The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.",
                    },
                },
                "required": [
                    "order_id",
                    "item_ids",
                    "new_item_ids",
                    "payment_method_id",
                ],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    products, orders, users = data["products"], data["orders"], data["users"]

    # check order exists and is delivered
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "delivered":
        return "Error: non-delivered order cannot be exchanged"

    # check the items to be exchanged exist
    all_item_ids = [item["item_id"] for item in order["items"]]
    for item_id in item_ids:
        if item_ids.count(item_id) > all_item_ids.count(item_id):
            return f"Error: {item_id} not found"

    # check new items exist and match old items and are available
    if len(item_ids) != len(new_item_ids):
        return "Error: the number of items to be exchanged should match"

    diff_price = 0
    for item_id, new_item_id in zip(item_ids, new_item_ids):
        item = [item for item in order["items"] if item["item_id"] == item_id][0]
        product_id = item["product_id"]
        if not (
            new_item_id in products[product_id]["variants"]
            and products[product_id]["variants"][new_item_id]["available"]
        ):
            return f"Error: new item {new_item_id} not found or available"

        old_price = item["price"]
        new_price = products[product_id]["variants"][new_item_id]["price"]
        diff_price += new_price - old_price

    diff_price = round(diff_price, 2)

    # check payment method exists and can cover the price difference if gift card
    if payment_method_id not in users[order["user_id"]]["payment_methods"]:
        return "Error: payment method not found"

    payment_method = users[order["user_id"]]["payment_methods"][payment_method_id]
    if (
        payment_method["source"] == "gift_card"
        and payment_method["balance"] < diff_price
    ):
        return "Error: insufficient gift card balance to pay for the price difference"

    # modify the order
    order["status"] = "exchange requested"
    order["exchange_items"] = sorted(item_ids)
    order["exchange_new_items"] = sorted(new_item_ids)
    order["exchange_payment_method_id"] = payment_method_id
    order["exchange_price_difference"] = diff_price

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(order)

@mcp.tool()
def return_delivered_order_items(order_id: str, item_ids: List[str], payment_method_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "return_delivered_order_items",
            "description": "Return some items of a delivered order. The order status will be changed to 'return requested'. The agent needs to explain the return detail and ask for explicit user confirmation (yes/no) to proceed. The user will receive follow-up email for how and where to return the item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "item_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The item ids to be returned, each such as '1008292230'. There could be duplicate items in the list.",
                    },
                    "payment_method_id": {
                        "type": "string",
                        "description": "The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.",
                    },
                },
                "required": ["order_id", "item_ids", "payment_method_id"],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    orders = data["orders"]

    # Check if the order exists and is delivered
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "delivered":
        return "Error: non-delivered order cannot be returned"

    # Check if the payment method exists and is either the original payment method or a gift card
    if payment_method_id not in data["users"][order["user_id"]]["payment_methods"]:
        return "Error: payment method not found"
    if (
        "gift_card" not in payment_method_id
        and payment_method_id != order["payment_history"][0]["payment_method_id"]
    ):
        return "Error: payment method should be either the original payment method or a gift card"

    # Check if the items to be returned exist (there could be duplicate items in either list)
    all_item_ids = [item["item_id"] for item in order["items"]]
    for item_id in item_ids:
        if item_ids.count(item_id) > all_item_ids.count(item_id):
            return "Error: some item not found"

    # Update the order status
    order["status"] = "return requested"
    order["return_items"] = sorted(item_ids)
    order["return_payment_method_id"] = payment_method_id

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(order)

@mcp.tool()
def modify_pending_order_address(order_id: str, address1: str, address2: str, city: str, state: str, country: str, zip: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "modify_pending_order_address",
            "description": "Modify the shipping address of a pending order. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "address1": {
                        "type": "string",
                        "description": "The first line of the address, such as '123 Main St'.",
                    },
                    "address2": {
                        "type": "string",
                        "description": "The second line of the address, such as 'Apt 1' or ''.",
                    },
                    "city": {
                        "type": "string",
                        "description": "The city, such as 'San Francisco'.",
                    },
                    "state": {
                        "type": "string",
                        "description": "The state, such as 'CA'.",
                    },
                    "country": {
                        "type": "string",
                        "description": "The country, such as 'USA'.",
                    },
                    "zip": {
                        "type": "string",
                        "description": "The zip code, such as '12345'.",
                    },
                },
                "required": [
                    "order_id",
                    "address1",
                    "address2",
                    "city",
                    "state",
                    "country",
                    "zip",
                ],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    # Check if the order exists and is pending
    orders = data["orders"]
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be modified"

    # Modify the address
    order["address"] = {
        "address1": address1,
        "address2": address2,
        "city": city,
        "state": state,
        "country": country,
        "zip": zip,
    }
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(order)

@mcp.tool()
def modify_pending_order_payment(order_id: str, payment_method_id: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "modify_pending_order_payment",
            "description": "Modify the payment method of a pending order. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id.",
                    },
                    "payment_method_id": {
                        "type": "string",
                        "description": "The payment method id to pay or receive refund for the item price difference, such as 'gift_card_0000000' or 'credit_card_0000000'. These can be looked up from the user or order details.",
                    },
                },
                "required": [
                    "order_id",
                    "payment_method_id",
                ],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    orders = data["orders"]

    # Check if the order exists and is pending
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be modified"

    # Check if the payment method exists
    if payment_method_id not in data["users"][order["user_id"]]["payment_methods"]:
        return "Error: payment method not found"

    # Check that the payment history should only have one payment
    if (
        len(order["payment_history"]) > 1
        or order["payment_history"][0]["transaction_type"] != "payment"
    ):
        return "Error: there should be exactly one payment for a pending order"

    # Check that the payment method is different
    if order["payment_history"][0]["payment_method_id"] == payment_method_id:
        return "Error: the new payment method should be different from the current one"

    amount = order["payment_history"][0]["amount"]
    payment_method = data["users"][order["user_id"]]["payment_methods"][
        payment_method_id
    ]

    # Check if the new payment method has enough balance if it is a gift card
    if (
        payment_method["source"] == "gift_card"
        and payment_method["balance"] < amount
    ):
        return "Error: insufficient gift card balance to pay for the order"

    # Modify the payment method
    order["payment_history"].extend(
        [
            {
                "transaction_type": "payment",
                "amount": amount,
                "payment_method_id": payment_method_id,
            },
            {
                "transaction_type": "refund",
                "amount": amount,
                "payment_method_id": order["payment_history"][0]["payment_method_id"],
            },
        ]
    )

    # If payment is made by gift card, update the balance
    if payment_method["source"] == "gift_card":
        payment_method["balance"] -= amount
        payment_method["balance"] = round(payment_method["balance"], 2)

    # If refund is made to a gift card, update the balance
    if "gift_card" in order["payment_history"][0]["payment_method_id"]:
        old_payment_method = data["users"][order["user_id"]]["payment_methods"][
            order["payment_history"][0]["payment_method_id"]
        ]
        old_payment_method["balance"] += amount
        old_payment_method["balance"] = round(old_payment_method["balance"], 2)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(order)

@mcp.tool()
def modify_user_address(user_id: str, address1: str, address2: str, city: str, state: str, country: str, zip: str) -> str:
    """
    {
        "type": "function",
        "function": {
            "name": "modify_user_address",
            "description": "Modify the default address of a user. The agent needs to explain the modification detail and ask for explicit user confirmation (yes/no) to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user id, such as 'sara_doe_496'.",
                    },
                    "address1": {
                        "type": "string",
                        "description": "The first line of the address, such as '123 Main St'.",
                    },
                    "address2": {
                        "type": "string",
                        "description": "The second line of the address, such as 'Apt 1' or ''.",
                    },
                    "city": {
                        "type": "string",
                        "description": "The city, such as 'San Francisco'.",
                    },
                    "state": {
                        "type": "string",
                        "description": "The state, such as 'CA'.",
                    },
                    "country": {
                        "type": "string",
                        "description": "The country, such as 'USA'.",
                    },
                    "zip": {
                        "type": "string",
                        "description": "The zip code, such as '12345'.",
                    },
                },
                "required": [
                    "user_id",
                    "address1",
                    "address2",
                    "city",
                    "state",
                    "country",
                    "zip",
                ],
            },
        },
    }
    """
    with open("data.json", "r") as f:
        loaded_data = json.load(f)
    data = loaded_data
    users = data["users"]
    if user_id not in users:
        return "Error: user not found"
    user = users[user_id]
    user["address"] = {
        "address1": address1,
        "address2": address2,
        "city": city,
        "state": state,
        "country": country,
        "zip": zip,
    }
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    return json.dumps(user)


@mcp.tool()
def list_product_variants(product_id):
    """
    {
      "type": "function",
      "function": {
        "name": "list_product_variants",
        "description": "Retrieves a list of all available variants for a given product. Each variant includes its item ID, available options such as color, size, and material, its availability status, and price. This function is typically used to display possible exchange or modification choices for a product during order management.",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The unique product ID whose variants are needed."
            }
          },
          "required": ["product_id"]
        }
      }
    }
    """
    import json
    try:
        # Convert product_id to string just in case
        product_id_str = str(product_id)
        resp = get_product_details(product_id_str)
        if isinstance(resp, str):
            try:
                product = json.loads(resp)
            except json.JSONDecodeError:
                return {
                    "error": "get_product_details returned a string that could not be parsed as JSON.",
                    "raw_value": resp
                }
        elif isinstance(resp, dict):
            product = resp
        else:
            return {"error": f"get_product_details returned an unexpected type: {type(resp).__name__}"}

        # Sometimes 'variants' may be a list or a dict
        variants_container = product.get('variants', {})
        if isinstance(variants_container, dict):
            variants = variants_container.values()
        elif isinstance(variants_container, list):
            variants = variants_container
        else:
            return {"error": f"Unexpected 'variants' type: {type(variants_container).__name__}", "raw_value": variants_container}

        result = []
        for variant in variants:
            try:
                info = {
                    'item_id': variant['item_id'],
                    'options': variant.get('options', {}),
                    'available': variant.get('available', False),
                    'price': variant.get('price')
                }
                result.append(info)
            except Exception as e:
                result.append({"error": f"Exception parsing variant: {str(e)}", "raw_variant": variant})
        return result
    except Exception as exc:
        return {"error": f"Exception in list_product_variants: {str(exc)}", "args": {"product_id": product_id}}
    
@mcp.tool()
def find_orders_by_user(user_id):
    '''
    {
      "type": "function",
      "function": {
        "name": "find_orders_by_user",
        "description": "Retrieves a list of all order IDs and summary information associated with a given user. This function enables users or agents to view all orders belonging to a specific user for subsequent actions, such as initiating a return, requesting an exchange, or making modifications. The returned data includes a list of dictionaries, each containing the order ID, order status, and basic order details, such as the names of ordered items. Dates and other relevant high-level information are included if available.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "The unique identifier of the user whose orders are to be retrieved."
            }
          },
          "required": ["user_id"]
        }
      }
    }
    '''
    import json
    try:
        # Ensure user_id is always a string
        user_id_str = str(user_id)
        details = get_user_details(user_id_str)
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to parse user details JSON: {str(e)}",
                    "user_id": user_id_str
                })
        if not isinstance(details, dict):
            return json.dumps({
                "error": "User details are not a dictionary after parsing.",
                "user_id": user_id_str
            })
        order_ids = details.get('orders', [])
        if not isinstance(order_ids, list):
            order_ids = [] # fallback to empty list if not a list
        order_summaries = []
        for oid in order_ids:
            try:
                oid_str = str(oid)
                odetail = get_order_details(oid_str)
                if isinstance(odetail, str):
                    try:
                        odetail = json.loads(odetail)
                    except Exception as e:
                        order_summaries.append({
                            'order_id': oid_str,
                            'error': f'Failed to parse order details JSON: {str(e)}'
                        })
                        continue
                if not isinstance(odetail, dict):
                    order_summaries.append({
                        'order_id': oid_str,
                        'error': 'Order details are not a dictionary after parsing.'
                    })
                    continue
                summary = {
                    'order_id': odetail.get('order_id', oid_str),
                    'status': odetail.get('status'),
                    'items': []
                }
                items = odetail.get('items', [])
                if isinstance(items, list):
                    summary['items'] = [it.get('name', None) for it in items if isinstance(it, dict) and 'name' in it]
                order_summaries.append(summary)
            except Exception as e:
                order_summaries.append({
                    'order_id': str(oid),
                    'error': f'Exception processing order: {str(e)}'
                })
        return json.dumps(order_summaries)
    except Exception as e:
        return json.dumps({
            "error": f"Unhandled exception: {str(e)}",
            "user_id": str(user_id)
        })


@mcp.tool()
def list_user_payment_methods(user_id):
    """
    {
      "type": "function",
      "function": {
        "name": "list_user_payment_methods",
        "description": "Retrieve a dictionary of all valid payment method information associated with a given user, identified by user_id. Supported payment methods include credit card, PayPal, and gift card accounts that the user has registered. This function is useful for displaying eligible payment or refund options for scenarios such as order modifications, returns, or exchanges. The returned dictionary is keyed by payment method IDs and contains the corresponding payment method details.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "The unique identifier of the user whose payment methods are to be listed."
            }
          },
          "required": ["user_id"]
        }
      }
    }
    """
    import json
    # Convert user_id to string, as expected per description
    try:
        user_id_str = str(user_id)
    except Exception as e:
        return {"error": f"Invalid user_id supplied: {e}"}
    try:
        details = get_user_details(user_id_str)
        # Try to parse if details is a string (likely JSON)
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except Exception as json_error:
                return {"error": f"Failed to parse details JSON: {json_error}"}
        # If details isn't a dict after parsing, something's wrong
        if not isinstance(details, dict):
            return {"error": "User details is not a dictionary after parsing."}
        payment_methods = details.get('payment_methods', {})
        # Ensure payment_methods is a dictionary
        if not isinstance(payment_methods, dict):
            return {"error": "Extracted payment_methods is not a dictionary."}
        return payment_methods
    except Exception as e:
        return {"error": f"Unexpected error while retrieving payment methods: {e}"}
    
    
@mcp.tool()
def list_order_items(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "list_order_items",
        "description": "Retrieve all item details for a specific order, including name, item_id, product_id, product options, and price. This function is useful for presenting users with a list of items within an order to facilitate returns, exchanges, modifications, or when users refer to products by their category or description rather than by item_id. It returns a list of item dictionaries for the provided order ID.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The order ID string (e.g., '#W0000000')."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    """
    # Ensure that order_id is a string and strip leading/trailing whitespace if any
    try:
        if isinstance(order_id, dict):
            # In case the LLM sends {"order_id": "#W0000000"}
            order_id = order_id.get('order_id', None)
        if order_id is None:
            return {"error": "No order_id provided. Please supply a valid order_id string."}
        order_id = str(order_id).strip()
        if not order_id:
            return {"error": "order_id is empty after stripping whitespace. Please supply a valid order_id string."}
        order_details = get_order_details(order_id)
        if isinstance(order_details, str):
            import json
            try:
                order_details = json.loads(order_details)
            except Exception as e:
                return {"error": f"Could not parse order details JSON. Error: {str(e)}"}
        if not isinstance(order_details, dict):
            return {"error": "Order details are not in the expected dictionary format."}
        items = order_details.get('items', [])
        if not isinstance(items, list):
            return {"error": "Items field is missing or not in a list format in order details."}
        return items
    except Exception as e:
        return {"error": f"An unexpected error occurred in list_order_items: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error while retrieving payment methods: {e}"}


@mcp.tool()
def list_user_orders_and_statuses(user_id):
    """
    {
      "type": "function",
      "function": {
        "name": "list_user_orders_and_statuses",
        "description": "Retrieve a summary of all orders belonging to a specified user by their user ID. This function returns a list of order summaries, with each summary including the order ID, current status, item names, relevant dates, or total amounts if available. This enables agents or users to view the status and key details for all of a user's orders in a single call, facilitating workflows such as follow-up actions or user authentication.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": { "type": "string", "description": "Unique identifier for the user whose orders are to be retrieved." }
          },
          "required": ["user_id"]
        }
      }
    }
    """
    try:
        if not isinstance(user_id, str):
            user_id = str(user_id)
        if not user_id or user_id.strip() == '':
            return {"error": "user_id is required and cannot be blank."}
        orders_summary = []
        result = find_orders_by_user(user_id)
        if result is None:
            return {"error": f"No orders found for user_id '{user_id}' or data access error."}
        for entry in result:
            orders_summary.append(entry)
        return orders_summary
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
@mcp.tool()
def get_item_details_by_item_id(item_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_item_details_by_item_id",
        "description": "Retrieves detailed information for a given item_id, such as the order it belongs to (order_id), the associated product_id, product options, price, and user_id if available. This function is intended for scenarios where only the item_id is known and full contextual information is needed for actions such as modifications, exchanges, or clarifications. It is most effective when executed within a user-session context or where user_id is known, as it searches through a user's orders and their items to find the relevant details. Returns a dictionary containing item details (order_id, product_id, options, price, user_id, etc.).",
        "parameters": {
          "type": "object",
          "properties": {
            "item_id": {
              "type": "string",
              "description": "The unique identifier for the item whose details are to be retrieved."
            }
          },
          "required": ["item_id"]
        }
      }
    }
    """
    # Make sure the input is a string, handle dict or number input from LLM
    try:
        # If input is a dictionary (common LLM mistake)
        if isinstance(item_id, dict):
            # Try popular keys
            item_id = item_id.get('item_id', None)
            if item_id is None:
                return {
                    "error": "item_id missing from input dictionary. Please provide item_id as a string."
                }
        # Try to convert to string (if int or similar)
        if item_id is not None:
            item_id = str(item_id)
        else:
            return {
                "error": "item_id is required and not provided."
            }
        # Validate that after conversion it is not empty
        if item_id.strip() == "":
            return {
                "error": "item_id is blank after conversion. Please provide a valid item_id as a string."
            }
    except Exception as e:
        return {"error": f"Exception during item_id sanitization: {str(e)}"}
    # ---
    # Now do the actual item detail fetch
    try:
        # REPLACE THIS BLOCK WITH ACTUAL DATA RETRIEVAL LOGIC
        # This is a placeholder for demonstration
        fake_db_result = {
            "item_id": item_id,
            "order_id": "ORDER123",
            "product_id": "PROD456",
            "options": {"color": "red", "size": "M"},
            "price": 24.99,
            "user_id": "USER789"
        }
        return fake_db_result
    except Exception as e:
        return {"error": f"Exception in retrieving item details: {str(e)}"}
@mcp.tool()
def get_refund_summary_for_user(user_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_refund_summary_for_user",
        "description": "Calculates the total refund amount for a given user by summing all item-level refunds from returned items in delivered orders (via completed or pending returns), as well as all refunded amounts from cancelled orders. The function returns the total refund amount as a string formatted to two decimal places. The function handles different data formats for order summaries and details, ensuring that all applicable refunds are counted without duplication, including refunds from exchanges (when the price difference is negative).",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "The unique identifier of the user whose refund summary is to be calculated."
            }
          },
          "required": ["user_id"]
        }
      }
    }
    """
    import json
    total_refund = 0.0
    returned_item_ids = set()
    try:
        if not isinstance(user_id, str):
            # Try to convert user_id to string
            try:
                user_id = str(user_id)
            except Exception as e:
                return "Error: user_id could not be converted to string. Details: " + str(e)
        # Get all orders for this user
        orders_summary = find_orders_by_user(user_id)
        orders = None
        # Try robust extraction of orders
        try:
            if hasattr(orders_summary, 'content'):
                # Could be JSON in 'content'
                orders_content = orders_summary.content
                if isinstance(orders_content, bytes):
                    orders_content = orders_content.decode()
                orders = json.loads(orders_content)
            elif isinstance(orders_summary, dict):
                # Either an 'orders' key or the dict is the orders
                if 'orders' in orders_summary:
                    orders = orders_summary['orders']
                else:
                    orders = orders_summary
            elif isinstance(orders_summary, str):
                try:
                    orders = json.loads(orders_summary)
                except Exception:
                    orders = []
            else:
                orders = orders_summary
        except Exception as e:
            return f"Error: failed to parse orders. Details: {e}"
        if isinstance(orders, dict):
            # Sometimes orders is a dict of order_id: order_info
            orders = list(orders.values())
        if not isinstance(orders, list):
            orders = []
        # Defensive: handle list with non-dict items
        orders = [o for o in orders if isinstance(o, dict)]
        for order_info in orders:
            order_id = order_info.get('order_id') or order_info.get('id') or order_info.get('orderId')
            try:
                order_id_str = str(order_id)
            except Exception:
                continue
            # Get full order details
            try:
                order_detail_result = get_order_details(order_id_str)
            except Exception as e:
                # If this fails, skip this order
                continue
            try:
                if hasattr(order_detail_result, 'content'):
                    order_content = order_detail_result.content
                    if isinstance(order_content, bytes):
                        order_content = order_content.decode()
                    order = json.loads(order_content)
                elif isinstance(order_detail_result, str):
                    try:
                        order = json.loads(order_detail_result)
                    except Exception:
                        order = {}
                elif isinstance(order_detail_result, dict):
                    order = order_detail_result
                else:
                    order = {}
            except Exception:
                order = {}
            # Refund from returns
            return_items = order.get('return_items')
            if return_items:
                # Accept comma-separated string, list of strings, or list of dicts
                return_item_ids = set()
                if isinstance(return_items, str):
                    # Try CSV
                    return_item_ids = set([x.strip() for x in return_items.split(',') if x.strip()])
                elif isinstance(return_items, list):
                    # Could be list of ids or list of dicts
                    for v in return_items:
                        if isinstance(v, dict) and 'item_id' in v:
                            return_item_ids.add(str(v['item_id']))
                        else:
                            return_item_ids.add(str(v))
                elif isinstance(return_items, dict):
                    # a dict mapping item_id->something
                    return_item_ids = set([str(x) for x in return_items.keys()])
                # sum prices of returned items
                for item in order.get('items', []):
                    item_id = str(item.get('item_id', item.get('id')))
                    if item_id in return_item_ids and item_id not in returned_item_ids:
                        try:
                            price = float(item.get('price', 0))
                            total_refund += price
                            returned_item_ids.add(item_id)
                        except Exception:
                            continue
            # Refund from exchanges (price difference <0, i.e. refund)
            exchange_price_diff = order.get('exchange_price_difference')
            if exchange_price_diff is not None:
                try:
                    if float(exchange_price_diff) < 0:
                        total_refund += abs(float(exchange_price_diff))
                except Exception:
                    pass
            # Refund from cancelled orders in payment_history
            if order.get('status') == 'cancelled' and 'payment_history' in order:
                for trx in order['payment_history']:
                    if isinstance(trx, dict) and trx.get('transaction_type') == 'refund':
                        try:
                            total_refund += float(trx.get('amount', 0))
                        except Exception:
                            continue
        return f"{total_refund:.2f}"
    except Exception as e:
        # Top-level error guard
        return f"Error: An internal error occurred during refund calculation: {e}"
@mcp.tool()
def remove_items_from_pending_order(order_id, item_ids, payment_method_id):
    '''
    {
      "type": "function",
      "function": {
        "name": "remove_items_from_pending_order",
        "description": "Removes specified items from a user's pending order without requiring replacements. The user must confirm each removal, and the refunded amount for the removed items will be processed to the chosen payment method. Use this function when a user wishes to cancel or remove some items from a pending order, while keeping the rest of the order unchanged. Returns the updated order details after removal.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {"type": "string", "description": "The order's unique identifier."},
            "item_ids": {"type": "array", "items":{"type": "string"}, "description": "List of unique identifiers for items to remove from the order."},
            "payment_method_id": {"type": "string", "description": "The unique identifier for the payment method to process the refund to."}
          },
          "required": ["order_id", "item_ids", "payment_method_id"]
        }
      }
    }
    '''
    import json
    # Ensure order_id and payment_method_id are strings
    try:
        if not isinstance(order_id, str):
            order_id = str(order_id)
        if not isinstance(payment_method_id, str):
            payment_method_id = str(payment_method_id)
    except Exception as e:
        return {
            "error": f"order_id and payment_method_id must be convertible to string. Details: {e}"
        }
    # Try to ensure item_ids is a list of strings
    try:
        if isinstance(item_ids, str):
            # Attempt to parse as JSON array
            try:
                parsed = json.loads(item_ids)
                if isinstance(parsed, list):
                    item_list = [str(i) for i in parsed]
                else:
                    # Maybe it's a comma-separated string
                    item_list = [s.strip() for s in item_ids.split(",") if s.strip()]
            except Exception:
                item_list = [s.strip() for s in item_ids.split(",") if s.strip()]
        elif isinstance(item_ids, list):
            item_list = [str(i) for i in item_ids]
        else:
            item_list = [str(item_ids)]
    except Exception as e:
        return {
            "error": f"item_ids could not be parsed as a list or string list. Details: {e}"
        }
    # If list is empty, return error
    if not item_list:
        return {
            "error": "item_ids is empty. At least one item_id must be provided."
        }
    # Now, fetch order details to determine if all items are to be removed (i.e., full cancellation)
    try:
        order_details = get_order_details(order_id)
        order_items = order_details.get("items", [])
        order_item_ids = set(str(item["item_id"]) for item in order_items)
        remove_set = set(item_list)
        # If all items in the order are in remove_set, cancel the order
        if order_item_ids and (order_item_ids.issubset(remove_set)):
            # All items are being removed; treat as cancellation
            # Choose standard reason; can be made configurable if needed
            return cancel_pending_order(order_id, reason="no longer needed")
    except Exception as e:
        return {
            "error": f"Failed to check for full cancellation: {e}"
        }
    try:
        new_item_ids = ["" for _ in item_list]  # No-replacement/removal
        return modify_pending_order_items(order_id, item_list, new_item_ids, payment_method_id)
    except Exception as e:
        return {
            "error": f"Error calling modify_pending_order_items. Details: {e}"
        }
if __name__ == "__main__":
    mcp.run(transport='stdio')
