# Agent with Sub-Agents: an E-commerce Assistant (Google ADK)

A beginner-friendly, fully working example of **one main agent that hands the conversation to three sub-agents**, built with Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and a Gemini model.

It accompanies the YouTube video **"Agent with Sub-Agents"**. The video walks through every file shown here.

```
ecommerce_agent  (root: greets the customer, saves name, email, phone)
├── catalog_agent  (shows products, adds picks to the cart)
├── cart_agent     (shows the cart, adds / removes items, confirms the cart)
└── order_agent    (confirms the details, places the order)
```

All four agents share **one session**. As the customer moves from agent to agent, each agent adds its own keys to the session state:

| Agent | Adds to `session.state` |
|---|---|
| `ecommerce_agent` (root) | `user_name`, `user_email`, `user_phone` |
| `catalog_agent` | `cart` |
| `cart_agent` | edits `cart`, then adds `cart_total`, `cart_confirmed` |
| `order_agent` | `order_id`, `order_status` |

---

## What you'll learn

- How to connect agents with `sub_agents=[...]`
- How control moves between agents with ADK's built-in `transfer_to_agent` (down to a sub-agent, sideways to a sibling, and back)
- What a **session** is: **events** (the history) and **state** (the shared notebook)
- How tools read and write state through **`ToolContext`**
- How instructions read state with `{placeholders}`

---

## Project layout

```
code/
├── ecommerce_agent/
│   ├── __init__.py        # tells ADK where the agent is: "from . import agent"
│   ├── agent.py           # the root agent + save_customer_details tool
│   ├── catalog_agent.py   # sub-agent 1: list_products, add_to_cart
│   ├── cart_agent.py      # sub-agent 2: view_cart, remove_from_cart, confirm_cart
│   ├── order_agent.py     # sub-agent 3: place_order
│   └── data.py            # mock product catalog (stands in for a database)
├── .env.example           # copy to .env and add your API key
├── .gitignore             # keeps .venv/ and .env out of git
├── requirements.txt       # google-adk
└── README.md
```

---

## Prerequisites

- **Python 3.10 or newer**. Check with `python --version`.
- A **Gemini API key** (the free tier works):
  1. Go to **https://aistudio.google.com/api-keys**
  2. Click **Create API key**, and choose or create a Google Cloud project
  3. Copy the key. You'll paste it into `.env` in step 4 below.
- A code editor such as Visual Studio Code (optional, but recommended)

---

## Setup and run

Run these commands from inside the `code/` folder.

### 1. Create a virtual environment

A **virtual environment** is a private folder of Python packages for this one project. Anything you install goes into `.venv/` instead of your computer's global Python, so this project's libraries never clash with other projects. You create it once.

```bash
python -m venv .venv
```

This creates a folder called `.venv/`.

### 2. Activate it

Do this **every time you open a new terminal**.

| System | Command |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\activate` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| Mac / Linux | `source .venv/bin/activate` |

When it's active, your prompt starts with `(.venv)`. To leave it later, run `deactivate`.

> **PowerShell says "running scripts is disabled on this system"?** Run this once, then try again:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 3. Install the requirements

```bash
pip install -r requirements.txt
```

This installs Google ADK into `.venv/`.

### 4. Add your API key

Copy the example file:

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Mac / Linux
```

Then open `.env` and paste in your key:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```

`.env` is listed in `.gitignore`, so your key is never committed.

### 5. Run it

```bash
adk web
```

Open **http://localhost:8000**, pick **`ecommerce_agent`** from the dropdown, and start chatting.

To chat in the terminal instead of the browser, run `adk run ecommerce_agent`.

---

## Try this conversation

| You type | What happens |
|---|---|
| `Hi, I'm Asha. asha@example.com, 555-0101` | Root calls `save_customer_details`, then transfers **down** to `catalog_agent` |
| `What products do you have?` | `catalog_agent` calls `list_products` |
| `Headphones and 2 speakers, please. That's all.` | `add_to_cart` twice, then transfers **sideways** to `cart_agent` |
| `Remove the speakers.` | `cart_agent` calls `remove_from_cart` |
| `Actually, do you have chargers?` | `cart_agent` passes control **back** to `catalog_agent` |
| `Add one, please.` | `add_to_cart`, then back to `cart_agent` |
| `Looks good!` | `confirm_cart` saves `cart_total` and `cart_confirmed`, then transfers to `order_agent` |
| `Yes, place it.` | `place_order` saves `order_id` and `order_status` |

In `adk web`, open the **State** tab on the left and watch the keys appear one agent at a time. The **Events** tab shows every message, tool call and `transfer_to_agent` hand-off.

The LLM decides the exact wording and when to call each tool, so your conversation may look slightly different each time.

---

## How it works

### 1. `sub_agents` connects the team

```python
root_agent = Agent(
    ...
    tools=[save_customer_details],
    sub_agents=[catalog_agent, cart_agent, order_agent],
)
```

That one line turns a single agent into a team. ADK looks for a variable called **`root_agent`** in `agent.py`, so keep that name.

### 2. `description` helps the LLM choose

Every agent has a `description`. When control needs to move, the LLM reads these descriptions to pick the agent best suited to the next message.

### 3. `transfer_to_agent` moves control

Once an agent has sub-agents, ADK automatically gives the agents a built-in tool called `transfer_to_agent`. When the LLM calls it, control moves to that agent. Only **one agent is in control at a time**, and control can move:

- **down**, from the root to a sub-agent
- **sideways**, to a sibling (e.g. `catalog_agent` → `cart_agent`)
- **back up**, to the parent

Each instruction says when to hand off, e.g. *"When the customer has finished choosing, transfer to cart_agent."*

### 4. One shared session

Every agent works on the **same session**:

- **events**: the history. Every message, tool call, tool result and hand-off is recorded.
- **state**: a dictionary of key-value pairs, the shared notebook. Chatting alone doesn't change it. Only tools (and callbacks) write to it.

Nothing is lost when control moves, because every agent reads the same state.

### 5. `ToolContext` gives tools access to the session

```python
def save_customer_details(name: str, email: str, phone: str,
                          tool_context: ToolContext) -> dict:
    tool_context.state["user_name"] = name
    ...
```

- **The LLM never sees `tool_context`.** ADK removes it from the tool's schema, so the model only sees `name`, `email` and `phone`.
- **ADK passes it in for you** when the tool runs. It finds the parameter by its type hint, `ToolContext` (or by the name `tool_context`).
- **`tool_context.state`** is the shared session state:
  - read: `cart = tool_context.state.get("cart", {})`
  - write: `tool_context.state["cart"] = cart`
- ADK records each write as a `state_delta` on the tool's event, and the session saves it.
- **Always assign the value back.** Changing a dict in place (`cart["P-101"] = 1`) is not enough. The change is only recorded when you assign the key.
- Tools that don't touch the session don't need it. `list_products` has no `tool_context`.
- It also offers `agent_name`, `actions`, `save_artifact()`, `search_memory()` and more, which aren't needed in this project.

### 6. `{placeholders}` read state inside instructions

```python
instruction="""
You place the order for {user_name?}.
- Confirm the delivery details: email {user_email?}, phone {user_phone?}.
"""
```

ADK replaces `{user_name}` with `state["user_name"]` before the instruction reaches the LLM. The **`?`** makes the key optional: if it isn't in state yet, ADK leaves it blank instead of raising an error.

---

## File-by-file

| File | What's inside |
|---|---|
| `agent.py` | `save_customer_details` (writes 3 keys) and `root_agent` with `sub_agents=[...]` |
| `catalog_agent.py` | `list_products` (no state) and `add_to_cart` (read the cart, update it, write it back) |
| `cart_agent.py` | `view_cart`, `remove_from_cart`, and `confirm_cart` (writes `cart_total`, `cart_confirmed`); reuses `add_to_cart` |
| `order_agent.py` | `place_order`: checks `cart_confirmed`, writes `order_id` and `order_status` |
| `data.py` | `PRODUCTS`: five mock products with ids `P-101` to `P-105` |
| `__init__.py` | `from . import agent`, so ADK can find `root_agent` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `adk` is not recognized | The virtual environment isn't active. Run the activate command from step 2. |
| `ecommerce_agent` is missing from the dropdown | Run `adk web` from the `code/` folder (the folder that *contains* `ecommerce_agent/`). |
| `API key not valid` / missing key | Check `.env` is in the `code/` folder and `GOOGLE_API_KEY` has no quotes or spaces. |
| Model not found / quota errors | Set `GEMINI_MODEL` in `.env` to another model available to your key (e.g. a Flash-Lite model). |
| PowerShell blocks `activate` | See the `Set-ExecutionPolicy` tip in step 2. |

---

## Next step: add your own sub-agent

Try a `returns_agent`:

1. Create `ecommerce_agent/returns_agent.py` with a tool like `start_return(order_id, tool_context)` that writes `return_status` to state.
2. Give it a clear `description` and an instruction that says when to transfer back.
3. Import it in `agent.py` and add it to `sub_agents=[...]`.
4. Mention it in the root agent's instruction so the LLM knows when to route there.
