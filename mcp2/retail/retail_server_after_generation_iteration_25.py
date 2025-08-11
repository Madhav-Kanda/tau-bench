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
def count_available_product_variants(product_id):
    """
    {
      "type": "function",
      "function": {
        "name": "count_available_product_variants",
        "description": "Counts the number of available item variants (options) for a given product. This function queries the product details using the product's unique identifier and iterates through its variants, counting only those where the 'available' flag is set to True. The count is returned as a string. This is useful for determining inventory or availability information for a product with multiple options or versions.",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The unique identifier of the product for which available variants should be counted."
            }
          },
          "required": ["product_id"]
        }
      }
    }
    """
    import json

    try:
        # Try to coerce product_id to string, since it's expected to be a string
        if not isinstance(product_id, str):
            product_id = str(product_id)
        
        # Defensive try/catch in case get_product_details is missing or errors
        try:
            response = get_product_details(product_id)
        except Exception as e:
            return json.dumps({
                "error": f"Failed to retrieve product details: {str(e)}",
                "product_id": product_id
            })

        # If response is a JSON string, decode it
        if isinstance(response, str):
            try:
                details = json.loads(response)
            except Exception as e:
                return json.dumps({
                    "error": f"Product details could not be parsed as JSON: {str(e)}",
                    "product_id": product_id
                })
        elif isinstance(response, dict):
            details = response
        else:
            return json.dumps({
                "error": "Product details are neither string nor dict. Cannot continue.",
                "product_id": product_id
            })

        # Ensure 'variants' is a dict
        variants = details.get('variants', {})
        if not isinstance(variants, dict):
            return json.dumps({
                "error": "'variants' field is missing or not a dictionary in product details.",
                "product_id": product_id
            })

        count = 0
        for variant_id, variant in variants.items():
            # Robust handling: variant must be dict (ignore otherwise)
            if isinstance(variant, dict) and variant.get('available', False) is True:
                count += 1
        return str(count)
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error in count_available_product_variants: {str(e)}",
            "product_id": str(product_id)
        })


@mcp.tool()
def get_return_refund_options(order_id, item_ids):
    '''
    {
      "type": "function",
      "function": {
        "name": "get_return_refund_options",
        "description": "Returns the valid payment method options available for refunding returned items from a delivered order. This function examines the original payment method used for the order, as well as any eligible gift card(s) associated with the user, and returns a list of all valid refund destinations for the specified items. Use this function before finalizing a return request to inform the user of available refund methods, and to verify that the user's preferred refund option is available. The function takes the order's ID (with '#' prefix) and a JSON-encoded string listing the IDs of items to be returned. It returns a serialized JSON list of eligible payment method IDs and their human-readable descriptions (such as specific credit card info, PayPal, or gift card) that can be used for the refund.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    '''
    import json
    # Defensive conversion: order_id should be a string with '#' prefix
    if not isinstance(order_id, str):
        try:
            order_id = str(order_id)
        except Exception as e:
            return json.dumps({"error": f"order_id could not be stringified: {e}"})
    if not order_id.startswith('#'):
        order_id = f"#{order_id}"

    # Defensive conversion: item_ids should be a JSON list, or string encoding thereof
    item_ids_list = None
    if isinstance(item_ids, str):
        try:
            item_ids_list = json.loads(item_ids)
            if not isinstance(item_ids_list, list):
                return json.dumps({"error": "item_ids decoded but is not a list."})
        except Exception as e:
            return json.dumps({"error": f"item_ids could not be loaded as JSON list: {e}"})
    elif isinstance(item_ids, list):
        item_ids_list = item_ids
    else:
        return json.dumps({"error": "item_ids must be a JSON-encoded string or a list."})

    # Get order details (to find original payment method and user_id)
    try:
        order = get_order_details(order_id)
    except Exception as e:
        return json.dumps({"error": f"Error in get_order_details: {e}"})
    if isinstance(order, str):
        try:
            order = json.loads(order)
        except Exception as e:
            return json.dumps({"error": f"Order details returned as string but not JSON: {e}"})
    if not isinstance(order, dict):
        return json.dumps({"error": "Order details are not a dictionary."})
    user_id = order.get('user_id')
    if not user_id:
        return json.dumps({"error": "user_id not found in order details."})

    # Get user details (to find eligible gift cards)
    try:
        user = get_user_details(user_id)
    except Exception as e:
        return json.dumps({"error": f"Error in get_user_details: {e}"})
    if isinstance(user, str):
        try:
            user = json.loads(user)
        except Exception as e:
            return json.dumps({"error": f"User details returned as string but not JSON: {e}"})
    if not isinstance(user, dict):
        return json.dumps({"error": "User details are not a dictionary."})

    # Find original payment method from payment_history
    payment_history = order.get('payment_history', [])
    if isinstance(payment_history, str):
        try:
            payment_history = json.loads(payment_history)
        except Exception as e:
            return json.dumps({"error": f"payment_history is a string, but not JSON-decodable: {e}"})
    
    original_payment_method_id = None
    for ph in payment_history:
        if isinstance(ph, str):
            try:
                ph = json.loads(ph)
            except Exception:
                continue
        if isinstance(ph, dict) and ph.get('transaction_type') == 'payment':
            original_payment_method_id = ph.get('payment_method_id')
            break
    payment_methods = []
    user_pms = user.get('payment_methods', {})
    if isinstance(user_pms, str):
        try:
            user_pms = json.loads(user_pms)
        except Exception as e:
            return json.dumps({"error": f"user[\'payment_methods\'] returned as string but not JSON: {e}"})
    if not isinstance(user_pms, dict):
        user_pms = {}
    if original_payment_method_id:
        # Find source for display from user's payment methods
        pm_info = user_pms.get(original_payment_method_id, {})
        if isinstance(pm_info, str):
            try:
                pm_info = json.loads(pm_info)
            except Exception:
                pm_info = {}
        if pm_info.get('source') == 'credit_card':
            desc = f"Credit Card ({pm_info.get('brand','')} ****{pm_info.get('last_four','')})"
        elif pm_info.get('source') == 'paypal':
            desc = "PayPal"
        elif pm_info.get('source') == 'gift_card':
            desc = "Gift Card"
        else:
            desc = pm_info.get('source','Unknown Payment Method')
        payment_methods.append({"id": original_payment_method_id, "description": desc})
    # Add all user's gift cards
    for pm_id, pm_info in user_pms.items():
        if isinstance(pm_info, str):
            try:
                pm_info = json.loads(pm_info)
            except Exception:
                pm_info = {}
        if pm_info.get('source') == 'gift_card' and pm_id != original_payment_method_id:
            desc = 'Gift Card'
            payment_methods.append({"id": pm_id, "description": desc})
    return json.dumps(payment_methods)



@mcp.tool()
def get_most_expensive_available_variant(product_id, required_options=None):
    '''
    {
      "type": "function",
      "function": {
        "name": "get_most_expensive_available_variant",
        "description": "Finds and returns the most expensive available variant for a given product. This function retrieves the product details based on the supplied product_id and evaluates each variant to determine availability. Optionally, if required_options are provided (as a JSON string or dictionary), only those variants matching all specified key-value pairs will be considered. The function returns the variant dictionary with item_id, price, options, and availability status of the most expensive matching variant. If no matching and available variant is found, an appropriate error message is returned.",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The product id to look up."
            },
            "required_options": {
              "anyOf": [
                {"type": "string"},
                {"type": "object"},
                {"type": "null"}
              ],
              "description": "(Optional) JSON string, dictionary, or None, specifying required option key-value pairs for filtering variants."
            }
          },
          "required": ["product_id"]
        }
      }
    }
    '''
    import json
    def parse_options(options):
        if options is None or options == 'None' or options == 'null':
            return None
        if isinstance(options, dict):
            return options
        if isinstance(options, str):
            s = options.strip()
            if not s:
                return None
            try:
                return json.loads(s)
            except Exception:
                try:
                    # try to convert single quotes to double quotes for fallback
                    s2 = s.replace("'", '"')
                    return json.loads(s2)
                except Exception:
                    # Could not parse, just ignore options silently (fail-safe)
                    return None
        # Unknown type - ignore
        return None

    try:
        product_id_str = str(product_id)
    except Exception as e:
        return {'error': f'Invalid product_id: {repr(product_id)}. Conversion error: {str(e)}'}

    required_opts = parse_options(required_options)

    try:
        details = get_product_details(product_id_str)
    except Exception as e:
        return {'error': f'Error fetching product details for id {product_id_str}: {str(e)}'}

    if isinstance(details, str):
        import ast
        try:
            details = ast.literal_eval(details)
        except Exception as e:
            return {'error': f'Product details not valid dictionary for id {product_id_str}. Literal_eval failed: {str(e)}'}

    if not isinstance(details, dict):
        return {'error': f'Product details for id {product_id_str} are not in expected format.'}

    variants = details.get('variants', {})
    if not isinstance(variants, dict):
        return {'error': 'Product variants missing or not a dict.'}

    most_expensive = None
    for variant in variants.values():
        if not isinstance(variant, dict):
            continue
        if required_opts:
            matched = True
            options = variant.get('options', {})
            if not isinstance(options, dict):
                matched = False
            else:
                for k, v in required_opts.items():
                    if k not in options or str(options[k]) != str(v):
                        matched = False
                        break
            if not matched:
                continue
        available = variant.get('available', False)
        try:
            available = bool(available)
        except Exception:
            available = False
        if not available:
            continue
        try:
            price = float(variant.get('price', 0))
        except Exception:
            price = 0
        if (most_expensive is None) or (price > float(most_expensive.get('price', 0))):
            most_expensive = variant.copy()
            most_expensive['price'] = price  # store as float for comparison
    if most_expensive:
        out_price = most_expensive['price']
        orig_variant = None
        for v in variants.values():
            try:
                if float(v.get('price', 0)) == out_price and v.get('item_id') == most_expensive.get('item_id'):
                    orig_variant = v
                    break
            except Exception:
                continue
        if orig_variant:
            price_out = orig_variant.get('price')
        else:
            price_out = out_price
        return {
            'item_id': most_expensive['item_id'],
            'price': price_out,
            'options': most_expensive.get('options', {}),
            'available': bool(most_expensive.get('available', False))
        }
    return {'error': 'No available variant matches the criteria.'}



@mcp.tool()
def get_user_payment_methods(user_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_user_payment_methods",
        "description": "Retrieves all payment methods associated with a user, including gift cards (with their current balances), PayPal accounts, and credit cards. This function returns a dictionary containing all available payment methods for the specified user, providing a unified view for checking balances and available payment options.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string", "description": "The unique identifier of the user whose payment methods are to be retrieved."}
          },
          "required": ["user_id"]
        }
      }
    }
    """
    import json
    # Convert user_id to string if not already
    try:
        user_id_str = str(user_id)
    except Exception as e:
        return {
            "error": f"Could not convert user_id to string: {e}.",
            "input_user_id": user_id
        }
    
    try:
        details = get_user_details(user_id_str)
    except Exception as e:
        return {
            "error": f"Error calling get_user_details: {e}",
            "user_id": user_id_str
        }

    # Ensure we get a JSON string and parse safely
    if not isinstance(details, str):
        try:
            details = str(details)
        except Exception as e:
            return {
                "error": f"Could not convert details to string: {e}",
                "user_id": user_id_str
            }
    try:
        user_info = json.loads(details)
    except Exception as e:
        return {
            "error": f"Error parsing details JSON: {e}",
            "raw_details": details,
            "user_id": user_id_str
        }
    
    if not isinstance(user_info, dict):
        return {
            "error": "Parsed user_info is not a dictionary.",
            "parsed_user_info": user_info,
            "user_id": user_id_str
        }
    
    payment_methods = user_info.get('payment_methods', {})
    if not isinstance(payment_methods, dict):
        return {
            "error": "payment_methods field is not a dictionary.",
            "raw_payment_methods": payment_methods,
            "user_id": user_id_str
        }
    return payment_methods





@mcp.tool()
def get_order_tracking_info(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_order_tracking_info",
        "description": "Retrieves the tracking numbers and shipment details for a given order. This function takes an order ID as input and fetches the associated order details, extracting information for each fulfillment, including tracking ID(s), carrier (if available), the list of fulfilled item IDs, and the overall order status. The function returns these details as a JSON-encoded list of dictionaries, where each dictionary contains the following keys: 'tracking_id' (a list of tracking IDs), 'carrier' (if present), 'fulfilled_items' (a list of item IDs for that fulfillment), and 'status' (the current order status). This information is useful for providing users with shipment and tracking information for their orders.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The ID of the order for which tracking details are to be retrieved."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    """
    import json
    try:
        # Accept order_id as string or int
        if not isinstance(order_id, str):
            try:
                order_id = str(order_id)
            except Exception:
                return json.dumps({"error": "order_id could not be cast to string. Received: {}".format(repr(order_id))})
        # Check get_order_details existence
        if 'get_order_details' not in globals():
            return json.dumps({"error": "get_order_details function is not available in the current context."})
        order_details_str = get_order_details(order_id)
        try:
            order_details = json.loads(order_details_str)
        except Exception as e:
            return json.dumps({"error": "Failed to parse order_details JSON: {}".format(str(e)), "raw": order_details_str})
        fulfillments = order_details.get("fulfillments", [])
        if not isinstance(fulfillments, list):
            # Try to coerce it to a list
            fulfillments = [fulfillments]
        tracking_info_list = []
        for fulfill in fulfillments:
            tracking_entry = {}
            # tracking_id can be None, string or list
            tracking_id = fulfill.get("tracking_id", [])
            if tracking_id is None:
                tracking_id = []
            elif isinstance(tracking_id, str):
                tracking_id = [tracking_id]
            elif not isinstance(tracking_id, list):
                # Try to coerce unexpected type
                tracking_id = [str(tracking_id)]
            tracking_entry["tracking_id"] = tracking_id
            # Carrier (optional)
            carrier = fulfill.get("carrier", None)
            if carrier is not None:
                tracking_entry["carrier"] = carrier
            # Fulfilled item ids
            item_ids = fulfill.get("item_ids", [])
            if item_ids is None:
                item_ids = []
            elif isinstance(item_ids, str):
                item_ids = [item_ids]
            elif not isinstance(item_ids, list):
                item_ids = [str(item_ids)]
            tracking_entry["fulfilled_items"] = item_ids
            # Status
            status = order_details.get("status", None)
            tracking_entry["status"] = status
            tracking_info_list.append(tracking_entry)
        return json.dumps(tracking_info_list)
    except Exception as err:
        return json.dumps({"error": "Unexpected error in get_order_tracking_info: {}".format(str(err)), "order_id": repr(order_id)})
    


@mcp.tool()
def get_item_tracking_info(order_id, item_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_item_tracking_info",
        "description": "Retrieves a list of fulfillment records containing tracking and shipping details for a specified item within a given order. For the given order_id (string) and item_id (string), the function filters all fulfillment records to include only those that list the specified item_id among their fulfilled items. Each returned fulfillment is a dictionary containing: 'tracking_id' (list of tracking numbers), 'carrier' (optional, carrier information if available), 'fulfilled_items' (list of fulfilled item IDs), and 'status' (fulfillment or order status as a string). This can be used to obtain tracking and shipping status for a specific item when orders contain multiple items that may ship separately.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    """
    try:
        # Attempt to convert the arguments to the required types (string)
        order_id_str = str(order_id) if order_id is not None else None
        item_id_str = str(item_id) if item_id is not None else None
        if not order_id_str or not item_id_str:
            return {"error": "Missing required argument: order_id and item_id are both required as non-empty strings."}
    except Exception as e:
        return {"error": f"Argument conversion failed: {str(e)}"}

    try:
        # Use get_order_tracking_info to fetch all fulfillments
        all_fulfillments = get_order_tracking_info(order_id_str)
        if all_fulfillments is None:
            return {"error": f"No fulfillment records found for order_id {order_id_str}."}
        # Filter fulfillment(s) where 'fulfilled_items' contains the item_id
        result = []
        for fulfillment in all_fulfillments:
            fulfilled_items = fulfillment.get('fulfilled_items', [])
            # Try to ensure all items in fulfilled_items are string for comparison
            fulfilled_items_str = [str(fi) for fi in fulfilled_items if fi is not None]
            if item_id_str in fulfilled_items_str:
                result.append(fulfillment)
        return result
    except Exception as e:
        return {"error": f"Failed to retrieve item tracking info: {str(e)}"}


@mcp.tool()
def get_cheapest_available_variant(product_id, required_options=None):
    '''
    {
      "type": "function",
      "function": {
        "name": "get_cheapest_available_variant",
        "description": "Finds and returns the cheapest available variant for a specified product. This function retrieves the product details using the provided product_id and examines all its variants to determine which ones are available. If required_options are specified (as a JSON string, dictionary, or None), only variants matching all of the specified option key-value pairs will be considered. The function returns the details of the cheapest variant as a JSON string, including fields such as item_id, price, options, and availability. If no suitable variant is found, an error message is returned as JSON. This is useful for price queries and comparison shopping, particularly when searching for specific product configurations.",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The unique identifier for the product whose variants are being searched."
            },
            "required_options": {
              "type": ["object", "string", "null"],
              "description": "Optional. Filter criteria for variant options. Accepts a dictionary, a JSON-formatted string, or None. Only variants matching all specified key-value pairs are considered."
            }
          },
          "required": ["product_id"]
        }
      }
    }
    '''
    import json
    # Defensive conversion of product_id to string
    try:
        pid = str(product_id)
    except Exception as e:
        return json.dumps({'error': f'Could not convert product_id to string: {str(e)}'})
    # Defensive fetch of product details
    try:
        details = get_product_details(pid)
    except Exception as e:
        return json.dumps({'error': f'Error fetching product details: {str(e)}'})
    # Coerce fetched details to dict if it's a JSON string
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except Exception as e:
            return json.dumps({'error': f'Product details are not valid JSON: {str(e)}'})
    if not isinstance(details, dict):
        return json.dumps({'error': 'Product details are not a dict after processing.'})
    # Defensive extraction of variants
    variants = details.get('variants', {})
    if not isinstance(variants, dict):
        return json.dumps({'error': 'Variants field is not a dict.'})
    # Parse required_options into dict
    options_dict = None
    if required_options is not None:
        if isinstance(required_options, dict):
            options_dict = required_options
        elif isinstance(required_options, str):
            try:
                options_dict = json.loads(required_options)
                if not isinstance(options_dict, dict):
                    return json.dumps({'error': 'Parsed required_options string is not a dict.'})
            except Exception as e:
                return json.dumps({'error': f'Could not parse required_options string as JSON: {str(e)}'})
        elif required_options is None:
            options_dict = None
        else:
            return json.dumps({'error': f'required_options must be a dict, JSON string, or None (got {type(required_options)}).'})
    # Search for the cheapest available variant that matches required_options
    cheapest = None
    for variant in variants.values():
        if not isinstance(variant, dict):
            continue
        if not variant.get('available', False):
            continue
        # Defensive extraction of variant options
        v_options = variant.get('options', {})
        if options_dict:
            if not isinstance(v_options, dict):
                continue
            match = True
            for k, v in options_dict.items():
                if v_options.get(k) != v:
                    match = False
                    break
            if not match:
                continue
        v_price = variant.get('price')
        try:
            v_price = float(v_price)
        except (ValueError, TypeError):
            continue
        if (cheapest is None) or (v_price < float(cheapest.get('price', float('inf')))):
            cheapest = variant
    if cheapest:
        try:
            return json.dumps(cheapest)
        except Exception as e:
            return json.dumps({'error': f'Could not serialize result to JSON: {str(e)}'})
    else:
        return json.dumps({'error': 'No available variant found matching these options.'})
@mcp.tool()
def modify_pending_order_addresses_bulk(order_ids, address1, address2, city, state, country, zip):
    '''
    {
      "type": "function",
      "function": {
        "name": "modify_pending_order_addresses_bulk",
        "description": "Updates the shipping address for multiple pending orders in a single operation. This function accepts a collection of order IDs (provided as a comma-separated string, JSON array string, or Python list) and new address components including address1, address2, city, state, country, and zip. For each provided order ID, it attempts to update the shipping address of the associated pending order by calling the existing modify_pending_order_address function. The function returns a summary dictionary mapping each order ID to the result status or error of the update attempt. This bulk update utility is particularly useful for correcting shipping details across multiple pending orders efficiently, reducing manual repetitive tasks and ensuring address consistency.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_ids": {
              "anyOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}}
              ],
              "description": "List of order IDs to update, as a comma-separated string, JSON array string, or Python list."
            },
            "address1": {
              "type": "string",
              "description": "First line of the new address."
            },
            "address2": {
              "type": "string",
              "description": "Second line of the new address (optional)."
            },
            "city": {
              "type": "string",
              "description": "City for the new address."
            },
            "state": {
              "type": "string",
              "description": "State or region for the new address."
            },
            "country": {
              "type": "string",
              "description": "Country for the new address."
            },
            "zip": {
              "type": "string",
              "description": "Postal/ZIP code for the new address."
            }
          },
          "required": ["order_ids", "address1", "address2", "city", "state", "country", "zip"]
        }
      }
    }
    '''
    import json
    results = {}
    # Try to convert order_ids into a valid Python list
    try:
        # Accept strings (possibly comma-separated or JSON), or lists.
        order_id_list = None
        if isinstance(order_ids, list):
            order_id_list = order_ids
        elif isinstance(order_ids, str):
            try:
                # Try parsing as JSON array string
                val = json.loads(order_ids)
                if isinstance(val, list):
                    order_id_list = val
                else:
                    # It's a primitive; use as single item
                    order_id_list = [str(order_ids)]
            except Exception:
                # Not a JSON string, maybe comma-separated
                split_ids = [x.strip() for x in order_ids.split(',') if x.strip()]
                if split_ids:
                    order_id_list = split_ids
                else:
                    order_id_list = [str(order_ids)]
        else:
            # Fallback to string representation
            order_id_list = [str(order_ids)]
        if not isinstance(order_id_list, list) or not order_id_list:
            return {"error": "No valid order IDs were provided. Please review the request payload."}
    except Exception as e:
        return {"error": f"Unable to parse order_ids: {str(e)}"}
    # Sanitize/force types for other parameters
    try:
        address1 = str(address1)
        address2 = str(address2)
        city = str(city)
        state = str(state)
        country = str(country)
        zip = str(zip)
    except Exception as e:
        return {"error": f"Could not convert address parameters to string: {str(e)}"}
    # Perform bulk operation, collecting results and errors
    for order_id in order_id_list:
        try:
            res = modify_pending_order_address(
                order_id=str(order_id),
                address1=address1,
                address2=address2,
                city=city,
                state=state,
                country=country,
                zip=zip
            )
            results[str(order_id)] = res
        except Exception as e:
            results[str(order_id)] = {"error": f"Failed to update order_id {order_id}: {str(e)}"}
    return results
@mcp.tool()
def get_pending_orders_for_user(user_id):
    '''
    {
      "type": "function",
      "function": {
        "name": "get_pending_orders_for_user",
        "description": "Returns a list of order IDs, as strings, that belong to the specified user and are currently in the 'pending' state. These 'pending' orders are modifiable by agent functions (such as modifying items, address, or payment method). This function is intended to assist workflows that require efficient bulk or multi-order modifications for a single user. The function accepts a string user_id and returns a list of the user's order IDs with status 'pending'.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": { "type": "string", "description": "The user's id to look for pending orders." }
          },
          "required": ["user_id"]
        }
      }
    }
    '''
    import json
    try:
        # LLMs might send user_id nested in a dict or as part of args, attempt to extract
        if isinstance(user_id, dict) and "user_id" in user_id:
            user_id = user_id["user_id"]
        elif isinstance(user_id, (list, tuple)) and len(user_id) > 0:
            user_id = user_id[0]
        user_id = str(user_id)
    except Exception as e:
        return {"error": f"Could not extract user_id: {str(e)}"}

    try:
        user_details = get_user_details(user_id)
        # Patch: If user_details is a string (likely JSON), load it
        if isinstance(user_details, str):
            user_details = json.loads(user_details)
    except Exception as e:
        return {"error": f"Error retrieving user details for user_id {user_id}: {str(e)}"}
    if user_details is None or "orders" not in user_details:
        return {"error": f"No orders found or invalid user for user_id {user_id}"}

    pending_orders = []
    for oid in user_details.get("orders", []):
        try:
            order = get_order_details(oid)
            if isinstance(order, str):
                order = json.loads(order)
        except Exception as e:
            # Log or skip the order if inaccessible
            continue
        if isinstance(order, dict) and order.get("status") == "pending":
            pending_orders.append(str(oid))
    return pending_orders
@mcp.tool()
def calculate_order_total_excluding_items(order_id, exclude_item_ids):
    '''
    {"type": "function", "function": {"name": "calculate_order_total_excluding_items", "description": "Calculates the total amount paid for a specific order after excluding the prices of specified item IDs. This function is useful in scenarios where you need to determine the remaining value in an order after some items have been returned or excluded. It takes an order ID and a list of item IDs to be excluded, which can be provided as a JSON string, a comma-separated string, or a Python list. The function returns the updated order total, excluding the specified items, as a rounded string.", "parameters": {"type": "object", "properties": {"order_id": {"type": "string", "description": "The ID of the order to process."}, "exclude_item_ids": {"oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}], "description": "A JSON-encoded list, comma-separated string, or Python list of item IDs to exclude from the total calculation."}}, "required": ["order_id", "exclude_item_ids"]}}}
    '''
    import json
    def normalize_exclude_item_ids(exclude_item_ids):
        # Handle string types (could be comma separated, JSON encoded, or single ID)
        if isinstance(exclude_item_ids, str):
            # Try to detect JSON list
            try:
                potential_json = exclude_item_ids.strip()
                if (potential_json.startswith('[') and potential_json.endswith(']')) or \
                   (potential_json.startswith('"') and potential_json.endswith('"')):
                    loaded = json.loads(potential_json)
                    if isinstance(loaded, list):
                        return set(str(x) for x in loaded)
                    else:
                        # Not a list, treat as single ID
                        return set([str(loaded)])
            except Exception:
                # Not JSON, treat as plain string
                pass
            # Try comma separated or single string
            if ',' in exclude_item_ids:
                return set(s.strip() for s in exclude_item_ids.split(',') if s.strip())
            else:
                s = exclude_item_ids.strip()
                if s:
                    return set([s])
                else:
                    return set()
        # Handle list/tuple/set
        elif isinstance(exclude_item_ids, (list, tuple, set)):
            return set(str(x) for x in exclude_item_ids)
        else:
            # Unknown type
            raise ValueError("exclude_item_ids must be a string, list, or set.")

    try:
        items_to_exclude = normalize_exclude_item_ids(exclude_item_ids)
    except Exception as e:
        return f"Error: Failed to interpret exclude_item_ids argument ({str(e)})"

    # Defensive cast order_id to str (may come as int, etc)
    order_id_str = str(order_id)
    try:
        order_details = get_order_details(order_id_str)
    except Exception as e:
        return f"Error: Exception encountered fetching order details: {str(e)}"
    # Try parsing if comes as string (common from LLM)
    if isinstance(order_details, str):
        import ast
        try:
            if order_details.strip().startswith('{') or order_details.strip().startswith('['):
                order_details = ast.literal_eval(order_details)
        except Exception:
            return 'Error: Unable to parse returned order details.'
    if not order_details or not isinstance(order_details, dict) or 'items' not in order_details:
        return 'Error: Unable to fetch order items.'
    if not isinstance(order_details['items'], list):
        return 'Error: Malformed order details (items is not a list).'
    total = 0.0
    for item in order_details['items']:
        try:
            item_id = str(item.get('item_id', ''))
            if item_id and item_id not in items_to_exclude:
                price = item.get('price')
                if price is not None:
                    total += float(price)
        except Exception as e:
            # Skip item and log issue
            continue
    return str(round(total, 2))
@mcp.tool()
def calculate_refund_total_for_items(order_id, item_ids):
    """
    {
      "type": "function",
      "function": {
        "name": "calculate_refund_total_for_items",
        "description": "Calculates the total refund amount for a set of returned items within a specified order. This function determines the sum of the prices for the provided item IDs in the given order, allowing the customer to know the precise refund amount when partially returning items from an order. The function handles various formats for the item_ids parameter (JSON string, comma-separated string, or Python list) and ensures proper parsing and calculation. Returns the total refundable amount as a string rounded to two decimal places, or an error string if order or item data cannot be parsed.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The ID of the order from which refund is being calculated."
            },
            "item_ids": {
              "oneOf": [
                {"type": "string", "description": "A JSON string, comma-separated string, or single item ID representing one or more item IDs to refund."},
                {"type": "array", "items": {"type": "string"}, "description": "List of item IDs to be refunded."}
              ],
              "description": "One or more item IDs to be refunded, specified as a JSON string, a comma-separated string, or a Python list."
            }
          },
          "required": ["order_id", "item_ids"]
        },
        "returns": {
          "type": "string",
          "description": "The total refund amount, rounded to two decimal places, as a string. Returns an error string if input data is invalid."
        }
      }
    }
    """
    import json
    try:
        # Try to parse item_ids into a list of strings
        item_ids_list = []
        if isinstance(item_ids, list):
            # If it's a list, ensure all entries are strings
            item_ids_list = [str(x).strip() for x in item_ids if str(x).strip()]
        elif isinstance(item_ids, str):
            # Try to parse as JSON array or string
            try:
                loaded = json.loads(item_ids)
                if isinstance(loaded, list):
                    item_ids_list = [str(x).strip() for x in loaded if str(x).strip()]
                elif isinstance(loaded, str):
                    item_ids_list = [loaded.strip()] if loaded.strip() else []
                else:
                    return "Error: 'item_ids' JSON did not decode to a list or string."
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as comma-separated string
                if ',' in item_ids:
                    item_ids_list = [x.strip() for x in item_ids.split(',') if x.strip()]
                elif item_ids.strip():
                    item_ids_list = [item_ids.strip()]
        else:
            return "Error: 'item_ids' is not a recognisable type."
        if not item_ids_list:
            return "Error: No valid item IDs provided."
    except Exception as e:
        return f"Error processing 'item_ids': {str(e)}"

    # Get order details
    order = get_order_details(order_id)
    # If returned as a JSON string or dict
    if isinstance(order, str):
        import ast
        try:
            order = ast.literal_eval(order)
        except Exception:
            try:
                order = json.loads(order)
            except Exception:
                return 'Error: Unable to parse order details.'
    if not isinstance(order, dict):
        return 'Error: Order data is not a dictionary.'
    if 'items' not in order or not isinstance(order['items'], list):
        return 'Error: No item details found in the order.'

    total = 0.0
    for item in order['items']:
        item_id = str(item.get('item_id', '')).strip()
        price = item.get('price', 0.0)
        try:
            if item_id in item_ids_list:
                total += float(price)
        except Exception as e:
            # Price or id issue, skip this item
            continue
    return f'{round(total, 2):.2f}'
@mcp.tool()
def get_all_items_in_order(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_all_items_in_order",
        "description": "Retrieves all items associated with a specific order using the provided order_id. This function calls get_order_details(order_id) and returns the 'items' list found in the order details dictionary. Each item in the list is itself a dictionary, typically containing at least an 'item_id', and optionally fields such as 'name', 'product_id', 'price', and 'options'. If the order details retrieval returns a string (for example, an error message), the function returns that string directly. Otherwise, it returns the list of items or an empty list if no items are found.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique ID of the order, usually in string format and often prefixed with a '#' character."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    """
    try:
        # Convert to string and strip leading/trailing spaces if possible
        if not isinstance(order_id, str):
            order_id = str(order_id)
        order_id = order_id.strip()
        # Optionally, enforce '#' prefix if domain-specific rule. Uncomment next lines if needed.
        # if not order_id.startswith('#'):
        #     order_id = '#' + order_id
    except Exception as e:
        return f"Could not process order_id argument: {e}"
    try:
        order_details = get_order_details(order_id)
    except Exception as e:
        return f"Error calling get_order_details: {e}"
    if isinstance(order_details, str):
        # If error string or not parsed, return directly
        return order_details
    if not isinstance(order_details, dict):
        return f"Unexpected order_details format: {type(order_details)} ({order_details})"
    items = order_details.get('items', [])
    if not isinstance(items, list):
        return f"Unexpected items format: {type(items)} ({items})"
    return items
@mcp.tool()
def get_order_total(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_order_total",
        "description": "Retrieves the total amount paid for a specific order, including all items and applicable fees, unless otherwise specified. This function is mainly used to confirm the total or refund amount for an order after modifications, cancellations, or address changes. It first attempts to compute the total based on the order's payment history, summing all payment-type transactions. If payment history is unavailable, it falls back to summing item prices in the order, if such information exists. Returns the computed total amount paid as a formatted string or returns an error message if the total cannot be determined.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique identifier of the order (e.g., '#W1234567')."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    """
    # Ensure order_id is a string (handle int, float, bool, or None)
    if order_id is None or (isinstance(order_id, str) and not order_id.strip()):
        return 'Error: Provided order_id is null or empty.'
    try:
        if not isinstance(order_id, str):
            order_id = str(order_id)
    except Exception as e:
        return f"Error: Could not convert order_id to string ({e})."
    try:
        order_details = get_order_details(order_id)
    except Exception as e:
        return f"Error: Exception while retrieving order details ({e})."
    if isinstance(order_details, str):
        # If an error message or a JSON-serialized dictionary is returned
        try:
            import json
            details = json.loads(order_details)
            order_details = details
        except Exception:
            # If not JSON, return the string (assumed to be error message)
            return order_details
    if not isinstance(order_details, dict):
        return 'Error: Unable to retrieve order details.'
    total = None
    payment_history = order_details.get('payment_history', [])
    if not isinstance(payment_history, list):
        payment_history = []
    payments = [entry for entry in payment_history if isinstance(entry, dict) and entry.get('transaction_type') == 'payment']
    try:
        if payments:
            amounts = []
            for entry in payments:
                try:
                    amounts.append(float(entry['amount']))
                except Exception:
                    continue
            if amounts:
                total = sum(amounts)
        else:
            # Fallback: Try to sum item prices if present
            items = order_details.get('items', [])
            if isinstance(items, list) and items and all(isinstance(item, dict) and 'price' in item for item in items):
                amounts = []
                for item in items:
                    try:
                        amounts.append(float(item['price']))
                    except Exception:
                        continue
                if amounts:
                    total = sum(amounts)
    except Exception as e:
        return f"Error: Exception while calculating total ({e})."
    if total is not None:
        try:
            return '{:.2f}'.format(total)
        except Exception as e:
            return f"Error: Could not format the total ({e})."
    else:
        return 'Error: Could not determine the order total.'
@mcp.tool()
def get_order_refund_total(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_order_refund_total",
        "description": "Calculates and returns the total amount refunded for a specific order, identified by order_id. This function retrieves the order details and examines the payment history to find all transactions of type 'refund'. It sums the 'amount' fields of these refund transactions to compute the total refunded amount. The function accepts the order_id as a parameter (expected to be a string), and returns the total refunded amount as a string formatted to two decimal places. If there are no refunds for the order, the function returns '0.00'. If the order details are unavailable or invalid, it returns an error message as a string.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    """
    import json
    # Ensure order_id is string and not None/empty
    if order_id is None:
        return 'Error: order_id is required.'
    if not isinstance(order_id, str):
        try:
            order_id = str(order_id)
        except Exception:
            return 'Error: Unable to convert order_id to string.'
    if order_id.strip() == '':
        return 'Error: order_id cannot be empty.'
    try:
        order_details = get_order_details(order_id)
    except Exception as e:
        return f'Error: Exception while retrieving order details: {e}'
    # Try to parse JSON string if it's a string response
    if isinstance(order_details, str):
        try:
            order_details = json.loads(order_details)
        except Exception:
            return 'Error: Unable to parse order details.'
    if not isinstance(order_details, dict):
        return 'Error: Invalid order details structure.'
    payment_history = order_details.get('payment_history', [])
    # Accept payment_history as serialized string as well
    if isinstance(payment_history, str):
        try:
            payment_history = json.loads(payment_history)
        except Exception:
            return 'Error: Unable to parse payment_history.'
    if not isinstance(payment_history, list):
        return 'Error: payment_history must be a list.'
    if not payment_history:
        return '0.00'
    total_refund = 0.0
    for transaction in payment_history:
        if isinstance(transaction, str):
            try:
                transaction = json.loads(transaction)
            except Exception:
                continue
        if not isinstance(transaction, dict):
            continue
        if transaction.get('transaction_type') == 'refund':
            # Try to tolerate missing amounts and non-float convertible amounts
            amount = transaction.get('amount', 0)
            if amount in [None, '']:
                continue
            try:
                # Accept both string and numeric types
                total_refund += float(amount)
            except Exception:
                continue
    try:
        return '{:.2f}'.format(total_refund)
    except Exception:
        return 'Error: Unable to format refund total.'
@mcp.tool()
def get_order_total_after_modification(order_id):
    '''
    {
      "type": "function",
      "function": {
        "name": "get_order_total_after_modification",
        "description": "Retrieves the total amount for a specific order after a modification such as address or payment method change. This function ensures the agent can confirm and communicate the accurate, updated price or total (including any dynamic price changes, fees, or discounts resulting from the modification) to the user. It should be called after any modification action to guarantee the user receives up-to-date pricing information. Arguments: order_id (string): The unique identifier of the order. Must include the '#' prefix if applicable. Returns: (string): The current total amount for the order after modifications.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique identifier of the order. Must include the '#' prefix if applicable."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    '''
    # Argument normalization & defensive programming
    try:
        # Accepts int, float, or str; converts to str and ensures '#' prefix as appropriate
        if order_id is None:
            return "Error: 'order_id' argument is required."
        order_id_str = str(order_id).strip()
        if not order_id_str:
            return "Error: 'order_id' argument cannot be empty."
        # Heuristically prepend '#' if that's the order format and it's missing (optional)
        if not order_id_str.startswith('#') and any(c.isdigit() for c in order_id_str):
            # For agents that may just submit numbers (e.g., '12345')
            order_id_str = '#' + order_id_str
        # Final validation: basic check that order_id looks valid
        if not order_id_str.startswith('#') or len(order_id_str) < 2:
            return f"Error: order_id ('{order_id_str}') is not in the expected format (should start with '#')."
        return get_order_total(order_id_str)
    except Exception as e:
        return f"Error in get_order_total_after_modification: {str(e)}"
@mcp.tool()
def get_item_details_in_order(order_id, item_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_item_details_in_order",
        "description": "Retrieves all available fields (such as price, options, product id, and item name) for a specific item within the context of a given order. This function is useful when quickly finding the price, characteristics, or options of a particular item that a user has ordered, or when computing totals and refunds involving individual items. If the specified item is found within the order, a dictionary containing the item's details is returned; otherwise, an error string will be returned indicating the item could not be found.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    """
    # Convert arguments to string for robustness to LLM input
    try:
        order_id_str = str(order_id).strip()
        item_id_str = str(item_id).strip()
    except Exception as e:
        return f"Error processing input arguments: {e}"  

    # Defensive: order_id cannot be empty or None
    if not order_id_str:
        return "Error: order_id is missing or empty."
    if not item_id_str:
        return "Error: item_id is missing or empty."

    try:
        items = get_all_items_in_order(order_id_str)
    except Exception as e:
        return f"Error calling get_all_items_in_order: {e}"
    
    if isinstance(items, str):
        # error string or not found
        return items
    if not isinstance(items, list):
        return f"Error: get_all_items_in_order did not return a list."

    for item in items:
        item_id_value = item.get('item_id')
        if item_id_value is not None and str(item_id_value).strip() == item_id_str:
            return item
    return f"Item id {item_id} not found in order {order_id}."
@mcp.tool()
def calculate_order_total_with_item_replacement(order_id, old_item_ids, new_item_ids):
    """
    {
      "type": "function",
      "function": {
        "name": "calculate_order_total_with_item_replacement",
        "description": "Calculates the recalculated total amount for a given order after replacing certain items with new specified items. The function takes three arguments: an order ID, a list of old item IDs to remove, and a list of new item IDs to add. The item ID lists may be passed as strings in JSON array format or as comma-separated values. The function works as follows: 1) Retrieves all items in the specified order. 2) Removes those identified by the old_item_ids list, subtracting their prices from the order total. 3) For each item in the new_item_ids list, fetches the price using the associated product ID (which matches the product type of the removed item). 4) Adds the price for each new item to the total. If any errors occur during data retrieval (e.g., unable to fetch order, product, or variant data), the function returns an error message as a string. The final output is a string with the recalculated order total, rounded to two decimal places.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique identifier of the order to be recalculated."
            },
            "old_item_ids": {
              "type": "string",
              "description": "A JSON array string or a comma-separated values string representing the item IDs to remove from the order."
            },
            "new_item_ids": {
              "type": "string",
              "description": "A JSON array string or a comma-separated values string representing the item IDs to add to the order as replacements."
            }
          },
          "required": ["order_id", "old_item_ids", "new_item_ids"]
        }
      }
    }
    """
    import json
    def parse_ids(ids):
        # Normalize: always return a list of strings
        if isinstance(ids, list):
            return [str(x) for x in ids]
        if isinstance(ids, str):
            ids_strip = ids.strip()
            if ids_strip.startswith('[') and ids_strip.endswith(']'):
                try:
                    parsed = json.loads(ids_strip)
                    if isinstance(parsed, list):
                        return [str(x) for x in parsed]
                except Exception:
                    pass
            # Now try comma-separated string
            if ',' in ids_strip:
                return [s.strip() for s in ids_strip.split(',') if s.strip()]
            # If it's a single non-empty string (not JSON array/not comma)
            if ids_strip:
                return [ids_strip]
            else:
                return []
        # Handle numeric types (shouldn't happen but just in case)
        if isinstance(ids, (int, float)):
            return [str(ids)]
        return []

    order_id_str = str(order_id) if not isinstance(order_id, str) else order_id

    old_ids = parse_ids(old_item_ids)
    new_ids = parse_ids(new_item_ids)

    if not isinstance(old_ids, list) or not isinstance(new_ids, list):
        return "Error: Invalid format for item ids."
    if len(old_ids) == 0:
        return "Error: No old item ids given."
    if len(new_ids) == 0:
        return "Error: No new item ids given."

    try:
        # 1. Get all order items
        items = get_all_items_in_order(order_id_str)
    except Exception as e:
        return f"Error: Failed to fetch order items: {str(e)}"
    if isinstance(items, str):
        # Error message from function
        return items

    # 2. Calculate original total
    try:
        orig_total = 0.0
        item_dict = {}  # Map item_id to its detail
        for it in items:
            item_id = str(it.get('item_id'))
            price = it.get('price', 0)
            try:
                price = float(price)
            except Exception:
                price = 0.0
            orig_total += price
            item_dict[item_id] = it
    except Exception as e:
        return f"Error: Failed to process order items: {str(e)}"

    # 3. Subtract the price of removed items
    removed_total = 0.0
    old_prods = []  # For product_id checking
    for oid in old_ids:
        oid_str = str(oid)
        if oid_str in item_dict:
            try:
                price = float(item_dict[oid_str].get('price', 0))
            except Exception:
                price = 0.0
            removed_total += price
            old_prods.append((oid_str, item_dict[oid_str].get('product_id', '')))
        else:
            # Not found, skip with warning
            old_prods.append((oid_str, None))

    # 4. Find prices for replacement items
    added_total = 0.0
    for idx, nid in enumerate(new_ids):
        nid_str = str(nid)
        # Determine corresponding product_id (require same type as old item being replaced)
        if idx < len(old_prods):
            product_id = old_prods[idx][1]
        else:
            product_id = None
        if not product_id:
            return f"Error: Cannot determine product id for replacement item {nid_str}."
        try:
            prod_detail = get_product_details(product_id)
        except Exception as e:
            return f"Error: Failed to fetch product details: {str(e)}"
        if isinstance(prod_detail, str):
            return prod_detail
        variants = prod_detail.get('variants', {})
        # Variants could be a dict with item_id as key or a list
        variant = None
        if isinstance(variants, dict):
            variant = variants.get(nid_str)
            if not variant:
                # Try by matching 'item_id' as key
                for v in variants.values():
                    if str(v.get('item_id')) == nid_str:
                        variant = v
                        break
        elif isinstance(variants, list):
            for v in variants:
                if str(v.get('item_id')) == nid_str:
                    variant = v
                    break
        price = None
        if variant:
            price = variant.get('price')
        if price is None:
            return f"Error: Could not find price for replacement item {nid_str} in product {product_id}."
        try:
            price = float(price)
        except Exception:
            return f"Error: Non-numeric price found for replacement item {nid_str}."
        added_total += price
    # 5. Compute new total
    new_total = orig_total - removed_total + added_total
    try:
        return f"{round(new_total, 2):.2f}"
    except Exception:
        return "Error: Failed to compute or format final total."
@mcp.tool()
def get_item_price_and_options_in_order(order_id, item_name):
    """
    {
      "type": "function",
      "function": {
        "name": "get_item_price_and_options_in_order",
        "description": "Retrieves the price and all available option details (such as battery life, color, etc.) for the first item matching the specified name within the given order. This function is useful for answering user inquiries about the price or specific options of an ordered or potentially modifiable item. If the order or item cannot be found, it returns an appropriate error message.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The order identifier, possibly prefixed with '#' as used in your system."
            },
            "item_name": {
              "type": "string",
              "description": "The exact name of the item for lookup as it appears in the order."
            }
          },
          "required": ["order_id", "item_name"]
        }
      }
    }
    """
    import json
    # Ensure arguments are strings
    try:
        if not isinstance(order_id, str):
            order_id = str(order_id)
        if not isinstance(item_name, str):
            item_name = str(item_name)
    except Exception as e:
        return f"Error: Failed to convert order_id or item_name to string. Details: {str(e)}"
    
    # Defensive: strip and normalize
    order_id = order_id.strip()
    item_name = item_name.strip()
    
    try:
        all_items = get_all_items_in_order(order_id)
        # If the return value is a string, see if it's actually a serialized dict (as observed in the bug)
        if isinstance(all_items, str):
            try:
                parsed = json.loads(all_items)
                if isinstance(parsed, dict) and 'items' in parsed:
                    all_items = parsed['items']
                else:
                    return f"Error: Unable to retrieve items for order {order_id}. {all_items}"
            except Exception:
                # Not a JSON string: treat as error as before
                return f"Error: Unable to retrieve items for order {order_id}. {all_items}"
    except Exception as e:
        return f"Error: Exception while retrieving items for order {order_id}. Details: {str(e)}"
    
    if not hasattr(all_items, '__iter__'):
        return f"Error: Unexpected return value from get_all_items_in_order for order {order_id}."
    for item in all_items:
        try:
            name = item.get('name') if isinstance(item, dict) else None
            if name is not None and str(name).strip().lower() == item_name.lower():
                result = {
                    'price': item.get('price', None) if isinstance(item, dict) else None,
                    'options': item.get('options', {}) if isinstance(item, dict) else {}
                }
                return result
        except Exception as e:
            continue
    return f"Error: Item '{item_name}' not found in order {order_id}."
@mcp.tool()
def check_order_modification_status(order_id):
    """
    {
      "type": "function",
      "function": {
        "name": "check_order_modification_status",
        "description": "Checks whether an order with the given order_id can still have its items modified. This function retrieves the current status of the order and determines if item modifications are allowed based on the status. It also checks if item modification has already been performed using the modify_pending_order_items tool. The function returns a dictionary containing a boolean under the key 'modification_allowed' and a 'reason' string that explains why modification is allowed or not. Typical statuses considered are 'pending' (modification allowed), statuses indicating previous modification (modification not allowed), 'processed', 'delivered', and 'cancelled'.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique identifier of the order whose modification status is to be checked."
            }
          },
          "required": ["order_id"]
        }
      }
    }
    """
    # Ensure order_id is a string and not a list, dict, or None
    if order_id is None:
        return {
            'modification_allowed': False,
            'reason': 'order_id is missing or None.'
        }
    if isinstance(order_id, (list, tuple)):
        if len(order_id) == 0:
            return {
                'modification_allowed': False,
                'reason': 'order_id was provided as an empty list or tuple.'
            }
        order_id = order_id[0]
    if isinstance(order_id, dict):
        if 'order_id' in order_id:
            order_id = order_id['order_id']
        else:
            return {
                'modification_allowed': False,
                'reason': 'order_id was provided as a dict without "order_id" key.'
            }
    try:
        str_order_id = str(order_id)
        if not str_order_id.strip():
            return {
                'modification_allowed': False,
                'reason': 'order_id is empty or blank after conversion to string.'
            }
    except Exception as e:
        return {
            'modification_allowed': False,
            'reason': f'order_id could not be stringified: {e}'
        }
    try:
        order_details = get_order_details(str_order_id)
    except Exception as e:
        return {
            'modification_allowed': False,
            'reason': f'Error retrieving order details: {e}'
        }
    # Attempt to parse if it's a string (e.g., a JSON blob)
    if isinstance(order_details, str):
        try:
            import json
            order_details = json.loads(order_details)
        except Exception:
            return {'modification_allowed': False, 'reason': 'Failed to parse order details.'}
    # order_details should now be a dict
    if not isinstance(order_details, dict):
        return {'modification_allowed': False, 'reason': 'Order details are not in the expected format.'}
    status = str(order_details.get('status', '')).lower()
    if status == 'pending':
        return {
            'modification_allowed': True,
            'reason': 'Item modification is allowed. Order status is pending and item modifications have not yet been made.'
        }
    elif 'item modif' in status:
        return {
            'modification_allowed': False,
            'reason': 'Item modification is NOT allowed: the modify_pending_order_items tool has already been used for this pending order.'
        }
    elif status == 'processed':
        return {
            'modification_allowed': False,
            'reason': 'Order has already been processed. Item modification is not allowed.'
        }
    elif status == 'delivered':
        return {
            'modification_allowed': False,
            'reason': 'Order is delivered. Modifications can only occur after delivery via return or exchange.'
        }
    elif status == 'cancelled':
        return {
            'modification_allowed': False,
            'reason': 'Order is cancelled. No further modifications are possible.'
        }
    elif not status:
        return {
            'modification_allowed': False,
            'reason': 'Order status is missing. Unable to determine if modification is allowed.'
        }
    else:
        return {
            'modification_allowed': False,
            'reason': f'Item modification is not allowed: order status is "{status}".'
        }
@mcp.tool()
def prepare_pending_order_item_modifications(order_id, modifications):
    """
    {
      "type": "function",
      "function": {
        "name": "prepare_pending_order_item_modifications",
        "description": "Prepares and summarizes a batch of item modifications for a pending order without applying the changes. This function allows agents to stage multiple requested modifications, each specifying an original item to be replaced and a new item (with optional metadata like product type), check their structure for validity, and generate a clear, confirmation-ready checklist. The generated summary presents each requested replacement in detail and is designed for user review and approval prior to committing them with a one-time update operation. No further item edits can be performed after approval.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The unique identifier of the order; may include a '#' prefix."
            },
            "modifications": {
              "type": "string",
              "description": "A JSON-encoded array of objects, each specifying an item modification (with keys like 'original_item_id', 'new_item_id', and optional metadata such as 'product_type')."
            }
          },
          "required": ["order_id", "modifications"]
        }
      }
    }
    """
    import json

    # Defensive: Normalize order_id to string
    try:
        if not isinstance(order_id, str):
            order_id = str(order_id)
    except Exception:
        return 'Error: Could not convert order_id to string.'

    # Defensive: Ensure modifications is JSON string or can be converted
    try:
        if isinstance(modifications, list):
            mods = modifications  # Already a list
        elif isinstance(modifications, dict):
            # LLM might give a dict; wrap it into list
            mods = [modifications]
        elif isinstance(modifications, str):
            mods = json.loads(modifications)
        else:
            # Try to serialize and deserialize if unknown type
            mods = json.loads(json.dumps(modifications))
    except Exception as e:
        return f'Error: Could not parse modifications list. Details: {e}'
    if not isinstance(mods, list):
        return 'Error: Modifications must be a list of objects.'

    summary = []
    for i, mod in enumerate(mods):
        if not isinstance(mod, dict):
            return f'Error: Modification at position {i} is not an object.'
        original_id = str(mod.get('original_item_id', ''))
        new_id = str(mod.get('new_item_id', ''))
        # If original_id or new_id is empty, that's a problem
        if not original_id or not new_id:
            return (f"Error: Each modification must specify both 'original_item_id' and 'new_item_id'. "
                    f"Problem found at position {i}.")
        product_type = mod.get('product_type', None)
        action_line = f"Replace item {original_id} with {new_id}"
        if product_type:
            action_line += f" (Product: {product_type})"
        summary.append(action_line)
    checklist = f"Planned modifications for order {order_id}:\n"
    checklist += '\n'.join(f"- {s}" for s in summary)
    checklist += "\n\nPlease confirm all listed changes are correct. Once confirmed, all modifications will be applied in a single operation. No further item modifications will be allowed for this order after this action."
    return checklist
@mcp.tool()
def suggest_replacement_variant(product_id, current_item_id, prioritize_option_keys=None):
    """
    {
      "type": "function",
      "function": {
        "name": "suggest_replacement_variant",
        "description": "Suggest the most suitable available variant for a given product to replace a currently selected item. This function takes a product ID and the item ID of the current variant that needs replacement, and optionally a list of option keys to prioritize (such as color, size, or material). It examines all available variants of the product, compares their option values to the current variant, and ranks potential replacements by similarity, applying extra weight to matches on prioritized option keys if provided. The function returns a dictionary describing the suggested replacement variant if available, or an error string if no suitable replacement is found or if required data is missing.",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The unique identifier of the product whose variants should be considered for replacement."
            },
            "current_item_id": {
              "type": "string",
              "description": "The item ID corresponding to the variant being replaced."
            },
            "prioritize_option_keys": {
              "type": ["array", "null"],
              "items": {"type": "string"},
              "description": "An optional list of option keys (e.g., ['color', 'size']) to prioritize during the replacement selection process."
            }
          },
          "required": ["product_id", "current_item_id"]
        }
      }
    }
    """
    import json
    # Defensive conversion: ensure product_id and current_item_id are str
    try:
        product_id = str(product_id)
    except Exception as e:
        return f"Invalid product_id: {repr(e)}"
    try:
        current_item_id = str(current_item_id)
    except Exception as e:
        return f"Invalid current_item_id: {repr(e)}"
    # Defensive: handle prioritize_option_keys - can be list, string (comma separated), or None
    if prioritize_option_keys is None:
        prioritized = []
    elif isinstance(prioritize_option_keys, str):
        # e.g., "color,size" or "[\"color\", \"size\"]"
        try:
            if prioritize_option_keys.strip().startswith("["):
                prioritized = json.loads(prioritize_option_keys)
                if not isinstance(prioritized, list):
                    prioritized = [str(prioritized)]
                prioritized = [str(x) for x in prioritized]
            else:
                prioritized = [x.strip() for x in prioritize_option_keys.split(",") if x.strip()]
        except Exception:
            prioritized = []
    elif isinstance(prioritize_option_keys, list):
        prioritized = [str(x) for x in prioritize_option_keys if x is not None]
    else:
        # Unknown type, ignore
        prioritized = []

    try:
        prod_details = get_product_details(product_id)
    except Exception as e:
        return f"Failed to fetch product details: {repr(e)}"
    # Handle possible stringified JSON (as sometimes expected from LLM wrappers)
    if isinstance(prod_details, str):
        try:
            prod_details = json.loads(prod_details)
        except:
            return "Unable to retrieve product details."
    if not isinstance(prod_details, dict):
        return "Malformed product details."
    variants = prod_details.get('variants', {})
    if isinstance(variants, list):
        variants = {str(v.get('item_id')): v for v in variants if isinstance(v, dict) and 'item_id' in v}
    elif not isinstance(variants, dict):
        return "Product variants missing or malformed."

    # Locate the current item's options
    current_opts = None
    for v in variants.values():
        try:
            if str(v.get('item_id')) == str(current_item_id):
                current_opts = v.get('options', {})
                break
        except Exception:
            continue
    if not current_opts or not isinstance(current_opts, dict):
        return "Current item options not found."
    # Pick all available variants (excluding the one being replaced)
    available = []
    for v in variants.values():
        try:
            if v.get('available', False) and str(v.get('item_id')) != str(current_item_id):
                available.append(v)
        except Exception:
            continue
    if not available:
        return "No available replacement variants."

    def variant_score(v):
        opts = v.get('options', {})
        if not isinstance(opts, dict):
            opts = {}
        match = sum((opts.get(k) == current_opts.get(k)) for k in current_opts)
        prioritized_bonus = 0
        for key in prioritized:
            val = current_opts.get(key)
            if key in opts and opts[key] == val:
                prioritized_bonus += 10
        return match + prioritized_bonus

    try:
        available.sort(key=variant_score, reverse=True)
    except Exception:
        return "Error ranking available variants."
    best = available[0] if available else None
    if not best:
        return "No suitable replacement variant found."
    return best
@mcp.tool()
def confirm_and_execute_exchange_delivered_order_items(order_id, item_ids, new_item_ids, payment_method_id, user_confirmation):
    '''
    {
      "type": "function",
      "function": {
        "name": "confirm_and_execute_exchange_delivered_order_items",
        "description": "Prompts the user for a final yes/no confirmation before proceeding to exchange one or more items in a delivered order. If the user confirms ('yes'), the function will execute the exchange by calling exchange_delivered_order_items with the provided order and item data. If the user does not confirm, the function halts the operation and returns an aborted message. This ensures that all exchanges are intentional and explicitly approved. All arguments must be strings: item_ids and new_item_ids should be provided as JSON string arrays or lists of strings representing the item IDs. This function should be used when user consent is required before making changes to delivered orders.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {"type": "string", "description": "Unique identifier for the order."},
            "item_ids": {"type": "string", "description": "JSON array (string) or list of item IDs (as strings) to exchange from the order."},
            "new_item_ids": {"type": "string", "description": "JSON array (string) or list of replacement item IDs (as strings)."},
            "payment_method_id": {"type": "string", "description": "Identifier for the payment method to use for any additional charges or refunds."},
            "user_confirmation": {"type": "string", "description": "User's confirmation response; must be 'yes' to proceed with the exchange."}
          },
          "required": ["order_id", "item_ids", "new_item_ids", "payment_method_id", "user_confirmation"]
        }
      }
    }
    '''
    import json
    # Normalize and validate user_confirmation
    if str(user_confirmation).strip().lower() == 'yes':
        # Attempt to parse item_ids and new_item_ids into lists
        def parse_items(items):
            if isinstance(items, list):
                return [str(i) for i in items]
            if isinstance(items, str):
                items_str = items.strip()
                # Try to parse as JSON array
                try:
                    parsed = json.loads(items_str)
                    if isinstance(parsed, list):
                        return [str(i) for i in parsed]
                except Exception:
                    pass
                # Try splitting comma-separated or space-separated string
                if ',' in items_str:
                    return [i.strip() for i in items_str.split(',') if i.strip()]
                if ' ' in items_str:
                    return [i.strip() for i in items_str.split(' ') if i.strip()]
                if items_str:
                    return [items_str]
            return []
        try:
            parsed_item_ids = parse_items(item_ids)
            parsed_new_item_ids = parse_items(new_item_ids)
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to parse item_ids or new_item_ids: {e}'}
        if not parsed_item_ids or not parsed_new_item_ids:
            return {'status': 'error', 'message': 'Parsed item_ids or new_item_ids is empty or invalid.'}
        try:
            return exchange_delivered_order_items(order_id, parsed_item_ids, parsed_new_item_ids, payment_method_id)
        except Exception as e:
            return {'status': 'error', 'message': f'Exchange execution failed: {e}'}
    else:
        return {'status': 'aborted', 'message': 'Exchange cancelled by user confirmation.'}
@mcp.tool()
def return_all_delivered_order_items(order_id, payment_method_id):
    """
    {
      "type": "function",
      "function": {
        "name": "return_all_delivered_order_items",
        "description": "Return all items from a delivered order in a single operation by submitting a return request for all item IDs in the specified order to the selected refund payment method. This function streamlines the process for users who wish to return an entire delivered order, handling the retrieval of item IDs and the return submission in one step. If an error occurs while retrieving items, the error message is returned. Otherwise, the function returns the response from processing the return for all applicable item IDs.",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The ID of the delivered order to return items from (including the '#' if present)."
            },
            "payment_method_id": {
              "type": "string",
              "description": "The payment method ID to receive the refund (e.g., a specific gift card or the original payment method)."
            }
          },
          "required": ["order_id", "payment_method_id"]
        }
      }
    }
    """
    # Defensive: convert order_id and payment_method_id to string if possible
    try:
        order_id = str(order_id)
        payment_method_id = str(payment_method_id)
    except Exception as e:
        return f"Error: Failed to convert arguments to string. order_id={order_id}, payment_method_id={payment_method_id}. Exception: {e}"

    # Retrieve all items in the given order
    try:
        items = get_all_items_in_order(order_id)
    except Exception as e:
        return f"Error retrieving items for order_id={order_id}: {e}"

    if isinstance(items, str):  # error returned (string error message)
        return items
    if not isinstance(items, list):
        return f"Error: Items returned is not a list for order_id={order_id}. Response: {items}"

    # Extract item_ids from items list, check structure
    item_ids = []
    try:
        for item in items:
            if isinstance(item, dict) and 'item_id' in item:
                item_ids.append(item['item_id'])
            else:
                return f"Error: Item in items missing 'item_id' or not a dict. Problematic item: {item}"
    except Exception as e:
        return f"Error processing item list for order_id={order_id}: {e}"
    
    if not item_ids:
        return f"No items with 'item_id' found to return in order {order_id}."
    
    # Defensive: call return operation, catch errors
    try:
        response = return_delivered_order_items(order_id=order_id, item_ids=item_ids, payment_method_id=payment_method_id)
    except Exception as e:
        return f"Error submitting return for order {order_id}: {e}"
    return response
@mcp.tool()
def get_pending_orders_for_user(user_id):
    """
    {
      "type": "function",
      "function": {
        "name": "get_pending_orders_for_user",
        "description": "Fetches a list of order IDs that belong to the specified user and are currently in the 'pending' state. This function is useful for determining all pending and therefore updatable orders for a user, such as for bulk address modifications or status updates. It converts the provided user_id to string, retrieves user details, collects all associated order IDs, checks the status of each order, and includes only those currently marked as 'pending'. If user details retrieval fails, it returns an error string.",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "The user ID whose pending orders are to be retrieved."
            }
          },
          "required": ["user_id"]
        }
      }
    }
    """
    try:
        # Try to ensure user_id is a string
        if isinstance(user_id, dict) and 'user_id' in user_id:
            _user_id = user_id['user_id']
        else:
            _user_id = user_id
        _user_id = str(_user_id)
        user_details = get_user_details(_user_id)
        if isinstance(user_details, str):
            return user_details  # error string or message already
        if not isinstance(user_details, dict):
            return f"Error: Invalid user details structure for user_id {_user_id}"  # Defensive error
        order_ids = user_details.get("orders", [])
        if not isinstance(order_ids, list):
            return f"Error: 'orders' field malformed or missing for user_id {_user_id}"
        pending_orders = []
        for oid in order_ids:
            order = get_order_details(oid)
            if isinstance(order, str):
                continue  # Couldn't fetch order details; skip
            if not isinstance(order, dict):
                continue  # Malformed; skip
            status = str(order.get("status", "")).lower()
            if status.startswith("pending"):
                pending_orders.append(str(order.get("order_id", oid)))
        return pending_orders
    except Exception as e:
        return f"Error: Exception occurred in get_pending_orders_for_user: {str(e)}"
@mcp.tool()
def summarize_user_requested_actions(conversation_history):
    """
    {
      "type": "function",
      "function": {
        "name": "summarize_user_requested_actions",
        "description": "Analyzes a conversation history (as a string or serialized message list) and returns a structured summary (such as a JSON dictionary) containing only those return, exchange, or modification actions that have been explicitly requested and confirmed by the user. The function filters out suggestions or prompts generated by the assistant, ensuring that only user-initiated and user-confirmed actions are included. This summary can then be used to batch accurate tool calls, preventing unnecessary or premature actions by the agent. The output dictionary contains for each actionable request: the type of action (return, exchange, or modify), item and order details, payment/exchange/refund info if provided, and an explicit flag for user confirmation. Only actions confirmed by the user are included.",
        "parameters": {
          "type": "object",
          "properties": {
            "conversation_history": {
              "type": "string",
              "description": "Serialized list of conversation messages, either as raw text or a JSON-encoded array of message objects."
            }
          },
          "required": ["conversation_history"]
        }
      }
    }
    """
    import json
    import logging

    # Ensure conversation_history is a string (if it's dict/list, try to dump as json string)
    if not isinstance(conversation_history, str):
        try:
            conversation_history = json.dumps(conversation_history)
        except Exception as e:
            return json.dumps({
                "error": "Invalid argument type for conversation_history. Expected str or serialized JSON.",
                "detail": str(e),
                "status": "error_argument_type"
            })
    
    # Attempt to parse the conversation history. Accept either a JSON array or fallback to split by lines.
    try:
        history = json.loads(conversation_history)
        if isinstance(history, dict) and "messages" in history:
            history = history["messages"]
        if not isinstance(history, list):
            raise ValueError("Parsed conversation_history JSON is not a list.")
    except Exception:
        # fallback: try to split lines with role prefix
        try:
            msgs = [l for l in conversation_history.split('\n') if ':' in l]
            history = []
            for line in msgs:
                r, c = line.split(':', 1)
                history.append({'role': r.strip().lower(), 'content': c.strip()})
        except Exception as e:
            return json.dumps({
                "error": "Could not parse conversation_history. Expected a JSON-encoded list or a newline separated transcript.",
                "detail": str(e),
                "status": "error_parse"
            })
    
    # Validate that history is a list of dicts with at least 'role' and 'content'
    if (not isinstance(history, list)) or not all(isinstance(msg, dict) and 'role' in msg and 'content' in msg for msg in history):
        return json.dumps({
            "error": "conversation_history could not be interpreted as an array of message objects.",
            "status": "error_structure"
        })

    # State trackers
    plan = {'return': [], 'exchange': [], 'modify': []}
    temp_return = []
    temp_exchange = []
    temp_modify = []
    confirmation_flag = False
    last_summary_plan = None
    last_summary_message_idx = None

    # Look for structured user confirmations in progressive plan discussions.
    for i, msg in enumerate(history):
        role = str(msg.get('role', '')).lower()
        content = str(msg.get('content', '') or '')
        # The assistant's plan summary before explicit confirmation
        if role == 'assistant' and any(k in content.lower() for k in ['here is', "here's", 'the plan', 'here are the items', 'updated plan']):
            # Parse plan items by simple keyword matching and context.
            last_summary_plan = {'return': [], 'exchange': [], 'modify': []}
            for section in ['return', 'exchange', 'modify']:
                if section in content.lower():
                    # Find lines under each action keyword
                    lines = [l.strip('-* .') for l in content.split('\n') if l.strip() and ('- ' in l or '*' in l)]
                    for line in lines:
                        if section in line.lower():
                            continue
                        if "order" in line or 'from order' in line:
                            last_summary_plan[section].append(line)
                        elif len(lines) > 0:
                            last_summary_plan[section].append(line)
            last_summary_message_idx = i
        # User explicit confirmation (final approval)
        if role == 'user' and any(
                p in content.lower() for p in ["proceed", "this is perfect", "this looks good", "looks almost right", "go ahead", "please do it", "let's do it", "all good", "yes, proceed"]):
            # If confirmation comes after the last summary, assume the last plan is approved
            confirmation_flag = True
            break
        # User says 'not yet', 'add', 'wait', or 'one more change', revoke confirmation state
        if role == 'user' and any(p in content.lower() for p in ["not yet", "add", "no,", "wait", "one more", "change", "could we", 'i just realized', 'instead', 'prefer', 'rather', 'let me think']):
            confirmation_flag = False
            # Continue building plan
    # Build summary output if confirmed
    summary = {'actions': []}
    if confirmation_flag and last_summary_plan is not None:
        for action_type in ['return', 'exchange', 'modify']:
            for detail in last_summary_plan[action_type]:
                summary['actions'].append({'action_type': action_type, 'detail': detail})
    # Else, mark as no confirmed actions
    if not summary['actions']:
        summary['status'] = 'no_confirmed_actions'
    else:
        summary['status'] = 'confirmed_actions'
    return json.dumps(summary)
@mcp.tool()
def plan_order_modifications_sequentially(order_id, modifications=None, modification_types=None, **kwargs):
    '''
    {
      "type": "function",
      "function": {
        "name": "plan_order_modifications_sequentially",
        "description": "Plans and sequences multiple types of modifications on a pending order, ensuring that irreversible modifications (such as item changes) are performed last and that all changes comply with order status and business logic. Given an order_id, and two JSON-encoded lists: one for modification details, and one for the order/type of each intended modification, the function validates current order status, checks the feasibility and safety of each modification in sequence, and returns a step-by-step plan (as a JSON list of actions, parameters, and whether each is allowed), or an explicit error if risky or invalid. This is especially useful to avoid user mistakes when executing multiple order changes that have dependencies or irreversibility (e.g., item changes should occur after all address/payment changes).",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    '''
    import json
    import collections.abc
    # Robustly handle alternate argument naming from trajectory
    if modifications is None and modification_types is None and kwargs:
        # Accept alternate keys (frequent in some API trials)
        if 'modification_details' in kwargs:
            modifications = kwargs['modification_details']
        if 'modification_order' in kwargs:
            modification_types = kwargs['modification_order']
    # Parse modifications
    try:
        if isinstance(modifications, str):
            mods = json.loads(modifications)
        elif isinstance(modifications, collections.abc.Sequence) and not isinstance(modifications, str):
            mods = list(modifications)
        else:
            mods = [modifications]
    except Exception as e:
        return json.dumps({"error": f"Could not parse modifications: {str(e)}"})
    # Parse modification_types
    try:
        if isinstance(modification_types, str):
            types = json.loads(modification_types)
        elif isinstance(modification_types, collections.abc.Sequence) and not isinstance(modification_types, str):
            types = list(modification_types)
        else:
            types = [modification_types]
    except Exception as e:
        return json.dumps({"error": f"Could not parse modification_types: {str(e)}"})
    # Fallback for common bad API calls: if we get a list of dict containing a 'type' key, synthesize types
    if (not types or (isinstance(types, list) and all(t is None or (isinstance(t, str) and not t.strip()) for t in types))) and mods and isinstance(mods, list) and all(isinstance(m, dict) for m in mods):
        # Try to auto-extract types
        types = [m.get('type', '') for m in mods]
    # If still types is missing or mismatch, fail
    if not isinstance(mods, list) or not isinstance(types, list):
        return json.dumps({"error": "modifications and modification_types should be lists after parsing."})
    if len(mods) != len(types):
        return json.dumps({"error": f"Length mismatch: {len(mods)} modifications and {len(types)} modification_types."})

    # Normalize modification type strings (e.g., 'modify_item' -> 'items', 'modify_address' -> 'address')
    norm_map = {
        'modify_item': 'items',
        'modify_items': 'items',
        'item': 'items',
        'items': 'items',
        'modify_address': 'address',
        'address': 'address',
        'modify_payment': 'payment',
        'payment': 'payment',
    }
    norm_types = [norm_map.get(str(t).strip().lower(), str(t).strip().lower()) for t in types]

    # Pre-checks
    steps = []
    try:
        order_details = get_order_details(str(order_id))
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch order details: {str(e)}"})
    if isinstance(order_details, str):
        try:
            order_details_obj = json.loads(order_details)
        except Exception as e:
            return json.dumps({"error": f"Unable to retrieve order details: {order_details}. Parse error: {str(e)}"})
        order_details = order_details_obj
    if not isinstance(order_details, dict):
        return json.dumps({"error": f"Unrecognized order_details received: {repr(order_details)}"})
    status = order_details.get("status", "unknown")
    irreversible_types = {"items"}
    irreversible_done = False
    for idx, t_str in enumerate(norm_types):
        cur_mod = mods[idx]
        if status not in ["pending", "pending (item modified)"]:
            steps.append({"action": t_str, "params": cur_mod, "allowed": False, "reason": f"Order status is {status}. Only pending orders allow modifications."})
            continue
        if status == "pending (item modified)":
            steps.append({"action": t_str, "params": cur_mod, "allowed": False, "reason": "Items have already been modified once for this order. No further changes allowed."})
            continue
        if irreversible_done:
            steps.append({"action": t_str, "params": cur_mod, "allowed": False, "reason": "Cannot perform modification after item changes have been made."})
            continue
        if t_str == "address":
            steps.append({"action": "modify_pending_order_address", "params": cur_mod, "allowed": True})
        elif t_str == "payment":
            steps.append({"action": "modify_pending_order_payment", "params": cur_mod, "allowed": True})
        elif t_str == "items":
            steps.append({"action": "modify_pending_order_items", "params": cur_mod, "allowed": True})
            irreversible_done = True
        else:
            steps.append({"action": t_str, "params": cur_mod, "allowed": False, "reason": "Unknown modification type."})
    # Detect item not last
    found_item = False
    for ii, t_str in enumerate(norm_types):
        if t_str == "items":
            found_item = True
        elif found_item:
            steps[ii]["allowed"] = False
            steps[ii]["reason"] = "All item modifications must be performed last, since further changes will be blocked. Please re-order steps to do all other modifications first."
    return json.dumps(steps)
if __name__ == "__main__":
    mcp.run(transport='stdio')
