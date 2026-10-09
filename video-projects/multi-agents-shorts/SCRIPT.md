# Agent with Sub-Agents: Shorts

## Short 1: Stop building one giant AI agent
Your AI agent is doing way too much. Here's the fix.
> Hook: "1 AGENT, 7 JOBS" slams in over the overloaded red agent box.
The problem, the fix, and the one line of code that does it.
> Three pills: Problem · Fix · Code.
Picture an online store assistant. One agent saves the customer's details, lists products, adds to the cart, removes items, confirms the cart, and places the order.
> Tool chips fly out of the single agent, one per tool named.
That's seven tools and one giant instruction.
> "7 tools · 1 giant instruction" badge; the box turns red.
As it grows, it starts picking the wrong tool, and it's really hard to test.
> A wrong tool chip flashes; the box shakes with an OVERLOADED tag.
The fix: split the work. One root agent, like a front desk, and three sub-agents: catalog, cart and order.
> The same box turns blue and rises as ROOT; three sub-agents drop in below.
Each tool moves to the agent that's responsible for it.
> The tool chips fly to their owners.
In Google ADK, that's one line: sub_agents equals a list of your agents.
> Code card: sub_agents=[catalog_agent, cart_agent, order_agent].
Want the full build? Watch the full video, linked below.
> End card: "Full video ↓" with the main video's title.

## Short 2: How AI agents hand off a conversation
How does one AI agent hand a customer to another?
> Hook: a white pulse jumps between two agent boxes.
It comes down to three things: descriptions, one built-in tool, and a shared session.
> Three numbered cards stack in.
First, every agent has a description. The LLM reads them to decide who should answer next.
> Card 1: description quotes appear under each agent; the LLM scans them and picks one.
Second, as soon as you add sub-agents, Google ADK gives your agents a tool called transfer_to_agent.
> Card 2: the transfer_to_agent(...) chip.
Calling it hands control to another agent: down to a sub-agent, sideways to a sibling, or back up to the parent.
> The pulse travels down, sideways, then back up the tree with labels.
Only one agent is in control at a time.
> IN CONTROL tag; the other agents dim.
Third, they all share one session. Same history, same state. Nothing gets lost when control moves.
> Card 3: one session slab under all four agents.
Watch the full video, linked below.
> End card: "Full video ↓".

## Short 3: The parameter your AI never sees
There's a parameter in your ADK tools that the AI never sees.
> Hook: the function signature with tool_context blurred, then revealed.
What it is, why it's there, and the one mistake to avoid.
> Three pills: What · Why · The mistake.
It's called tool_context. When the LLM calls save customer details, it only sees name, email and phone.
> "What the LLM sees" card: name, email, phone.
ADK hides tool_context from the model, then passes it in when the tool runs. It spots it by its type hint, ToolContext.
> "What your function gets" card: tool_context added by ADK.
Through it, your tool reaches the session. Read state like a dictionary: state dot get. Write it the same way: state, key, equals value.
> READ / WRITE code lines.
ADK saves every write to the session.
> The write flows into an amber session.state box.
The mistake? Changing a dictionary in place isn't saved. Always assign it back.
> Red ✕ on cart["P-101"] = 1, green ✓ on tool_context.state["cart"] = cart.
The full walkthrough is in my full video, linked below.
> End card: "Full video ↓".

## Short 4: Watch the state grow across 4 AI agents
Four AI agents, one shopping trip, and one notebook they all share.
> Hook: four agent boxes around one amber notebook.
Let's watch the session state grow, one agent at a time.
> An empty state panel: { }.
Asha shares her name, email and phone. The root agent saves three keys, then hands her to the catalog agent, which adds a cart.
> user_name, user_email, user_phone appear; pulse to catalog; the cart key appears.
The cart agent edits it, then sends her back to the catalog for a charger, and back again.
> The cart value updates; the pulse goes back and forth.
When she's happy, it saves the total and marks the cart confirmed.
> cart_total and cart_confirmed appear.
The order agent already knows her email and phone, because it reads them from state, and it adds the order ID and status.
> The email and phone rows glow blue (read); order_id and order_status appear.
Eight keys, four agents, one shared session. Watch the full video, linked below.
> All 8 keys lit, tagged by agent; end card "Full video ↓".

## Short 5: Run a multi-agent app in four commands
Run a multi-agent AI app in four commands.
> Hook: a big "4" next to a terminal.
Set up, install, add your key, and run.
> Four step pills.
One: python dash m venv dot venv. That's a virtual environment, so this project's packages stay separate.
> Step 1: python -m venv .venv; a .venv folder appears.
Activate it: dot venv, Scripts, activate on Windows, or source dot venv slash bin slash activate on Mac and Linux.
> The Windows and Mac/Linux activate commands; the prompt shows (.venv).
Two: pip install dash r requirements dot txt.
> Step 2: pip install -r requirements.txt.
Three: put your Gemini API key in a dot env file.
> Step 3: .env with GOOGLE_API_KEY=…
Four: adk web. Open localhost 8000, and watch the State tab.
> Step 4: adk web; the State tab with the final state.
The full step-by-step is in my full video, linked below.
> End card: "Full video ↓".
