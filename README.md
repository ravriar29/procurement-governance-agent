# Enterprise Procurement AI Governance System

A multi-agent trust pipeline for onboarding suppliers into UCP-compliant enterprise procurement networks. Built with Claude Opus 4.8 (Anthropic) and Streamlit.

---

## Why this exists

The [Universal Commerce Protocol (UCP)](https://ucp.dev) is an open standard for decentralized, agent-native commerce — co-developed by Amazon, Etsy, DoorDash, and others. Its **AP2 Mandates** extension enables autonomous AI agents to execute purchases on behalf of users using cryptographically verifiable SD-JWT+kb credentials: no human in the loop, no token replay, no amount manipulation.

Amazon Business's Hosted Catalog — a $500M+ GMS enterprise procurement platform — is being built around this architecture. Before any supplier can receive autonomous orders from a procurement AI agent, it must pass a governance pipeline that checks exactly what this app checks.

This app is a working demonstration of that pipeline.

---

## What it does

Three AI agents evaluate a supplier's UCP profile in sequence, with trust gates between each:

```
Supplier UCP Profile
       │
       ▼
┌─────────────────────┐
│  Catalog Validator  │  Checks: capability naming (reverse-domain), catalog.search +
│                     │  catalog.lookup, AP2 mandate config (vp_formats_supported),
│    Score: 0–1000    │  transport bindings, payment handlers, profile completeness
└────────┬────────────┘
         │  Gate: ≥ 400 to proceed
         ▼
┌─────────────────────┐
│ Compliance Checker  │  Checks: HTTPS enforcement, RFC 9421 message signatures,
│                     │  JWS Detached Content (RFC 7515 App. F), JCS canonicalization
│    Score: 0–1000    │  (RFC 8785), ES256/JWK signing keys, credential flow direction,
└────────┬────────────┘  AP2 session locking, PCI-DSS scope
         │  Gate: ≥ 600 to proceed
         ▼
┌─────────────────────┐
│  Risk & Approval    │  Checks: supply chain, financial, operational, reputational,
│                     │  and agentic autonomy risk. Outputs final decision + AP2
│    Score: 0–1000    │  mandate authorization scope and spend limits
└────────┬────────────┘
         │
         ▼
  Final Decision:
  APPROVED_AUTONOMOUS  (Gold, ≥ 700) — AP2 mandates enabled
  APPROVED_CONDITIONAL (Silver, 400–699) — human sign-off required
  REJECTED             (Bronze, < 400) — remediation required
```

Every agent runs on **Claude Opus 4.8 with adaptive thinking** — the reasoning behind each governance decision is surfaced before it's committed to the audit trail.

Every action is logged to a **SHA-256 hash-chained audit trail**: tamper-evident, chain-verifiable, readable by compliance auditors without engineering support.

---

## UCP concepts in the code

| UCP Concept | Where it appears |
|---|---|
| Reverse-domain capability naming (`dev.ucp.shopping.catalog.search`) | Catalog Validator scoring dimension |
| `catalog.search` + `catalog.lookup` as separate capabilities | Catalog readiness check; separate from checkout |
| AP2 mandate config (`vp_formats_supported: {dc+sd-jwt: {}}`) | Catalog Validator + Compliance Checker |
| JWS Detached Content (RFC 7515 App. F) for merchant_authorization | Compliance Checker crypto audit |
| JCS canonicalization (RFC 8785) for mandate payload | Compliance Checker AP2 readiness |
| ES256 / EC P-256 JWK signing keys | Compliance Checker key verification |
| Session locking once AP2 negotiated | Risk & Approval agentic authorization |
| checkout_mandate + payment_mandate as two distinct artifacts | Risk & Approval AP2 scope |
| Credential flow: Platform → Business only (no echo) | Compliance Checker credential governance |
| Capability intersection (platform ∩ business) | Sample profiles model the intersection |
| `supported_versions` for backward compat | Sample profiles + Compliance Checker scoring |

---

## Sample profiles

| Profile | Expected outcome |
|---|---|
| **Amazon Business** | Gold — full UCP compliance, all catalog + AP2 capabilities, ES256 keys |
| **Acme Corp** | Silver/Bronze — HTTP endpoint, missing signing keys, non-compliant capability names |
| **Rogue Vendor** | Bronze — blocked at Gate 1; outdated UCP version, no /.well-known/ucp, wrong formats |

---

## Setup

```bash
# Clone
git clone https://github.com/ravriar29/procurement-governance-agent.git
cd procurement-governance-agent

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

You'll need an [Anthropic API key](https://console.anthropic.com). Enter it in the sidebar when the app loads.

---

## How this maps to real Amazon Business work

| App component | Amazon Business equivalent |
|---|---|
| Catalog Validator | Hosted Catalog intake: validating supplier catalog feeds against schema requirements |
| `catalog.search` + `catalog.lookup` | UCP-native catalog discovery before checkout — the protocol-layer expression of Hosted Catalog |
| Compliance Checker | 25+ workstream regulatory compliance program: translating legal mandates into technical requirements |
| AP2 mandate authorization | Agentic AI governance: defining what the procurement agent can do autonomously vs. requiring human approval |
| Risk & Approval decision matrix | Decision Authority Matrix from the [AI Governance PRD template](https://github.com/ravriar29/agentic-pm-toolkit/blob/main/ai-governance-prd-template.md) |
| Hash-chained audit trail | Auditability requirement from Section 4 of the PRD template: "logs immutable and tamper-evident" |

---

## Related

- [agentic-pm-toolkit](https://github.com/ravriar29/agentic-pm-toolkit) — PRD templates, launch dashboards, and pre-launch checklists for Agentic AI products
- [UCP Specification](https://ucp.dev/latest/specification/overview/)
- [AP2 Mandates](https://ucp.dev/latest/specification/ap2-mandates/)

---

Built by [Rav Riar](https://github.com/ravriar29) · Senior PM Technical, Amazon
