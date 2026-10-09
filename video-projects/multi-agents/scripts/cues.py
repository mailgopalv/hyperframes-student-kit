"""Narration cues -> timings. Single source of truth for SCRIPT.md and composition timing.
Run from the project folder: python scripts/cues.py
Writes scripts/cues.json + SCRIPT.md and prints each chapter's cue start times (chapter-local)."""
import json
import math
import pathlib

WPS = 140 / 60          # speaking rate, words per second
GAP = 0.8               # breath after each line
LEAD = {"ch0": 1.2}     # silent lead-in before a chapter's first line (default 0.6)
TAIL = 1.5              # hold after a chapter's last line (the whip lands here)
OUTRO_HOLD = 6.0        # silent CTA hold after the very last line

CHAPTERS = [
 ("ch0", "Title", [
  "In the last video, we built one AI agent that could answer questions about orders and products.",
  "Today we go one step further. We'll build an agent that has sub-agents: a small team of agents that work together.",
  "We'll use Google's Agent Development Kit, ADK, and build a simple online store assistant.",
 ]),
 ("ch1", "What is an agent?", [
  "Let's start with the basics. What is an agent?",
  "An agent is made of three parts. First, a model: the LLM that does the thinking.",
  "Second, instructions: plain English that tells the model what its job is and how to behave.",
  "And third, tools: normal Python functions the agent can call to actually do things, like look up a product.",
  "When a user sends a message, the agent reads it, decides if it needs a tool, calls the tool, and uses the result to write a reply.",
  "In ADK, that's just one Agent object: a name, a model, an instruction, and a list of tools.",
 ]),
 ("ch2", "What is a session?", [
  "Now, where does the conversation live? In ADK, every conversation is stored in a session.",
  "Forget about agents for a moment, and just look at the session itself.",
  "A session has an ID, it knows which user it belongs to, and it has two important parts: events and state.",
  "Events are the history. Every message the user sends becomes an event.",
  "Every reply becomes an event. Even tool calls and tool results are recorded as events. The list just keeps growing.",
  "State is different. State is a small notebook of key-value pairs, like the customer's name, or what's in their cart.",
  "Right now the state is empty. Chatting alone doesn't fill it.",
  "State only changes when an agent's tool writes to it, using tool_context dot state. Keep an eye on this notebook. It's the star of this video.",
 ]),
 ("ch3", "The problem", [
  "Now let's build our store assistant. The simple approach is one agent that does everything.",
  "It needs to save the customer's details, list products, add to the cart, view the cart, remove items, confirm the cart, and place the order.",
  "That's seven tools and one giant instruction for a single agent.",
  "As it grows, the instructions get huge, the model starts picking the wrong tool, and it becomes very hard to test.",
 ]),
 ("ch4", "Sub-agents", [
  "The fix is to split the work. We keep one main agent, called the root agent, and give it three sub-agents.",
  "Each tool moves to the agent that's responsible for it.",
  "In code, that's just one line: sub_agents equals a list of the three agents.",
  "The root agent, ecommerce agent, is the front desk. It greets the customer and saves their name, email and phone into state.",
  "The catalog agent shows the products and adds the ones the customer picks. It writes the cart.",
  "The cart agent lets the customer review and change the cart. When they're happy, it confirms the cart and saves the total.",
  "And the order agent confirms the details and places the order. It writes the order ID and the status.",
  "Every agent has one clear responsibility, and each one adds its own piece to the state.",
 ]),
 ("ch5", "How control moves", [
  "So how does the conversation move from one agent to another?",
  "First, every agent has a description. The LLM reads these descriptions to decide who should handle the next message.",
  "Second, when you add sub-agents, ADK automatically gives the agents a tool called transfer to agent. Calling it hands control to another agent.",
  "Only one agent is in control at any time. The others wait.",
  "Control can move down from the root to a sub-agent, sideways to a sibling, or back up to the parent.",
  "And here's the key idea: they all share one single session. Same events, same state. Nothing gets lost when control moves.",
 ]),
 ("ch6", "The customer journey", [
  "Let's watch that happen with a real customer. On the left is the chat, in the middle the agent in control, and on the right, the session.",
  "Asha opens the chat and shares her name, email and phone number.",
  "The root agent calls save customer details. Three keys appear in state: user name, email and phone.",
  "Then it transfers control down to the catalog agent.",
  "Asha asks to see the products, and picks the headphones and two speakers.",
  "The catalog agent calls add to cart. A new key appears: cart.",
  "She's done choosing, so control moves sideways to the cart agent.",
  "The cart agent shows her cart. Asha removes the speakers, and the cart updates.",
  "Then she changes her mind. She wants to see chargers. The cart agent passes control back to the catalog agent.",
  "She adds a phone charger, and the catalog agent sends her back to the cart.",
  "Asha says it looks good. The cart agent calls confirm cart, which adds the cart total, and marks the cart as confirmed.",
  "Control moves to the order agent. It already knows Asha's email and phone. It simply reads them from state.",
  "Asha says yes, and place order adds the last two keys: the order ID, and the order status.",
  "Look at the state now. It grew step by step, and every agent added its own piece. That's the whole idea of sub-agents sharing one session.",
 ]),
 ("ch7", "The code", [
  "Now let's walk through the code. The full repository is linked in the description, so you can download it and follow along. It's fully working, and the README explains every step.",
  'Everything lives in one folder, ecommerce agent, with one file per agent, a small data file, and an init file.',
  "Let's start with agent dot py, the root agent. At the top, we import Agent and ToolContext from ADK, and our three sub-agents from their own files.",
  'The model name comes from an environment variable, so you can switch models without touching the code.',
  "Next is our first tool, save customer details. It's a normal Python function. Its docstring matters: the LLM reads it to understand what the tool does.",
  "Now look at the last parameter: tool_context, of type ToolContext. This is important, so let's slow down.",
  'When the LLM decides to call this tool, it only sees name, email and phone. ADK hides tool_context from the model. The model never fills it in.',
  'When the tool actually runs, ADK creates the tool context and passes it in for you. It spots it by its type hint, ToolContext.',
  'Through it, your tool can reach the current session. The part we care about is tool_context dot state, the shared notebook from earlier.',
  "Reading state works like a dictionary: state dot get. Writing does too: state, key, equals value. ADK records every write on the tool's event, and saves it to the session.",
  "That's why it's in the parameters. Without tool_context, a tool can't see or change the session. It also gives you things like the agent name and actions, but today we only need state.",
  'Back in the code: save customer details writes three keys, user name, email and phone, and returns a small result for the LLM.',
  'Then we build the root agent. A name, the model, and a description. The description is what the LLM reads when it decides who should handle a message.',
  'The instruction is plain English: greet the customer, collect and save their details, then transfer to the catalog agent.',
  "tools lists the root agent's own tool, and sub_agents lists the three agents it can hand off to. That one line turns a single agent into a team.",
  'Next, catalog agent dot py. It imports the products from data dot py, which is just a Python dictionary standing in for a real database.',
  'list products has no tool_context, because it never touches the session. It just returns the products.',
  'add to cart does need it. It checks the product exists, reads the cart from state, adds the quantity, and writes the cart back.',
  "Why write it back? ADK saves a change when you assign the key. Changing the dictionary in place isn't enough, so always assign it back.",
  'Its instruction uses user name, in curly braces, straight from state, and says when to hand off: when the customer has finished choosing, transfer to cart agent.',
  'cart agent dot py reuses add to cart from the catalog file, and adds three tools of its own.',
  'view cart reads the cart from state and works out the total. remove from cart deletes an item, and writes the cart back.',
  'confirm cart saves two new keys: the cart total, and cart confirmed, set to true.',
  'Its instruction covers both directions: back to the catalog agent to browse more, or forward to the order agent when the customer is happy.',
  'In order agent dot py, place order first reads cart confirmed from state, so nobody can check out an unconfirmed cart.',
  'Then it creates an order ID and writes the last two keys: order ID and order status.',
  "Its instruction pulls the name, total, email and phone straight from state. The question mark means: if the key isn't there yet, leave it blank instead of failing.",
  'Last, init dot py has one line that imports agent. ADK looks inside for a variable called root_agent, so keep that name.',
  "Now let's run it. First, a virtual environment. It's a private folder of Python packages for this one project, so its libraries don't clash with anything else on your computer.",
  'Create it with python dash m venv dot venv. That makes a folder called dot venv.',
  'Then activate it. On Windows, dot venv, Scripts, activate. On Mac or Linux, source dot venv slash bin slash activate. Your prompt now starts with dot venv.',
  'Now install the requirements: pip install dash r requirements dot txt. That installs Google ADK into the virtual environment.',
  'Copy dot env dot example to dot env, and paste in your Gemini API key from Google AI Studio.',
  'Finally, run adk web, open localhost 8000, and pick ecommerce agent. Open the State tab and watch it grow, one agent at a time.',
 ]),
 ("ch8", "Recap", [
  "So, to recap: one root agent, three sub-agents, each with its own job, all sharing one session.",
  "Control moves between them with transfer to agent, and the state grows as the customer moves along.",
  "The code is linked in the description. Try adding your own sub-agent, maybe a returns agent.",
  "If you found this useful, please like the video, and share it with a friend who's learning AI.",
  "And please leave a comment. Even a quick one, like 'I'm interested', tells me you want more on this topic, so I'll know to make more videos like this.",
  "Subscribe to Explore AI with Gopal for more hands-on AI videos. Thanks for watching, and see you in the next one.",
 ]),
]


# What the viewer sees during each line (same order as CHAPTERS).
ON_SCREEN = {
 "ch0": ["Last video's single support_agent box with three tool chips.",
         "The box rises and becomes a root agent; three sub-agents pop in below it.",
         "Title card: Agent with Sub-Agents."],
 "ch1": ["Heading: What is an agent?",
         "Agent card, row 01: Model (gemini-2.5-flash).",
         "Row 02: Instructions.",
         "Row 03: Tools (list_products()).",
         "Four-step loop on the right: message, decide, call tool, reply.",
         "The loop swaps for the Agent(...) code; each line lights up its matching row."],
 "ch2": ["Heading: What is a session? The Session card appears.",
         "A plain chat window slides in: just the conversation.",
         "id and user_id appear, then the EVENTS and STATE columns.",
         "The user's message appears and becomes event 1.",
         "Tool call, tool result and replies stack up as events 2 to 6.",
         "STATE lights up amber; example keys appear as dashed placeholders.",
         "Placeholders vanish; the braces pulse with 'empty'.",
         "The tool_context.state[...] chip appears; the STATE column glows."],
 "ch3": ["Heading: One agent that does everything. The ecommerce_agent box appears.",
         "Seven tool chips fly out of the box, one per tool you name.",
         "The box turns red and shows the OVERLOADED badge.",
         "Three pains appear; one tool chip flashes red as the wrong pick."],
 "ch4": ["The same box turns blue, rises to the top as the ROOT AGENT; three sub-agents appear.",
         "Each tool chip flies to the agent that owns it.",
         "Code chip: sub_agents=[catalog_agent, cart_agent, order_agent].",
         "Spotlight on ecommerce_agent; card: writes user_name, user_email, user_phone.",
         "Spotlight on catalog_agent; writes cart.",
         "Spotlight on cart_agent; writes cart_total, cart_confirmed.",
         "Spotlight on order_agent; writes order_id, order_status.",
         "All agents lit; +N keys badges; the full session.state strip."],
 "ch5": ["Heading: How control moves. The agent tree returns.",
         "Each agent's description appears; a user message; the LLM scans and picks cart_agent.",
         "transfer_to_agent(...) chip; a white pulse runs from the root down to cart_agent.",
         "IN CONTROL tag on cart_agent; the others dim.",
         "Pulse moves down to catalog, sideways to cart, then back up to the root.",
         "One shared session slab slides in; every agent links down to it."],
 "ch6": ["Three panels: chat (left), agents (middle), session (right).",
         "Asha's first message appears.",
         "STEP 1: save_customer_details(); user_name, user_email, user_phone rows appear.",
         "transfer_to_agent('catalog_agent'); pulse moves to catalog_agent.",
         "STEP 2: list_products(), then Asha's pick.",
         "add_to_cart() chips; the cart row appears.",
         "Pulse moves sideways to cart_agent.",
         "STEP 3: view_cart(), remove_from_cart(); the cart value updates.",
         "Asha asks for chargers; pulse goes back to catalog_agent.",
         "add_to_cart('P-104'); cart updates; pulse returns to cart_agent.",
         "STEP 4: confirm_cart(); cart_total and cart_confirmed rows appear.",
         "Pulse to order_agent; the email and phone rows flash blue (being read).",
         "STEP 5: place_order(); order_id and order_status rows appear.",
         "Heading changes; each agent lights up with the rows it wrote."],
 "ch7": ['Heading: Walking through the code. A repo card: link in the description, fully working, complete README.',
         'Explorer shows the folder; the editor lists each file and its job.',
         'agent.py, lines 1 to 10: the imports are highlighted.',
         'Line 12: MODEL = os.getenv(...) is highlighted.',
         'save_customer_details: the signature, then the docstring are highlighted.',
         'The tool_context: ToolContext parameter glows.',
         'ToolContext panel. Left: what the LLM sees (name, email, phone only).',
         'Right: what your function gets. tool_context is added by ADK.',
         'Flow: LLM, then ADK adds tool_context, then your function, then session.state.',
         "Read and write cheat sheet; 'saved as state_delta on the tool's event'.",
         'Tools with and without tool_context; extra fields: agent_name, actions, artifacts.',
         'Back in agent.py, the three state writes are highlighted amber, then the return.',
         'root_agent: name, model, description are highlighted.',
         'The instruction block is highlighted.',
         'tools, then the sub_agents line glows.',
         'data.py (five products), then catalog_agent.py imports.',
         'list_products is highlighted; a note says no tool_context is needed.',
         'add_to_cart: check, read, update, write back, one line at a time.',
         'The write-back line glows with a tip: always assign it back.',
         'The catalog instruction: {user_name?} and the transfer line are highlighted.',
         'cart_agent.py imports; the reused add_to_cart is highlighted.',
         'view_cart, then remove_from_cart are highlighted.',
         'confirm_cart: the two state writes are highlighted amber.',
         'The two transfer lines in the cart instruction are highlighted.',
         'place_order: the cart_confirmed check is highlighted.',
         'The two final state writes are highlighted amber.',
         'The order instruction: the {placeholders} glow, then the ? marks pop.',
         '__init__.py (one line), then root_agent in agent.py.',
         "Setup: diagram of your computer's Python vs a project .venv folder.",
         'Terminal: python -m venv .venv; a .venv folder appears in the explorer.',
         'Activate commands for Windows and Mac/Linux; the prompt gains (.venv).',
         'pip install -r requirements.txt; requirements.txt is shown.',
         '.env.example to .env with a GOOGLE_API_KEY placeholder.',
         'adk web; the State tab with the final state.'],
 "ch8": ["Recap tree returns; 'One root. Three sub-agents. One shared session.'",
         "A hand-off glow runs across the tree; the eight state keys appear.",
         "Code in the description; a dashed returns_agent? box joins the tree.",
         "The recap slides away; the Explore AI with Gopal channel card appears with Like and Share lighting up.",
         "The Comment pill lights up; a sample comment 'I'm interested!' pops in.",
         "The Subscribe button pulses. It holds, then fades out."],
}


def fr(x):
    """Snap to a 30fps frame boundary."""
    return round(round(x * 30) / 30, 2)


def build():
    out, t = [], 0.0
    for cid, title, lines in CHAPTERS:
        local = LEAD.get(cid, 0.6)
        cues = []
        for i, text in enumerate(lines, 1):
            dur = len(text.split()) / WPS
            cues.append({"id": f"{cid}.{i}", "start": fr(local), "dur": fr(dur), "text": text})
            local += dur + GAP
        length = local - GAP + TAIL + (OUTRO_HOLD if cid == "ch8" else 0)
        length = math.ceil(length * 2) / 2
        out.append({"id": cid, "title": title, "start": fr(t), "duration": length, "cues": cues})
        t += length
    return out, t


def mmss(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


if __name__ == "__main__":
    chapters, total = build()
    root = pathlib.Path(__file__).resolve().parent.parent
    for ch in chapters:  # carry the on-screen notes into cues.json (the teleprompter shows them)
        for c, note in zip(ch["cues"], ON_SCREEN.get(ch["id"], [])):
            c["note"] = note
    (root / "scripts" / "cues.json").write_text(json.dumps({"title": "Agent with Sub-Agents", "total": total, "chapters": chapters}, indent=1))

    md = ["# Voiceover script: Agent with Sub-Agents (Google ADK)", "",
          f"**Runtime:** {mmss(total)}. The timestamps assume a relaxed pace of about 140 words per minute, with a short breath after each line.", "",
          "**How to use it:** read each line when its timestamp comes up. The *on screen* note tells you what the viewer is seeing, so you can point at it.",
          "You don't have to hit the times exactly. Record naturally, send me the audio, and I'll retime the animation to your delivery.", ""]
    for ch in chapters:
        md += [f"## {ch['title']}  ·  {mmss(ch['start'])} – {mmss(ch['start'] + ch['duration'])}", ""]
        notes = ON_SCREEN.get(ch["id"], [])
        for i, c in enumerate(ch["cues"]):
            md.append(f"**{mmss(ch['start'] + c['start'])}**  {c['text']}")
            if i < len(notes):
                md.append(f"<br>*On screen: {notes[i]}*")
            md.append("")
    (root / "SCRIPT.md").write_text("\n".join(md), encoding="utf-8")
    for ch in chapters:
        print(ch["id"], mmss(ch["start"]), ch["start"], ch["duration"], [(c["id"].split(".")[1], c["start"]) for c in ch["cues"]])
    print("TOTAL", mmss(total), total)
