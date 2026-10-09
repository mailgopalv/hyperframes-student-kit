"""Sub-agent 3: confirms the details and places the order."""

import os
import uuid

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .cart_agent import view_cart

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def place_order(tool_context: ToolContext) -> dict:
    """Places the order for everything in the confirmed cart."""
    if not tool_context.state.get("cart_confirmed"):
        return {"error": "Please confirm the cart first"}
    summary = view_cart(tool_context)

    order_id = "ORD-" + uuid.uuid4().hex[:6].upper()
    tool_context.state["order_id"] = order_id
    tool_context.state["order_status"] = "placed"
    return {
        "order_id": order_id,
        "items": summary["items"],
        "total": summary["total"],
        "email": tool_context.state.get("user_email"),
    }


order_agent = Agent(
    name="order_agent",
    model=MODEL,
    description="Confirms the customer's details and places the order.",
    instruction="""
    You place the order for {user_name?}.
    - Use view_cart to show the final items. The total is {cart_total?}.
    - Confirm the delivery details: email {user_email?}, phone {user_phone?}.
    - When the customer says yes, use place_order and share the order id.
    """,
    tools=[view_cart, place_order],
)
