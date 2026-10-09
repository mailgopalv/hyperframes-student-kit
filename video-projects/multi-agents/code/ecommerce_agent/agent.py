"""The main (root) agent: greets the customer and hands off to the sub-agents."""

import os

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .cart_agent import cart_agent
from .catalog_agent import catalog_agent
from .order_agent import order_agent

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def save_customer_details(name: str, email: str, phone: str,
                          tool_context: ToolContext) -> dict:
    """Saves the customer's name, email and phone number in the session state."""
    tool_context.state["user_name"] = name
    tool_context.state["user_email"] = email
    tool_context.state["user_phone"] = phone
    return {"status": "saved"}


root_agent = Agent(
    name="ecommerce_agent",
    model=MODEL,
    description="Collects customer details and routes to the right sub-agent.",
    instruction="""
    You are the front desk of an online store.
    1. Greet the customer and ask for their name, email and phone number.
    2. Save them with save_customer_details.
    3. Then transfer to catalog_agent so they can pick products.
    Later, route cart questions to cart_agent and checkout to order_agent.
    """,
    tools=[save_customer_details],
    sub_agents=[catalog_agent, cart_agent, order_agent],
)
