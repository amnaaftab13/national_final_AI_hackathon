# Agentic AI Platform for Pakistan’s Informal Digital Economy

# Project: AI Fashion Bazar

**Built for the National Agentic AI Hackathon – Pakistan’s Informal Digital Economy Challenge**

This repository contains a fully autonomous **multi-agent business automation system**, built using:

- **OpenAI Agent SDK**
- **Private MCP Server**
- **WhatsApp Integration (Twilio)**
- **FastAPI Backend**
- **Autonomous Inter-Agent Handoffs**
- **Full Degraded Mode + Cache System**
- **Custom Tracing Engine + File-Based Logs**

Our goal: **Enable Pakistani micro-entrepreneurs to run their entire WhatsApp-based business autonomously**, with AI agents handling:

- Sales  
- Inventory  
- Marketing  
- Payments  
- Supplier Procurement  
- Analytics  
- Business Intelligence Reporting  

—all without human intervention.


# 🚀 Core Features
## 1. Private MCP-Orchestrated Multi-Agent System

All agents communicate securely via a dedicated private MCP server, enabling:

- Shared tool access

- Inter-agent handoffs

- Memory-aware reasoning

- Traceability of every request

Agents included:

| Agent                     | Role                                                                            |
| ------------------------- | ------------------------------------------------------------------------------- |
| **SalesAgent**            | Handles product queries, cart items, and handoffs for orders                    |
| **InventoryAgent**        | Real-time stock checks via MCP tools                                            |
| **FinanceAgent**          | Order finalization, Easypaisa payment simulation, supplier payment finalization |
| **InsightAgent**          | Detects low-selling products and triggers autonomous workflows                  |
| **BusinessDecisionAgent** | Full business analysis (pricing, inventory, marketing recommendations)          |
| **MarketingAgent**        | Campaign generation for Facebook/Instagram                                      |
| **BuyingAgent**           | Supplier procurement workflow                                                   |
| **AnalyticsAgent**        | Dashboard-ready structured reporting                                            |

## 2. Demonstrated Autonomy (Judge Requirement)

- The system showcases full autonomous cycles, where agents:

- Detect low-selling products

- Trigger marketing campaigns automatically

- Notify procurement without admin approval

- Run profit/loss calculations

- Generate business strategies

- Push WhatsApp messages to the admin

- Perform 24-hour scheduled analysis automatically

- No human-coded flowcharts — all reasoning is agent-driven.

### Example autonomous chain:

**InsightAgent → MarketingAgent → BusinessDecisionAgent → FinanceAgent**

## 3. Degraded Mode (Offline + Weak Connectivity Support)

The system includes a full degraded mode architecture:

### When MCP server is unhealthy:

- Incoming WhatsApp messages are cached

- MCP health-monitor runs in background

- Auto-reconnect logic restores agent functionality

- Cached messages are replayed after connection recovery

- Dashboard cache is used to avoid expensive re-computation

- This ensures graceful degradation, as required by the Hackathon scoring rubric.

## 4. Ultra-Low Latency Design (Hackathon Highlight)

Our architecture achieves high performance and low response latency using:

### 1. Strategic Tool Caching

MCP list_tools results cached (cache_tools_list=True)

Dashboard analytics cached via dashboard_cache

### 2. Reduced Tokens = Lower Latency

Agents pass short structured handoff messages, not long histories

Prompts optimized to reduce context window size

Agents use structured JSON exchanges internally to avoid long LLM reasoning strings

### 3. Parallel Background Tasks

#### Example:

MarketingAgent uses background async tasks for Facebook poster generation

BuyingAgent triggers procurement processing parallel without blocking

### 4. Latency-Optimized MCP Workflows

MCP health daemon ensures uninterrupted processing

Short-circuit checks avoid costly retries

### Outcome:

## 🧠 LLM Model Usage

Our agentic system is fully optimized for **ultra-low cost** and **low latency** by using **Gemini 2.5 Flash (FREE tier)** for almost all agent reasoning tasks.

| Component / Agent          | Model Used               | Reason                                                                              |
| -------------------------- | ------------------------- | ----------------------------------------------------------------------------------- |
| **SalesAgent**             | Gemini 2.5 Flash (Free)   | Fast intent detection, minimal reasoning cost, ideal for WhatsApp conversations     |
| **InventoryAgent**         | Gemini 2.5 Flash (Free)   | Lightweight structured reasoning + tool calling                                     |
| **FinanceAgent**           | Gemini 2.5 Flash (Free)   | Payment confirmations & supplier workflows with low latency                         |
| **InsightAgent**           | Gemini 2.5 Flash (Free)   | Fast low-selling product detection + triggers                                       |
| **BusinessDecisionAgent**  | Gemini 2.5 Flash (Free)   | Full strategic analysis using structured data + reasoning                           |
| **MarketingAgent**         | Gemini 2.5 Flash (Free)   | Generates campaigns & descriptions efficiently                                      |
| **BuyingAgent**            | Gemini 2.5 Flash (Free)   | Supplier procurement logic + calculations                                           |
| **AnalyticsAgent**         | Gemini 2.5 Flash (Free)   | Dashboard-ready structured analytics JSON generation                                |

###  Zero-Cost LLM Architecture

All agent reasoning flows run on **Gemini 2.5 Flash (free tier)** which results in:

- **0 PKR / $0 cost**
- **High throughput**
- **Low end-to-end latency**
- **Massive token savings**
- **Unlimited daily usage for hackathon-scale workloads**
- **Perfect for batch tasks, analysis agents, and background workflows**

This setup guarantees a **commercially viable**, **cost-efficient**, and **fast** AI system for Pakistani SMEs.

 ## 5. Cost Optimization Strategy (Hackathon Highlight)

LLM cost and token efficiency were core design goals.  
Since the entire system runs on **Gemini 2.5 Flash (Free Tier)**, our architecture is intentionally optimized to reduce unnecessary model calls and minimize token usage.

---

###  Cost Reduction Techniques

#### **1. Free & Efficient Model Utilization (Gemini 2.5 Flash)**  
All agents use **Gemini 2.5 Flash**, which is:

- Extremely low-latency  
- High-context  
- Free to use (no token billing)  

To further optimize efficiency:

- Routine tasks (inventory checks, sales confirmations) use **short prompts**  
- Heavy reasoning tasks (business analysis, strategy) use **structured prompts** to minimize output length  

This ensures **zero cost while maintaining high autonomy**.

---

#### **2. Shared MCP Server (Single Session = Lower Token Usage)**  
Agents share a unified MCP session:

- Shared tool metadata  
- Shared memory/state  
- Shared context cache  
- Reuse of MCP tool responses  
- One active MCP stream for all agents  

This approach prevents:

- Repeated tool initialization  
- Duplicate context loading  
- Redundant agent-to-agent messages  

---

#### **3. Capped Token Windows**  
The system enforces strict token discipline to maintain low latency:

- BusinessDecisionAgent produces **compact structured summaries**  
- Absolutely **no markdown / long narratives**  
- No examples, no illustrative text  
- JSON-only outputs when required  

This prevents token bloat and speeds up agent reasoning cycles.

---

#### **4. Dashboard Cache (High-Cost Analysis Cache)**  
Analytics such as:

- Weekly performance summaries  
- Profit/loss calculations  
- Demand prediction  
- Marketing insights  

are cached for **60 minutes** using a centralized cache system.

The cache only resets on:

- Actual order updates  
- Inventory changes  
- Financial events  

This eliminates unnecessary re-computation and repeated model calls.

---

#### **5. Background Agents = No Double Regeneration**  
Certain agents run in background mode:

- **MarketingAgent** (campaign creation)  
- **BuyingAgent** (supplier procurement workflow)  

This ensures:

- The main agent doesn't regenerate long content  
- No duplicate reasoning cycles  
- Lower latency  
- Zero extra token usage

---

### ✔ Result:  
With this strategy, the entire multi-agent workflow runs:

- **Zero monetary cost** (Gemini Flash Free Tier)  
- **Low token consumption**  
- **High-speed autonomous decisions**  
- **Minimal-delay inter-agent communication**



## 6. Full Traceability & Logs (Hackathon Deliverable)

The system includes a custom `FileTracingProcessor` that logs:

- Agent spans  
- MCP calls  
- Inter-agent handoffs  
- Function/tool calls  
- Token usage  
- Duration  
- Preview of inputs and outputs  

All logs are stored in:

agent_logs.jsonl

#                           ┌────────────────────┐
                           │   WhatsApp User     │
                           └──────────┬──────────┘
                                      │
                              (FastAPI Webhook)
                                      │
                           ┌──────────▼──────────┐
                           │     Sales Agent      │
                           └──────────┬──────────┘
                                      │ Handoff
        ┌──────────────────────────────────────────────────────────────┐
        │                           MCP Server                          │
        │   (Shared Tools, State, Tracing, Context, Message Routing)    │
        └──────────────────────────────────────────────────────────────┘
                 │                 │                 │                │
      ┌──────────▼────────┐ ┌──────▼────────┐ ┌─────▼────────┐ ┌────▼─────────┐
      │  InventoryAgent   │ │  FinanceAgent  │ │ InsightAgent  │ │ BuyingAgent  │
      └──────────┬────────┘ └──────┬────────┘ └─────┬────────┘ └────┬─────────┘
                 │                 │                 │               │
                 └────────┬────────┴──────────┬──────┴──────────────┘
                          ▼                   ▼
                ┌────────────────┐   ┌────────────────────┐
                │ MarketingAgent │   │ BusinessDecision    │
                └────────────────┘   └────────────────────┘


## 8. End-to-End Autonomous Workflow Demo

A full working demonstration includes:

- User sends a WhatsApp message

- SalesAgent routes the request

- InventoryAgent checks stock

- FinanceAgent finalizes the order

- Payment simulated via Easypaisa mock

- InsightAgent detects low-sellers

- MarketingAgent auto-launches campaign

- BuyingAgent notifies admin

- BusinessDecisionAgent generates strategic plan

- AnalyticsAgent prepares dashboard JSON

- All actions recorded in agent_logs.jsonl.

## 9. Privacy & Security Design

- Environment variables for all credentials

- No personal data stored in logs

- MCP tools access restricted

- Session-specific isolation

Tracing scrubbed for PII

## 10. Running Locally
pip install -r requirements.txt
uvicorn main:app --reload --port 8000


### Start MCP server:

python mcp_server.py/**deployed**


### Expose webhook for WhatsApp (if using ngrok):

ngrok http 8000

## Conclusion

This system meets and exceeds the Hackathon evaluation criteria:

✔ Autonomy
✔ Multi-Agent Architecture
✔ Private MCP Orchestration
✔ Low Latency + Low Cost
✔ Degraded Mode
✔ Pakistan-Specific SME Use Case
✔ Full Trace Logs

## Workflow

The workflow link is here, please follow the link:
https://workflow-afb.vercel.app/

## Team Members
- Amna Aftab
- Arishah Khan
