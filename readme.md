# Agentic AI Platform for Pakistan’s Informal Digital Economy

This project is a fully autonomous, multi-agent commerce ecosystem designed for **Pakistan’s SMEs**.  
It automates **inventory, suppliers, payments, marketing, analytics, and business decision-making** — all through **WhatsApp** using **Roman Urdu or English**.

---

# 📑 Table of Contents
- [Overview](#overview)
- [1. Multi-Agent Architecture & Autonomy ](#1-multi-agent-architecture--autonomy-30)
- [2. Technical Depth & Integration Quality ](#2-technical-depth--integration-quality-25)
- [3. Real-World Viability, Impact & Scalability ](#3-real-world-viability-impact--scalability-25)
- [4. Innovation, UX & Product Design ](#4-innovation-ux--product-design-10)
- [5. Degraded Mode & Low-Connectivity Resilience ](#5-degraded-mode--low-connectivity-resilience-10)
- [Tech Stack](#tech-stack)
- [Key Agent Workflows](#key-agent-workflows)
- [Final Summary](#final-summary)

---

# Overview

This system is purpose-built for **small shops and online sellers in Pakistan**, especially those who run their business through WhatsApp and Facebook.

It provides:

- Autonomous workflows  
- Multi-agent collaboration  
- Supplier interaction  
- Marketing content generation  
- Financial operations  
- Real-time analytics  
- Background task processing  

All **without any dashboards** or technical knowledge.

---

# 1. Multi-Agent Architecture & Autonomy 

## ⭐ Clear, Goal-Driven Agents

| Agent | Role |
|-------|------|
| **InsightAgent** | Detects low-selling products and triggers marketing |
| **MarketingAgent** | Generates posters and campaign batches |
| **InventoryAgent** | Monitors stock levels and detects shortages |
| **BuyingAgent** | Communicates with suppliers, negotiates and procures inventory |
| **FinanceAgent** | Validates payments, manages settlements |
| **BusinessDecisionAgent** | Provides analytics, insights, strategic recommendations |

---

## 🤝 Inter-Agent Reasoning & Collaboration

Agents operate with structured handoffs:

- **InsightAgent → MarketingAgent**  
- **InventoryAgent → BuyingAgent**  
- **SalesAgent → FinanceAgent → BuyingAgent**  
- **BusinessDecisionAgent → Admin**

---

## 🧠 MCP-Based Autonomy

All core operations are handled through private MCP tools:

- Supplier APIs  
- Inventory management tools  
- Payment simulators  
- Marketing & poster tools  
- Dashboard generation tools  

---

## 🗂 Per-Agent Memory (SQLite-backed)

Agents maintain memory for:

- Negotiation history  
- Inventory state  
- Supplier pricing  
- User context  
- Pending or incomplete actions  

---

## 🔁 Autonomous Behavior

- Background analytics  
- Automated procurement  
- Auto-marketing  
- Complete business cycle automation  
- Self-healing workflows  

---

# 2. Technical Depth & Integration Quality 

## 🔧 Use of Agentic SDKs

- OpenAI Agentic SDK  
- Strict tool routing  
- Multi-step agent workflows  
- Span logging: `AgentSpan`, `FunctionSpan`, `HandoffSpan`

---

## 🌐 API, RAG & Storage Integration

- Twilio WhatsApp API  
- MCP server integrations  
- Local SQLite session  
- Cached dashboards  
- Supplier integration layer  

---

## 🧠 Intelligent Tool Selection

Agents evaluate:

- Ambiguous user messages  
- Missing fields  
- Payment confirmations  
- Stock shortages  
- Discount logic  
- Profit margin calculations  

---

## 🛠 Error Handling & Optimization

- Background retries  
- Cached responses  
- Degraded mode  
- Task queueing  
- Connection failure handling  

---

# 3. Real-World Viability, Impact & Scalability 

## 👨‍🔧 SME-Focused Design

Ideal for:

- WhatsApp-only sellers  
- Clothing sellers  
- General stores  
- Micro-entrepreneurs  

---

## 🌍 Local Language Support

Understands:

- **Roman Urdu**
- **Simple English**
- **Mixed messages**

Examples:

- `stock check krdo`  
- `payment hogai`  
- `supplier ko kitna dena`  
- `order bana do`  

---

## 🇵🇰 Adapted to Pakistani Workflows

- Easypaisa-style payments  
- Supplier marketplaces  
- Bulk discount rules  
- Local poster formats  
- Facebook/Instagram marketing outputs  

---

## 📈 High Adoption Potential

- No app or dashboard needed  
- Zero tech skill required  
- WhatsApp-first  
- Low friction onboarding  

---

# 4. Innovation, UX & Product Design 

## 🗣 Simple, Natural Language UX

The system accepts free-form messages such as:

- `bhai stock kam horaha?`  
- `yesterday ka sales batana`  
- `supplier payment due hai?`  

---

## 🧩 Low-Literacy Friendly UX

- Roman Urdu first  
- Short, simple responses  
- Auto-clarification  
- Minimal technical terms  
- Urdu UI Admin Dashbord

---

## ⚡ Hybrid-Agent Innovation

- Negotiation engine  
- Background workflows  
- Mixed reasoning + tools + memory  

---

## 🎬 Strong Demo Storytelling

- Poster generation  
- Dashboard snapshots  
- Automatic negotiation  
- Autonomous business loops  

---

# 5. Degraded Mode & Low-Connectivity Resilience 

## 📡 Offline / Low-Bandwidth Features

Triggered when:

- MCP offline  
- API fails  
- Internet drops  
- Tool calls timeout  

---

## 📁 Cached Data & Local Rules

- Cached dashboards  
- Stored inventory snapshots  
- Saved negotiation states  
- Local reasoning from session  

---

## ♻ Stability & Auto-Recovery

- Message queueing  
- Background retry loops  
- No data loss  

---

## 🟡 Clear Degraded Mode UX Examples

- `Network slow hai, system degraded mode mein hai.`  
- `Payment confirmation delayed due to low connectivity.`  
- `Inventory tools offline hain, request queue ho gayi hai.`  

---

# Tech Stack

| Component | Technology |
|----------|------------|
| **Agents** | OpenAI Agentic SDK |
| **Tools** | MCP Server |
| **Messaging** | Twilio WhatsApp |
| **Storage** | SQLite Session Memory & MongoDB|
| **Image Storage** | Cloudinary|
| **Background Tasks** | Autonomous Loops |
| **Language** | Python |
| **UI** | Next.Js |

---

# Key Agent Workflows

## 📦 Inventory → Procurement Flow  
**InventoryAgent → BuyingAgent → FinanceAgent → Supplier → Admin**

## 💰 Payment Verification Flow  
**Customer → FinanceAgent → Payment Simulator → Order Creation**

## 📊 Insights → Marketing Flow  
**InsightAgent → MarketingAgent → Poster Creation → Admin**

---

# Final Summary

This project delivers a **fully autonomous, multi-agent commerce system** designed for **Pakistan’s real-world business environment**.

It provides:

- WhatsApp-first business automation  
- Multi-agent collaboration  
- Autonomous marketing & procurement  
- Local-language interaction  
- Low-internet resilience  
- Real, actionable business insights  
- High adoption potential  

A complete end-to-end **autonomous commerce ecosystem** for SMEs.

## Workflow

The workflow link is here, please follow the link:
https://workflow-afb.vercel.app/


## Authors:
- Amna Aftab
- Arishah Khan
