# Shorts from "Agent with Sub-Agents": two options (pick one, no mixing)

Every short: vertical 1080×1920, same look as the main video (navy canvas, chrome headlines, agent tree, amber session state, white hand-off pulse), word-synced captions, end card "Full video on Explore AI with Gopal".

---

## Option A: reuse your voiceover from v2 (fastest, nothing to record)

Each short is **one continuous stretch** of the v2 audio, no splicing. The visuals are rebuilt vertically and synced to those words.

| # | Short | v2 audio | Length | Starts with… |
|---|---|---|---|---|
| A1 | Stop building one giant AI agent | 2:11 – 3:01 | ~50s | "Now let's build our store assistant…" |
| A2 | How AI agents hand off control | 3:45 – 4:33 | ~47s | "So how does the conversation move from one agent to another?" |
| A3 | ToolContext explained | 6:59 – 8:06 | ~66s | "Now look at the last parameter, tool_context…" |
| A4 | What is an agent? | 0:28 – 1:10 | ~42s | "Let's start with the basics first…" |
| A5 | Watch state grow across 4 agents | 4:33 – 6:08 | ~95s | "Let's watch what happens with the real customer…" |
| A6 | Run it yourself (venv → adk web) | 10:40 – 11:51 | ~71s | "Now let's run it…" |

**Trade-off:** the lines were written as the middle of a long video, so they open mid-thought ("Now let's…") with no hook, and they don't mention GitHub or the preview. I'd put a hook headline **on screen** for the first 2 seconds, as text only (no voice), to compensate. A5 and A6 run over 60 seconds. That's allowed (Shorts can be up to 3 min), but they'll perform better shorter.

---

## Option B: new short scripts that you record (best shorts)

Written for Shorts: a hook in the first 2 seconds, then a one-line preview of what's coming, then the GitHub mention and a pointer to the full video. Each is about 40–55 seconds at a natural pace. Record each one in a single take; the teleprompter works for these too.

### B1 · Stop building one giant AI agent (~50s)
> Your AI agent is doing way too much. Here's the fix.
> The problem, the fix, and the one line of code that does it.
> Picture an online store assistant. One agent saves the customer's details, lists products, adds to the cart, removes items, confirms the cart, and places the order. That's seven tools and one giant instruction.
> As it grows, it starts picking the wrong tool, and it's really hard to test.
> The fix: split the work. One root agent, like a front desk, and three sub-agents: catalog, cart and order. Each tool moves to the agent that's responsible for it.
> In Google ADK, that's one line: sub_agents equals a list of your agents.
> The code is on GitHub, link in the description. The full walkthrough is on my channel.

### B2 · How AI agents hand off a conversation (~45s)
> How does one AI agent hand a customer to another?
> It comes down to three things: descriptions, one built-in tool, and a shared session.
> First, every agent has a description. The LLM reads them to decide who should answer next.
> Second, as soon as you add sub-agents, Google ADK gives your agents a tool called transfer_to_agent. Calling it hands control to another agent: down to a sub-agent, sideways to a sibling, or back up to the parent. Only one agent is in control at a time.
> Third, they all share one session. Same history, same state. Nothing gets lost when control moves.
> The code is on GitHub, link in the description.

### B3 · The parameter your AI never sees: ToolContext (~50s)
> There's a parameter in your ADK tools that the AI never sees.
> What it is, why it's there, and the one mistake to avoid.
> It's called tool_context. When the LLM calls save customer details, it only sees name, email and phone. ADK hides tool_context from the model, then passes it in when the tool runs. It spots it by its type hint, ToolContext.
> Through it, your tool reaches the session. Read state like a dictionary: state dot get. Write it the same way: state, key, equals value. ADK saves every write to the session.
> The mistake? Changing a dictionary in place isn't saved. Always assign it back.
> Full code on GitHub, link in the description.

### B4 · Watch the state grow across 4 AI agents (~50s)
> Four AI agents, one shopping trip, and one notebook they all share.
> Let's watch the session state grow, one agent at a time.
> Asha shares her name, email and phone. The root agent saves three keys, then hands her to the catalog agent, which adds a cart.
> The cart agent edits it, then sends her back to the catalog for a charger, and back again.
> When she's happy, it saves the total and marks the cart confirmed.
> The order agent already knows her email and phone, because it reads them from state, and it adds the order ID and status.
> Eight keys, four agents, one shared session. The code is on GitHub, link in the description.

### B5 · Run a multi-agent app in four commands (~35s)
> Run a multi-agent AI app in four commands.
> Set up, install, add your key, and run.
> One: python dash m venv dot venv. That's a virtual environment, so this project's packages stay separate. Activate it: dot venv, Scripts, activate on Windows, or source dot venv slash bin slash activate on Mac and Linux.
> Two: pip install dash r requirements dot txt.
> Three: put your Gemini API key in a dot env file.
> Four: adk web. Open localhost 8000, and watch the State tab.
> The full project is on GitHub, link in the description.
