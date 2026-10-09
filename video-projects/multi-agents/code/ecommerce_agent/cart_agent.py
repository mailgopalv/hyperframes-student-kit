"""Sub-agent 2: lets the customer review the cart, then add or remove items."""

import os

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .catalog_agent import add_to_cart
from .data import PRODUCTS

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def view_cart(tool_context: ToolContext) -> dict:
    """Returns the items in the cart and the total price."""
    cart = tool_context.state.get("cart", {})
    items = []
    total = 0.0
    for product_id, quantity in cart.items():
        product = PRODUCTS[product_id]
        items.append({"id": product_id, "name": product["name"], "quantity": quantity})
        total += product["price"] * quantity
    return {"items": items, "total": round(total, 2)}


def remove_from_cart(product_id: str, tool_context: ToolContext) -> dict:
    """Removes a product from the cart."""
    cart = tool_context.state.get("cart", {})
    if product_id not in cart:
        return {"error": f"{product_id} is not in the cart"}

    del cart[product_id]
    tool_context.state["cart"] = cart
    return {"status": "removed", "cart": cart}


def confirm_cart(tool_context: ToolContext) -> dict:
    """Locks in the cart: saves the total and marks the cart as confirmed."""
    summary = view_cart(tool_context)
    if not summary["items"]:
        return {"error": "The cart is empty"}

    tool_context.state["cart_total"] = summary["total"]
    tool_context.state["cart_confirmed"] = True
    return {"status": "confirmed", "total": summary["total"]}


cart_agent = Agent(
    name="cart_agent",
    model=MODEL,
    description="Shows the cart, adds or removes items, and confirms the cart.",
    instruction="""
    You manage the shopping cart for {user_name?}.
    - Start by using view_cart to show the items and the total.
    - Use add_to_cart or remove_from_cart when the customer asks for changes.
    - If the customer wants to browse more products, transfer to catalog_agent.
    - When the customer is happy, use confirm_cart, then transfer to order_agent.
    """,
    tools=[view_cart, add_to_cart, remove_from_cart, confirm_cart],
)
