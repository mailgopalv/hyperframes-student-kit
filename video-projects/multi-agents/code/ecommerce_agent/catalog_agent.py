"""Sub-agent 1: shows the products and lets the customer pick some."""

import os

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .data import PRODUCTS

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def list_products() -> dict:
    """Returns every product in the store with its id, name and price."""
    return {"products": PRODUCTS}


def add_to_cart(product_id: str, quantity: int, tool_context: ToolContext) -> dict:
    """Adds a product to the customer's cart (stored in the session state)."""
    if product_id not in PRODUCTS:
        return {"error": f"No product found with id {product_id}"}

    cart = tool_context.state.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    tool_context.state["cart"] = cart
    return {"status": "added", "cart": cart}


catalog_agent = Agent(
    name="catalog_agent",
    model=MODEL,
    description="Shows the products and adds the ones the customer picks to the cart.",
    instruction="""
    You help {user_name?} browse the store.
    - Use list_products to show the products with their prices.
    - When the customer picks a product, use add_to_cart.
    - When the customer has finished choosing, transfer to cart_agent.
    """,
    tools=[list_products, add_to_cart],
)
