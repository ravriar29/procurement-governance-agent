# Amazon Business — Hosted Catalog AI Assistant

A working demo of Agentic AI applied to enterprise B2B procurement. Built to showcase how AI can compress the Hosted Catalog creation process from **6–8 weeks to minutes**.

**Live demo →** [ravriar29-procurement-governance-agent.streamlit.app](https://ravriar29-procurement-governance-agent.streamlit.app)

Built by [Rav Riar](https://github.com/ravriar29) · Sr PM Technical, Amazon Business

---

## The problem this solves

Amazon Business's **Hosted Catalog** lets companies pre-approve a curated set of items at contracted prices — so employees can only order from an approved list, at negotiated prices, in approved quantities. It eliminates off-contract spending and procurement policy violations.

**The problem:** Building a Hosted Catalog today is slow. A procurement admin (say, Nike's budget manager) has to:
1. Manually search thousands of results across Amazon Business / Ariba / SAP
2. Negotiate prices with Amazon Business sales reps across multiple calls
3. Loop through internal approvals
4. Wait for the catalog to be provisioned

**Total time: 6–8 weeks minimum.**

This demo shows what that workflow looks like with Agentic AI: the admin describes what their company needs in plain English, and a three-agent pipeline returns a curated Hosted Catalog — ready to activate — in minutes.

---

## What it does

### Overview tab
Explains Hosted Catalog to anyone unfamiliar with enterprise B2B procurement:
- What a Hosted Catalog is and why it exists
- Real-world example: Nike going remote for 5,000 employees
- How the AI-assisted flow works step by step
- Stats: 6–8 weeks → minutes, 100% price compliance, $0 off-contract spend
- How it integrates with SAP Ariba, Coupa, Oracle, and other procurement platforms

### Browse & Build tab
An Amazon Business-style product browsing experience with an embedded AI assistant:

```
┌─────────────────────┐  ┌────────────────────────┐  ┌──────────────────────┐
│  Left sidebar       │  │  Product grid           │  │  AI Catalog          │
│                     │  │                         │  │  Assistant           │
│  Category filters   │  │  Amazon-style cards:    │  │                      │
│  Price slider       │  │  • Business Price badge │  │  Dark header panel   │
│  In Stock filter    │  │  • Star ratings         │  │  Scenario templates  │
│                     │  │  • Availability status  │  │  Chat input          │
│  🛒 Cart summary    │  │  • Add to Cart (yellow) │  │  Conversational AI   │
│  🗂️ Catalog summary │  │  • Add to Catalog (org) │  │  responses           │
└─────────────────────┘  └────────────────────────┘  └──────────────────────┘
```

**Scenario quick-starts** (pre-populate the AI with a fillable template):
- 🏠 WFH Setup — filters grid to desks, chairs, monitors, keyboards, webcams
- 🗂️ Office Supplies — filters grid to office supplies, keyboards, headsets
- 🚀 New Hire Onboarding — filters grid to laptops, monitors, docking stations

**Two purchase paths per product:**
- **Add to Cart** — standard B2C-style individual purchase
- **Add to Catalog** — adds to the company's Hosted Catalog being built

---

## The three-agent pipeline

When the admin sends a message describing their needs, three Claude agents run in sequence:

```
Admin's plain-English request
         │
         ▼
┌──────────────────────────┐
│  Requirements Extractor  │  Parses: company, headcount, budget/person,
│                          │  categories needed, tier preference, timeline
└──────────────┬───────────┘
               │
               ▼
┌──────────────────────────┐
│  Catalog Scout           │  Searches Amazon Business catalog, matches
│                          │  requirements to available items, flags gaps
└──────────────┬───────────┘
               │
               ▼
┌──────────────────────────┐
│  Catalog Curator         │  Assembles final recommendations, identifies
│                          │  items needing vendor negotiation, estimates
└──────────────┬───────────┘  contract value
               │
               ▼
  Conversational response + product cards
  surfaced in the product grid
```

**Model:** Claude Opus 4.8 with `thinking: {type: "adaptive"}` and streaming

---

## UCP — why it matters here

The [Universal Commerce Protocol (UCP)](https://ucp.dev) is an open standard co-developed by Amazon, Etsy, DoorDash, and others for agent-native B2B commerce. It defines how a procurement AI agent on a platform (e.g., Coupa) talks to a commerce endpoint (e.g., Amazon Business) without a human in the loop.

The two UCP capabilities that power Hosted Catalog discoverability:

| Capability | What it does |
|---|---|
| `dev.ucp.shopping.catalog.search` | Agent queries the catalog with filters (category, price, quantity) |
| `dev.ucp.shopping.catalog.lookup` | Agent retrieves full item details by ID |

When AP2 Mandates are enabled, a procurement agent can autonomously place orders within the catalog's contracted parameters — no human approval required for routine reorders. This is the agentic autonomy layer that makes Hosted Catalog more than just a list of products.

---

## How to run locally

```bash
git clone https://github.com/ravriar29/procurement-governance-agent.git
cd procurement-governance-agent
pip install -r requirements.txt
streamlit run app.py
```

You'll need an [Anthropic API key](https://console.anthropic.com). Enter it in the sidebar when the app loads.

---

## How this maps to real Amazon Business work

| Demo component | Amazon Business equivalent |
|---|---|
| Three-agent pipeline | Agentic catalog discovery replacing manual Ariba/SAP search |
| Hosted Catalog build flow | The actual 6–8 week procurement workflow this accelerates |
| "Needs Sourcing" flag | Gap identification → vendor negotiation with Amazon Business sales |
| UCP catalog.search + catalog.lookup | Protocol-layer expression of Hosted Catalog in agent-native commerce |
| AP2 Mandates | Agentic autonomy framework for autonomous procurement within approved parameters |
| Amazon Business UI skin | B2B product experience built on the same visual language as Amazon.com |

---

## Stack

| Layer | Technology |
|---|---|
| AI | Claude Opus 4.8 (Anthropic), adaptive thinking, streaming |
| Frontend | Streamlit with custom Amazon Business CSS |
| Catalog data | Simulated Amazon Business catalog (20 SKUs across 9 categories) |
| Protocol reference | Universal Commerce Protocol (UCP) v2026 |

---

## Related

- [agentic-pm-toolkit](https://github.com/ravriar29/agentic-pm-toolkit) — PRD templates, launch dashboards, and pre-launch checklists for Agentic AI products
- [UCP Specification](https://ucp.dev/latest/specification/overview/)
- [Amazon Business Hosted Catalog](https://business.amazon.com/en/solutions/systems-integration/hosted-catalog)
