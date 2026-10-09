# Voiceover script: Agent with Sub-Agents (Google ADK)

**Runtime:** 14:07.0. The timestamps assume a relaxed pace of about 140 words per minute, with a short breath after each line.

**How to use it:** read each line when its timestamp comes up. The *on screen* note tells you what the viewer is seeing, so you can point at it.
You don't have to hit the times exactly. Record naturally, send me the audio, and I'll retime the animation to your delivery.

## Title  ·  0:00.0 – 0:27.0

**0:01.2**  In the last video, we built one AI agent that could answer questions about orders and products.
<br>*On screen: Last video's single support_agent box with three tool chips.*

**0:09.3**  Today we go one step further. We'll build an agent that has sub-agents: a small team of agents that work together.
<br>*On screen: The box rises and becomes a root agent; three sub-agents pop in below it.*

**0:19.1**  We'll use Google's Agent Development Kit, ADK, and build a simple online store assistant.
<br>*On screen: Title card: Agent with Sub-Agents.*

## What is an agent?  ·  0:27.0 – 1:18.5

**0:27.6**  Let's start with the basics. What is an agent?
<br>*On screen: Heading: What is an agent?*

**0:32.3**  An agent is made of three parts. First, a model: the LLM that does the thinking.
<br>*On screen: Agent card, row 01: Model (gemini-2.5-flash).*

**0:39.9**  Second, instructions: plain English that tells the model what its job is and how to behave.
<br>*On screen: Row 02: Instructions.*

**0:47.6**  And third, tools: normal Python functions the agent can call to actually do things, like look up a product.
<br>*On screen: Row 03: Tools (list_products()).*

**0:56.5**  When a user sends a message, the agent reads it, decides if it needs a tool, calls the tool, and uses the result to write a reply.
<br>*On screen: Four-step loop on the right: message, decide, call tool, reply.*

**1:08.9**  In ADK, that's just one Agent object: a name, a model, an instruction, and a list of tools.
<br>*On screen: The loop swaps for the Agent(...) code; each line lights up its matching row.*

## What is a session?  ·  1:18.5 – 2:25.5

**1:19.1**  Now, where does the conversation live? In ADK, every conversation is stored in a session.
<br>*On screen: Heading: What is a session? The Session card appears.*

**1:26.3**  Forget about agents for a moment, and just look at the session itself.
<br>*On screen: A plain chat window slides in: just the conversation.*

**1:32.7**  A session has an ID, it knows which user it belongs to, and it has two important parts: events and state.
<br>*On screen: id and user_id appear, then the EVENTS and STATE columns.*

**1:42.5**  Events are the history. Every message the user sends becomes an event.
<br>*On screen: The user's message appears and becomes event 1.*

**1:48.4**  Every reply becomes an event. Even tool calls and tool results are recorded as events. The list just keeps growing.
<br>*On screen: Tool call, tool result and replies stack up as events 2 to 6.*

**1:57.8**  State is different. State is a small notebook of key-value pairs, like the customer's name, or what's in their cart.
<br>*On screen: STATE lights up amber; example keys appear as dashed placeholders.*

**2:07.2**  Right now the state is empty. Chatting alone doesn't fill it.
<br>*On screen: Placeholders vanish; the braces pulse with 'empty'.*

**2:12.7**  State only changes when an agent's tool writes to it, using tool_context dot state. Keep an eye on this notebook. It's the star of this video.
<br>*On screen: The tool_context.state[...] chip appears; the STATE column glows.*

## The problem  ·  2:25.5 – 3:01.0

**2:26.1**  Now let's build our store assistant. The simple approach is one agent that does everything.
<br>*On screen: Heading: One agent that does everything. The ecommerce_agent box appears.*

**2:33.3**  It needs to save the customer's details, list products, add to the cart, view the cart, remove items, confirm the cart, and place the order.
<br>*On screen: Seven tool chips fly out of the box, one per tool you name.*

**2:44.8**  That's seven tools and one giant instruction for a single agent.
<br>*On screen: The box turns red and shows the OVERLOADED badge.*

**2:50.4**  As it grows, the instructions get huge, the model starts picking the wrong tool, and it becomes very hard to test.
<br>*On screen: Three pains appear; one tool chip flashes red as the wrong pick.*

## Sub-agents  ·  3:01.0 – 4:09.5

**3:01.6**  The fix is to split the work. We keep one main agent, called the root agent, and give it three sub-agents.
<br>*On screen: The same box turns blue, rises to the top as the ROOT AGENT; three sub-agents appear.*

**3:11.4**  Each tool moves to the agent that's responsible for it.
<br>*On screen: Each tool chip flies to the agent that owns it.*

**3:16.5**  In code, that's just one line: sub_agents equals a list of the three agents.
<br>*On screen: Code chip: sub_agents=[catalog_agent, cart_agent, order_agent].*

**3:23.3**  The root agent, ecommerce agent, is the front desk. It greets the customer and saves their name, email and phone into state.
<br>*On screen: Spotlight on ecommerce_agent; card: writes user_name, user_email, user_phone.*

**3:33.5**  The catalog agent shows the products and adds the ones the customer picks. It writes the cart.
<br>*On screen: Spotlight on catalog_agent; writes cart.*

**3:41.6**  The cart agent lets the customer review and change the cart. When they're happy, it confirms the cart and saves the total.
<br>*On screen: Spotlight on cart_agent; writes cart_total, cart_confirmed.*

**3:51.8**  And the order agent confirms the details and places the order. It writes the order ID and the status.
<br>*On screen: Spotlight on order_agent; writes order_id, order_status.*

**4:00.8**  Every agent has one clear responsibility, and each one adds its own piece to the state.
<br>*On screen: All agents lit; +N keys badges; the full session.state strip.*

## How control moves  ·  4:09.5 – 5:01.5

**4:10.1**  So how does the conversation move from one agent to another?
<br>*On screen: Heading: How control moves. The agent tree returns.*

**4:15.6**  First, every agent has a description. The LLM reads these descriptions to decide who should handle the next message.
<br>*On screen: Each agent's description appears; a user message; the LLM scans and picks cart_agent.*

**4:24.6**  Second, when you add sub-agents, ADK automatically gives the agents a tool called transfer to agent. Calling it hands control to another agent.
<br>*On screen: transfer_to_agent(...) chip; a white pulse runs from the root down to cart_agent.*

**4:35.2**  Only one agent is in control at any time. The others wait.
<br>*On screen: IN CONTROL tag on cart_agent; the others dim.*

**4:41.2**  Control can move down from the root to a sub-agent, sideways to a sibling, or back up to the parent.
<br>*On screen: Pulse moves down to catalog, sideways to cart, then back up to the root.*

**4:50.5**  And here's the key idea: they all share one single session. Same events, same state. Nothing gets lost when control moves.
<br>*On screen: One shared session slab slides in; every agent links down to it.*

## The customer journey  ·  5:01.5 – 6:55.0

**5:02.1**  Let's watch that happen with a real customer. On the left is the chat, in the middle the agent in control, and on the right, the session.
<br>*On screen: Three panels: chat (left), agents (middle), session (right).*

**5:14.5**  Asha opens the chat and shares her name, email and phone number.
<br>*On screen: Asha's first message appears.*

**5:20.4**  The root agent calls save customer details. Three keys appear in state: user name, email and phone.
<br>*On screen: STEP 1: save_customer_details(); user_name, user_email, user_phone rows appear.*

**5:28.5**  Then it transfers control down to the catalog agent.
<br>*On screen: transfer_to_agent('catalog_agent'); pulse moves to catalog_agent.*

**5:33.2**  Asha asks to see the products, and picks the headphones and two speakers.
<br>*On screen: STEP 2: list_products(), then Asha's pick.*

**5:39.5**  The catalog agent calls add to cart. A new key appears: cart.
<br>*On screen: add_to_cart() chips; the cart row appears.*

**5:45.5**  She's done choosing, so control moves sideways to the cart agent.
<br>*On screen: Pulse moves sideways to cart_agent.*

**5:51.0**  The cart agent shows her cart. Asha removes the speakers, and the cart updates.
<br>*On screen: STEP 3: view_cart(), remove_from_cart(); the cart value updates.*

**5:57.8**  Then she changes her mind. She wants to see chargers. The cart agent passes control back to the catalog agent.
<br>*On screen: Asha asks for chargers; pulse goes back to catalog_agent.*

**6:07.2**  She adds a phone charger, and the catalog agent sends her back to the cart.
<br>*On screen: add_to_cart('P-104'); cart updates; pulse returns to cart_agent.*

**6:14.4**  Asha says it looks good. The cart agent calls confirm cart, which adds the cart total, and marks the cart as confirmed.
<br>*On screen: STEP 4: confirm_cart(); cart_total and cart_confirmed rows appear.*

**6:24.6**  Control moves to the order agent. It already knows Asha's email and phone. It simply reads them from state.
<br>*On screen: Pulse to order_agent; the email and phone rows flash blue (being read).*

**6:33.6**  Asha says yes, and place order adds the last two keys: the order ID, and the order status.
<br>*On screen: STEP 5: place_order(); order_id and order_status rows appear.*

**6:42.1**  Look at the state now. It grew step by step, and every agent added its own piece. That's the whole idea of sub-agents sharing one session.
<br>*On screen: Heading changes; each agent lights up with the rows it wrote.*

## The code  ·  6:55.0 – 13:04.0

**6:55.6**  Now let's walk through the code. The full repository is linked in the description, so you can download it and follow along. It's fully working, and the README explains every step.
<br>*On screen: Heading: Walking through the code. A repo card: link in the description, fully working, complete README.*

**7:09.7**  Everything lives in one folder, ecommerce agent, with one file per agent, a small data file, and an init file.
<br>*On screen: Explorer shows the folder; the editor lists each file and its job.*

**7:19.1**  Let's start with agent dot py, the root agent. At the top, we import Agent and ToolContext from ADK, and our three sub-agents from their own files.
<br>*On screen: agent.py, lines 1 to 10: the imports are highlighted.*

**7:31.4**  The model name comes from an environment variable, so you can switch models without touching the code.
<br>*On screen: Line 12: MODEL = os.getenv(...) is highlighted.*

**7:39.5**  Next is our first tool, save customer details. It's a normal Python function. Its docstring matters: the LLM reads it to understand what the tool does.
<br>*On screen: save_customer_details: the signature, then the docstring are highlighted.*

**7:51.5**  Now look at the last parameter: tool_context, of type ToolContext. This is important, so let's slow down.
<br>*On screen: The tool_context: ToolContext parameter glows.*

**7:59.5**  When the LLM decides to call this tool, it only sees name, email and phone. ADK hides tool_context from the model. The model never fills it in.
<br>*On screen: ToolContext panel. Left: what the LLM sees (name, email, phone only).*

**8:11.9**  When the tool actually runs, ADK creates the tool context and passes it in for you. It spots it by its type hint, ToolContext.
<br>*On screen: Right: what your function gets. tool_context is added by ADK.*

**8:23.0**  Through it, your tool can reach the current session. The part we care about is tool_context dot state, the shared notebook from earlier.
<br>*On screen: Flow: LLM, then ADK adds tool_context, then your function, then session.state.*

**8:33.7**  Reading state works like a dictionary: state dot get. Writing does too: state, key, equals value. ADK records every write on the tool's event, and saves it to the session.
<br>*On screen: Read and write cheat sheet; 'saved as state_delta on the tool's event'.*

**8:47.3**  That's why it's in the parameters. Without tool_context, a tool can't see or change the session. It also gives you things like the agent name and actions, but today we only need state.
<br>*On screen: Tools with and without tool_context; extra fields: agent_name, actions, artifacts.*

**9:02.3**  Back in the code: save customer details writes three keys, user name, email and phone, and returns a small result for the LLM.
<br>*On screen: Back in agent.py, the three state writes are highlighted amber, then the return.*

**9:12.9**  Then we build the root agent. A name, the model, and a description. The description is what the LLM reads when it decides who should handle a message.
<br>*On screen: root_agent: name, model, description are highlighted.*

**9:25.7**  The instruction is plain English: greet the customer, collect and save their details, then transfer to the catalog agent.
<br>*On screen: The instruction block is highlighted.*

**9:34.7**  tools lists the root agent's own tool, and sub_agents lists the three agents it can hand off to. That one line turns a single agent into a team.
<br>*On screen: tools, then the sub_agents line glows.*

**9:47.5**  Next, catalog agent dot py. It imports the products from data dot py, which is just a Python dictionary standing in for a real database.
<br>*On screen: data.py (five products), then catalog_agent.py imports.*

**9:59.0**  list products has no tool_context, because it never touches the session. It just returns the products.
<br>*On screen: list_products is highlighted; a note says no tool_context is needed.*

**10:06.6**  add to cart does need it. It checks the product exists, reads the cart from state, adds the quantity, and writes the cart back.
<br>*On screen: add_to_cart: check, read, update, write back, one line at a time.*

**10:17.7**  Why write it back? ADK saves a change when you assign the key. Changing the dictionary in place isn't enough, so always assign it back.
<br>*On screen: The write-back line glows with a tip: always assign it back.*

**10:29.2**  Its instruction uses user name, in curly braces, straight from state, and says when to hand off: when the customer has finished choosing, transfer to cart agent.
<br>*On screen: The catalog instruction: {user_name?} and the transfer line are highlighted.*

**10:41.6**  cart agent dot py reuses add to cart from the catalog file, and adds three tools of its own.
<br>*On screen: cart_agent.py imports; the reused add_to_cart is highlighted.*

**10:50.5**  view cart reads the cart from state and works out the total. remove from cart deletes an item, and writes the cart back.
<br>*On screen: view_cart, then remove_from_cart are highlighted.*

**11:01.2**  confirm cart saves two new keys: the cart total, and cart confirmed, set to true.
<br>*On screen: confirm_cart: the two state writes are highlighted amber.*

**11:08.4**  Its instruction covers both directions: back to the catalog agent to browse more, or forward to the order agent when the customer is happy.
<br>*On screen: The two transfer lines in the cart instruction are highlighted.*

**11:19.5**  In order agent dot py, place order first reads cart confirmed from state, so nobody can check out an unconfirmed cart.
<br>*On screen: place_order: the cart_confirmed check is highlighted.*

**11:29.3**  Then it creates an order ID and writes the last two keys: order ID and order status.
<br>*On screen: The two final state writes are highlighted amber.*

**11:37.4**  Its instruction pulls the name, total, email and phone straight from state. The question mark means: if the key isn't there yet, leave it blank instead of failing.
<br>*On screen: The order instruction: the {placeholders} glow, then the ? marks pop.*

**11:50.2**  Last, init dot py has one line that imports agent. ADK looks inside for a variable called root_agent, so keep that name.
<br>*On screen: __init__.py (one line), then root_agent in agent.py.*

**12:00.4**  Now let's run it. First, a virtual environment. It's a private folder of Python packages for this one project, so its libraries don't clash with anything else on your computer.
<br>*On screen: Setup: diagram of your computer's Python vs a project .venv folder.*

**12:14.1**  Create it with python dash m venv dot venv. That makes a folder called dot venv.
<br>*On screen: Terminal: python -m venv .venv; a .venv folder appears in the explorer.*

**12:21.7**  Then activate it. On Windows, dot venv, Scripts, activate. On Mac or Linux, source dot venv slash bin slash activate. Your prompt now starts with dot venv.
<br>*On screen: Activate commands for Windows and Mac/Linux; the prompt gains (.venv).*

**12:34.1**  Now install the requirements: pip install dash r requirements dot txt. That installs Google ADK into the virtual environment.
<br>*On screen: pip install -r requirements.txt; requirements.txt is shown.*

**12:43.1**  Copy dot env dot example to dot env, and paste in your Gemini API key from Google AI Studio.
<br>*On screen: .env.example to .env with a GOOGLE_API_KEY placeholder.*

**12:52.0**  Finally, run adk web, open localhost 8000, and pick ecommerce agent. Open the State tab and watch it grow, one agent at a time.
<br>*On screen: adk web; the State tab with the final state.*

## Recap  ·  13:04.0 – 14:07.0

**13:04.6**  So, to recap: one root agent, three sub-agents, each with its own job, all sharing one session.
<br>*On screen: Recap tree returns; 'One root. Three sub-agents. One shared session.'*

**13:12.7**  Control moves between them with transfer to agent, and the state grows as the customer moves along.
<br>*On screen: A hand-off glow runs across the tree; the eight state keys appear.*

**13:20.8**  The code is linked in the description. Try adding your own sub-agent, maybe a returns agent.
<br>*On screen: Code in the description; a dashed returns_agent? box joins the tree.*

**13:28.4**  If you found this useful, please like the video, and share it with a friend who's learning AI.
<br>*On screen: The recap slides away; the Explore AI with Gopal channel card appears with Like and Share lighting up.*

**13:36.9**  And please leave a comment. Even a quick one, like 'I'm interested', tells me you want more on this topic, so I'll know to make more videos like this.
<br>*On screen: The Comment pill lights up; a sample comment 'I'm interested!' pops in.*

**13:50.2**  Subscribe to Explore AI with Gopal for more hands-on AI videos. Thanks for watching, and see you in the next one.
<br>*On screen: The Subscribe button pulses. It holds, then fades out.*
