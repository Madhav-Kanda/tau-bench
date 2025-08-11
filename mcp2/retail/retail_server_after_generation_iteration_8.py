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
    '''
    {
      "type": "function",
      "function": {
        "name": "get_item_tracking_info",
        "description": "Retrieves the tracking number(s) and fulfillment details specifically for the provided item ID within a given order. This function is useful when an order contains multiple items that may be fulfilled and shipped separately, allowing users to obtain tracking and shipping information solely for the desired item, as opposed to the whole order. The function returns a list of fulfillment records, each represented as a dictionary with fields such as tracking_id (list), carrier (optional), fulfilled_items (list), and status (string), but only includes those fulfillments that contain the specified item_id.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    '''
    import json
    # Attempt to robustly cast order_id and item_id for lookup: handle numbers/strings input by LLM
    try:
        order_id_cast = str(order_id)
        item_id_cast = str(item_id)
    except Exception as e:
        return {
            "error": "Invalid input types for order_id or item_id.",
            "details": str(e)
        }
    
    try:
        tracking_json = get_order_tracking_info(order_id_cast)
    except Exception as e:
        return {
            "error": "Failed to retrieve order tracking info.",
            "details": str(e)
        }

    # Try to decode tracking_json if it's a string, otherwise assume it's already a list/object
    try:
        if isinstance(tracking_json, str):
            fulfillments = json.loads(tracking_json)
        else:
            fulfillments = tracking_json
        if not isinstance(fulfillments, list):
            raise ValueError("Expected a list of fulfillment records.")
    except Exception as e:
        return {
            "error": "Could not parse fulfillments from tracking info.",
            "details": str(e)
        }
    filtered = []
    for fulfillment in fulfillments:
        fulfilled_items = fulfillment.get('fulfilled_items', [])
        # support fulfilled_items being a list of int/str and item_id as str/int
        # consider both direct and casted comparison
        match_found = False
        for item in fulfilled_items:
            if (item == item_id) or (str(item) == item_id_cast):
                match_found = True
                break
        if match_found:
            filtered.append(fulfillment)
    return filtered
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
if __name__ == "__main__":
    mcp.run(transport='stdio')
