You are working in my `support-agent-demo` project: a beginner-friendly, hands-on demo of building an MCP server in Python and connecting it to an AI support agent built with Google ADK (Agent Development Kit) and a free-tier Gemini model. It accompanies my YouTube tutorial "Build Your First AI Agent with MCP (Hands-on)".

Your job: write clear, accurate project documentation so a viewer with no prior experience can clone this repo and get it running.

## Step 1 — Read the code first (do not skip)

Before writing anything, read every file in the repo: `requirements.txt`, `ecommerce_mcp_server/data.py`, `ecommerce_mcp_server/server.py`, `support_agent/__init__.py`, `support_agent/agent.py`, everything in `docs/`, and `.env` if present.

The code is the source of truth. The notes below describe what I built in the video, but details may have changed since (versions, ports, package names, tool names). Wherever the code and my notes disagree, follow the code and list each disagreement for me at the end. Never invent tools, commands, versions or data that aren't in the code.

**Security:** never print, copy or commit the value of `GOOGLE_API_KEY`. Only ever show a placeholder.

## Step 2 — What the video covers (use as context)

**Goal:** an e-commerce customer-support agent that answers questions about orders and products from the store's own private data (via a hand-built MCP server), reads policy documents (via a public filesystem MCP server), and answers general questions via web search (via a public DuckDuckGo MCP server). It never guesses store data.

**Prerequisites shown:** Visual Studio Code, Python 3.11+, Node.js (LTS, needed for `npx`), and `uv`.

**Project layout built in the video:**
```
support-agent-demo/
├── ecommerce_mcp_server/
│   ├── data.py          # mock product + order data (stands in for a real API/database)
│   └── server.py        # the MCP server and its tools
├── support_agent/
│   ├── __init__.py      # ADK entry point — imports agent
│   └── agent.py         # the agent: model, instructions, MCP toolsets
├── docs/
│   ├── refund_policy.md
│   └── shipping_policy.md
├── .env                 # GEMINI_MODEL + GOOGLE_API_KEY (at project root)
└── requirements.txt     # mcp, google-adk
```

**The MCP server (`ecommerce_mcp_server/server.py`):**
- Built with `FastMCP` from the `mcp` library; imports ORDERS/PRODUCTS from `data.py`.
- Four tools: `get_order_status(order_id)`, `get_order_details(order_id)`, `search_products(category, color)` (both optional filters), `get_product_details(product_id)`.
- Each tool has a descriptive docstring. The video stresses these descriptions are what the LLM reads to decide which tool to call, so they matter.
- Unknown IDs return a friendly "No order/product found" error, not an exception.
- Runs with `transport="stdio"` when the agent and server are on the same machine. It was later switched to `transport="streamable-http"` (on port 8010, path `/mcp`) to show how you would deploy it as a remote server.
- Sample data from the video: orders like `O-5001` (packed for delivery, estimated 2026-09-17) and `O-5002` (out for delivery); products like the Aria Wireless Headphones (blue, $79.99, `P-1002`). Use whatever `data.py` actually contains.

**The agent (`support_agent/agent.py`):**
- `ROOT` = the project root (`Path(__file__).resolve().parent.parent`), so paths work from anywhere.
- Model is read from the `GEMINI_MODEL` env var, with a free-tier Flash-Lite default.
- A strict instruction ("harnessing"): always use the store's tools for order/product questions; never guess order status, product details or policy from general knowledge; use the filesystem tool for refund/shipping policy questions; use web search only for questions clearly unrelated to the store; if no tool can answer, say "I don't have access to that right now"; keep answers short and friendly.
- `build_toolsets()` returns the MCP toolsets:
  1. `private_ecommerce`: `McpToolset` + `StdioConnectionParams`, launching `server.py` with `sys.executable`
  2. `public_filesystem`: `npx -y @modelcontextprotocol/server-filesystem <ROOT>/docs` (uses `npx.cmd` on Windows)
  3. `public_web_search`: a DuckDuckGo MCP server (check the code for the exact command/package)
  4. optional `public_streamable_http_example`: `StreamableHTTPConnectionParams(url="http://127.0.0.1:<port>/mcp")`
- The video points out that every new toolset must also be added to the returned list, and the instructions updated to match.

**Getting a Gemini API key (as shown):** create or choose a project in Google Cloud Console → go to Google AI Studio → API Keys (aistudio.google.com/api-keys) → Create API key → choose the project → copy it into `.env`.

**Commands used in the video (Windows PowerShell, from the project root):**
```powershell
python --version
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run the MCP server on its own (no output = running fine; Ctrl+C to stop)
python .\ecommerce_mcp_server\server.py

# Test the MCP server with MCP Inspector (opens in the browser → Connect → Tools)
npx @modelcontextprotocol/inspector python.exe .\ecommerce_mcp_server\server.py

# Open MCP Inspector with no server, to try the built-in filesystem server
npx @modelcontextprotocol/inspector

# Run the agent in the ADK dev UI → http://localhost:8000 → pick support_agent
adk web

# Streamable HTTP variant: start the server, then connect Inspector (Transport: Streamable HTTP, URL http://localhost:8010/mcp)
python .\ecommerce_mcp_server\server.py
```

**Demo questions used to test the agent** (and which tool should fire):
- "Where is my order O-5001?" → `get_order_status`
- "Do you have headphones in blue?" → `search_products`
- "How long do I have before I can return my order?" → before the docs were added, "I don't have access to that right now"; after, it reads `refund_policy.md`
- "What is the weather forecast in Nottingham tomorrow?" → DuckDuckGo web search

**ADK web UI features mentioned:** the Events and Traces tabs (shows `tools/list`, then the LLM call, then the tool call, then the final answer), the Info graph of agent → toolsets, State (session metadata), Artifacts (generated files/images), Evals (evaluation sets for regression testing), and Sessions (switch, export for debugging).

## Step 3 — Create these files

1. **`README.md`** (the main deliverable), with these sections:
   - Title + a one-paragraph summary + a link placeholder for the video: `[Watch the tutorial](VIDEO_URL)`
   - **What you'll build**: a short list of the three capabilities (private data, policy docs, web search)
   - **How it works**: a Mermaid diagram (User → ADK Agent (Gemini) → three MCP servers → data/docs/web) plus a 5-step numbered walkthrough of one request: tools/list → LLM picks a tool → MCP call → result → friendly answer
   - **Prerequisites**: with install links, and a note on why each is needed (Node.js for `npx` MCP servers, `uv` if the web-search server uses `uvx`)
   - **Project structure**: a tree with one-line descriptions
   - **Setup**: step by step, with **Windows PowerShell** and **macOS/Linux** variants side by side (for example `.venv\Scripts\activate` vs `source .venv/bin/activate`, `python` vs `python3`)
   - **Configure your API key**: `.env` format with placeholders, and where to get the key
   - **Run it**: (a) test the MCP server with MCP Inspector, (b) run the agent with `adk web`, (c) try the four demo questions, each with the expected tool call
   - **The MCP tools**: a table of tool name, parameters, what it returns, and an example input
   - **Adding more MCP servers**: how the filesystem and DuckDuckGo toolsets are wired in, and the "add to the returned list + update instructions" rule
   - **Going remote: streamable HTTP**: the stdio vs streamable HTTP difference in two sentences, the code change, how to run it, and how to connect with Inspector and from the agent
   - **Why the instructions matter**: the "harnessing" idea, quoting the actual rules from `agent.py`
   - **Troubleshooting**: at least `npx`/`adk` not found, venv not activated, missing or invalid API key, port already in use, Inspector connects but shows no tools, and Windows `npx.cmd`
   - **Next steps**: ideas only (real database instead of mock data, evals, deployment)
2. **`.env.example`**: `GEMINI_MODEL=<value from code>` and `GOOGLE_API_KEY=your-api-key-here`
3. **`.gitignore`** (create it, or add to it if one exists): `.venv/`, `__pycache__/`, `.env`, `.adk/`, `*.pyc`
4. **`docs/ARCHITECTURE.md`** (short): the Mermaid diagram, the request lifecycle, and the stdio vs streamable HTTP comparison table

## Style

- Written for complete beginners: plain English, short sentences, explain each command in one line before or after it.
- Every command must be copy-pasteable and run from the project root.
- Use real names, ports and versions from the code, never made-up ones.
- Don't add features, tests or refactors, and don't change any Python code. This task is documentation only.

## When you're done

Reply with:
1. The list of files created or changed
2. Every place where the code differed from my notes above (for example a port that doesn't match between `server.py` and `agent.py`, or a different package version). Flag the port especially: in the recording the agent's streamable HTTP URL showed a different port from the server's 8010.
3. Anything you couldn't verify and left as a placeholder
