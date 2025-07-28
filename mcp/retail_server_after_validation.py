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
