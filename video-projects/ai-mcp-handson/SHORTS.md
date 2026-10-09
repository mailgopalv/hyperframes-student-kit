# Shorts from "Build Your First AI Agent with MCP"

Clip timestamps refer to `renders/0927-tight.mp4` and `renders/0927-tight-16x9-cards.mp4`, which share the same timeline.
**[YOU]** = a new voiceover line you record. **[CLIP]** = original footage and audio; the quoted words are what you say in it.
Each short ends with its own closing line that pays off that short's point, then points to the full video. Say these the way you'd say them to a friend: relaxed, not announced. Don't read them word for word; small changes that sound more like you are better. Set the full tutorial (youtu.be/oicQkCXg8Vo) as each Short's **Related video** so "linked below" is literally true.

---

## Short 1: "My AI Agent Refused to Lie to Me" (~60s)
**Hook text on screen:** "I asked my AI agent something it didn't know…"

| Time | Source | Script |
|---|---|---|
| 0–4s | [YOU] over the ADK chat UI | "I asked my AI support agent a question it had no data for. Watch what it does." |
| 4–16s | [CLIP] 32:55–33:07 | Typing *"How long do I have before I can return my order?"* → *"I don't have access to the return policy right now."* |
| 16–34s | [CLIP] 33:07–33:25 | "We have set up harnessing within our agent… if no tool is available to answer a question, say so plainly: I don't have access to that right now." |
| 34–40s | [YOU] | "No guessing. No made-up policy. Then I gave it the actual policy docs through an MCP server…" |
| 40–55s | [CLIP] 45:03–45:18 | Same question → it answers from `refund_policy.md` |
| 55–60s | [YOU] | "Same question, real answer. Full build is on my channel." |

**On-screen callouts:** "❌ No data → no guessing" at 0:10 · "✅ Added docs via MCP" at 0:42

---

## Short 2: "What ACTUALLY Happens When an AI Agent Calls a Tool" (~90s)
**Hook text:** "Your AI agent makes 4 calls before it answers you"

| Time | Source | Script |
|---|---|---|
| 0–4s | [YOU] | "When you ask an AI agent 'where is my order?', it doesn't just answer. Here's what happens behind the scenes." |
| 4–80s | [CLIP] 30:49–32:05 (Google ADK Traces tab) | "…it first initializes the MCP… then MCP send tools list… the first ever call it does is 'get me the list of tools you have'… the LLM reads all the available tools… it needs to call get_order_status with order ID O-5001… MCP nicely returns the result… and the LLM just creates a friendly message and sends it to the user." |
| 80–90s | [YOU] | "So that's the whole loop: find the tools, pick one, call it, answer. That's really all MCP is. I build this whole thing step by step in the full video. Tap the link below and go check it out!" |

**On-screen callouts** (numbered as they happen): ① tools/list ② LLM picks tool ③ MCP call ④ friendly answer

---

## Short 3: "Test Your MCP Server BEFORE AI Touches It (MCP Inspector)" (~75s)
**Hook text:** "Your MCP server is running… but does it work?"

| Time | Source | Script |
|---|---|---|
| 0–15s | [CLIP] 13:42–14:00 | "…if you don't see any error, it is running successfully, but there is no way of testing it… That's where MCP Inspector comes into picture." |
| 15–20s | [YOU] | "One command:" + show `npx @modelcontextprotocol/inspector python.exe server.py` on screen |
| 20–60s | [CLIP] 15:13–15:53 | Connect → Tools → get_order_status → enter O-5001 → result |
| 60–70s | [CLIP] 15:53–16:07 | The random ID → "No order found" |
| 70–75s | [YOU] | "Honestly, test your tools here first. It'll save you so much head-scratching once the agent's involved. I walk through the full setup in my full video. Go give it a watch, it's linked right below." |

---

## Short 4: "The Most Important Line in Your MCP Tool Isn't Code" (~60s)
**Hook text:** "Your AI agent reads THIS to decide what to do"

| Time | Source | Script |
|---|---|---|
| 0–4s | [YOU] over the `server.py` docstring | "Your AI agent never sees your code. It sees this." |
| 4–30s | [CLIP] 11:01–11:27 | "…whenever you're defining a tool, it is very important you give this description and be as descriptive as possible… the more information you give on what the tool does, the more helpful it is for the agent." |
| 30–50s | [CLIP] 15:47–16:07 | MCP Inspector showing that same description as the tool's help text |
| 50–60s | [YOU] | "So write your descriptions like you're explaining the tool to a new teammate. Want to see me build the whole server from scratch? Tap the video link below." |

---

## Short 5: "Add Web Search to Your AI Agent Without Writing a Tool" (~90s)
**Hook text:** "I gave my AI agent Google-level search in 5 lines"

| Time | Source | Script |
|---|---|---|
| 0–4s | [YOU] | "My support agent only knew about orders. So I plugged in a free web-search MCP server." |
| 4–30s | [CLIP] 42:19–42:45 | "…I don't have to build anything from scratch… we have this DuckDuckGo MCP server…" (show the toolset code in `agent.py`) |
| 30–70s | [CLIP] 46:10–46:50 | "What is the weather forecast in Nottingham tomorrow?" → web search call → "high of 18 degrees with partial sunshine" |
| 70–85s | [CLIP] 46:55–47:10 | "If it is anything specific to product or orders, it is going to use the e-commerce MCP server… any random questions, it makes a call to DuckDuckGo…" |
| 85–90s | [YOU] | "Orders, policy docs, and now the whole web, and I didn't write a single search tool. Want to build it yourself? Hit the link below and watch the full walkthrough." |

---

## Short 6: "stdio vs Streamable HTTP: MCP in 60 Seconds" (~60s)
**Hook text:** "Local or remote? Your MCP server needs to know"

| Time | Source | Script |
|---|---|---|
| 0–4s | [YOU] | "Every MCP server has one line that decides who can talk to it." |
| 4–30s | [CLIP] 12:10–12:36 | "…transport equals stdio if my MCP server is running in the same system where the agent is going to run… it's like a walkie-talkie…" |
| 30–50s | [CLIP] 47:46–48:06 | "…if you wanted it exposed to the public internet where anybody can connect… set it up as streamable HTTP…" |
| 50–60s | [YOU] | "Same server, one line changed, and now anyone can connect to it. I show both versions in the full video. Go check it out, the link's right below!" |

**On-screen:** a split card: `transport="stdio"` 🔌 Local vs `transport="streamable-http"` 🌐 Remote

---

## Production notes
- **Framing (9:16):** your recording is landscape. For each clip, crop about 1080 px wide around the part that matters (the chat panel, the Traces list, or the code line), then scale it to 1080×1920. Put the hook text in the top third and captions in the lower third.
- **Captions:** pull the lines from `renders/0927-tight.srt` for each clip range.
- **Pacing:** trim any clip pause over 0.3 s. Shorts need to be tighter than the long-form video.
- **Order to post:** 1 → 2 → 5 → 3 → 4 → 6. Lead with the most surprising ones and save the more technical ones for later.
