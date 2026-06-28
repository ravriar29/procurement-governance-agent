"""
Enterprise Procurement AI Governance System
Multi-agent trust pipeline for UCP-compliant supplier onboarding.

Built with Claude Opus 4.8 (Anthropic) + Streamlit.
UCP spec: https://ucp.dev — Universal Commerce Protocol, co-developed by Amazon.

Architecture mirrors the governance infrastructure behind Amazon Business
Hosted Catalog — a $500M+ GMS enterprise procurement platform.

Agent pipeline:
  1. Catalog Validator   — UCP profile structure, capability naming, catalog search/lookup
  2. Compliance Checker  — Security, AP2 mandate readiness, RFC 9421, JWS/JCS crypto
  3. Risk & Approval     — Final decision with agentic autonomy authorization
"""

import streamlit as st
import anthropic
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────

MODEL = "claude-opus-4-8"

# Minimum score to pass each pipeline gate
GATE_CATALOG_TO_COMPLIANCE = 400   # Bronze floor
GATE_COMPLIANCE_TO_RISK    = 600   # Silver floor


# ─── SHA-256 Hash-Chained Audit Logger ────────────────────────────────────────

class AuditLogger:
    """
    Tamper-evident audit log. Each entry's SHA-256 hash incorporates the
    previous entry's hash — any retroactive modification breaks the chain.

    Satisfies UCP / enterprise governance requirement: "logs immutable and
    tamper-evident; no agent action can modify or delete its own log entry."
    """

    def __init__(self):
        self.chain: list[dict] = []

    def log(self, agent: str, action: str, payload: dict, score: Optional[int] = None) -> dict:
        prev_hash = self.chain[-1]["hash"] if self.chain else "0" * 64
        entry = {
            "seq":       len(self.chain) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent":     agent,
            "action":    action,
            "score":     score,
            "payload":   payload,
            "prev_hash": prev_hash,
        }
        raw = json.dumps({k: v for k, v in entry.items() if k != "hash"}, sort_keys=True).encode()
        entry["hash"] = hashlib.sha256(raw).hexdigest()
        self.chain.append(entry)
        return entry

    def verify_chain(self) -> bool:
        for i, entry in enumerate(self.chain):
            expected_prev = self.chain[i - 1]["hash"] if i > 0 else "0" * 64
            if entry["prev_hash"] != expected_prev:
                return False
            check = {k: v for k, v in entry.items() if k != "hash"}
            if hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest() != entry["hash"]:
                return False
        return True


# ─── Sample UCP Profiles ──────────────────────────────────────────────────────
#
# UCP profiles are published at /.well-known/ucp (HTTPS, no redirects,
# Cache-Control: public max-age >= 60). They declare capabilities, transport
# bindings, payment handlers, and signing keys.
#
# Capability naming: reverse-domain format required.
#   ✅ dev.ucp.shopping.catalog.search
#   ✅ com.amazon.b2b.hosted_catalog
#   ❌ customCheckout  (informal, not reverse-domain)
#
# AP2 Mandates (dev.ucp.shopping.ap2_mandate):
#   Enables cryptographic authorization for autonomous agents via SD-JWT+kb.
#   Two artifacts: checkout_mandate (proof of checkout terms) +
#                  payment_mandate (payment authorization bound to checkout hash).
#   Once negotiated, session is Security Locked — cannot revert to unprotected flow.
#   Requires: signing_keys with ES256/JWK, vp_formats_supported: {dc+sd-jwt: {}}
#
# Catalog capabilities are SEPARATE from checkout:
#   dev.ucp.shopping.catalog.search  — free-text + filter product discovery
#   dev.ucp.shopping.catalog.lookup  — batch retrieval by variant/product ID
#   Catalog responses are NOT transactional commitments; checkout is authoritative.

SAMPLE_PROFILES = {

    "Amazon Business (Gold Standard)": {
        "ucp": {"version": "2025-01-01"},
        "well_known": "https://business.amazon.com/.well-known/ucp",
        "services": [
            {"type": "rest",     "endpoint": "https://business.amazon.com/api/ucp",   "version": "2025-01-01"},
            {"type": "mcp",      "endpoint": "https://business.amazon.com/mcp",        "version": "2025-01-01"},
            {"type": "a2a",      "endpoint": "https://business.amazon.com/a2a",        "version": "2025-01-01"},
            {"type": "embedded", "endpoint": "https://business.amazon.com/embedded",   "version": "2025-01-01"},
        ],
        "capabilities": {
            # Core commerce
            "dev.ucp.shopping.checkout":             ["2025-01-01"],
            "dev.ucp.shopping.cart":                 ["2025-01-01"],
            "dev.ucp.shopping.order":                ["2025-01-01"],
            # Catalog (separate from checkout — product discovery before purchase)
            "dev.ucp.shopping.catalog.search":       ["2025-01-01"],
            "dev.ucp.shopping.catalog.lookup":       ["2025-01-01"],
            # Agentic extensions
            "dev.ucp.shopping.ap2_mandate": [{
                "version": "2025-01-01",
                "extends": "dev.ucp.shopping.checkout",
                "config": {
                    "vp_formats_supported": {"dc+sd-jwt": {}}
                }
            }],
            # Standard extensions
            "dev.ucp.shopping.fulfillment":          ["2025-01-01"],
            "dev.ucp.shopping.discount":             ["2025-01-01"],
            "dev.ucp.shopping.buyer_consent":        ["2025-01-01"],
            # Amazon B2B extensions (vendor-namespaced)
            "com.amazon.b2b.hosted_catalog":         ["2025-01-01"],
            "com.amazon.b2b.purchase_order":         ["2025-01-01"],
            "com.amazon.b2b.approval_workflow":      ["2025-01-01"],
        },
        "payment_handlers": [
            {"id": "stripe",     "provider": "com.stripe.payment",           "pci_certified": True},
            {"id": "amex_b2b",   "provider": "com.amex.b2b.purchasing_card", "pci_certified": True},
            {"id": "amazon_pay", "provider": "com.amazon.pay",               "pci_certified": True},
        ],
        "signing_keys": [
            {"kid": "amzn-b2b-ec-2025-01",  "kty": "EC",  "crv": "P-256", "use": "sig", "alg": "ES256"},
            {"kid": "amzn-b2b-ec-2025-02",  "kty": "EC",  "crv": "P-384", "use": "sig", "alg": "ES384"},
        ],
        "security": {
            "transport":             "https_only",
            "auth_methods":          ["oauth2", "mtls", "http_message_signatures"],
            "rfc9421_compliant":     True,
            "credential_flow":       "platform_to_business_only",
            "no_credential_echo":    True,
            "pci_dss_scope":         "minimized_via_provider_tokenization",
        },
        "supported_versions": {
            "2024-06-01": "https://business.amazon.com/.well-known/ucp/v2024-06-01"
        },
    },

    "Acme Corp Supplier (Partial Compliance)": {
        "ucp": {"version": "2024-06-01"},
        "well_known": "https://acme-supply.example.com/.well-known/ucp",
        "services": [
            # HTTP endpoint — UCP requires HTTPS; this is a violation
            {"type": "rest", "endpoint": "http://acme-supply.example.com/api", "version": "2024-06-01"},
        ],
        "capabilities": {
            "dev.ucp.shopping.checkout":  ["2024-06-01"],
            "dev.ucp.shopping.cart":      ["2024-06-01"],
            # Violations: not reverse-domain format
            "customCheckout":             ["1.0"],
            "Fulfillment":                ["v2"],
            # Missing: catalog.search, catalog.lookup, ap2_mandate
        },
        "payment_handlers": [
            # Not PCI-certified, internal-only provider
            {"id": "manual_wire", "provider": "internal.manual", "pci_certified": False},
        ],
        # Missing signing keys — cannot verify message signatures or AP2 mandates
        "signing_keys": [],
        "security": {
            "transport":             "mixed",
            "auth_methods":          ["api_key"],
            "rfc9421_compliant":     False,
            # UCP violation: credentials echo back to platform
            "credential_flow":       "bidirectional",
            "no_credential_echo":    False,
            "pci_dss_scope":         "undefined",
        },
    },

    "Rogue Vendor (Non-Compliant)": {
        "ucp": {"version": "2020-01-01"},  # Severely outdated
        "well_known": None,                 # Missing /.well-known/ucp entirely
        "services": [
            {"type": "rest", "endpoint": "http://rogue-vendor.biz/checkout"},
        ],
        "capabilities": {
            # Completely wrong formats — no namespace, no dates
            "checkout": ["v1"],
            "payment":  ["v1"],
        },
        "payment_handlers": [],
        "signing_keys": [],
        "security": {
            "transport":         "http",
            "auth_methods":      [],
            "rfc9421_compliant": False,
            "credential_flow":   "unknown",
        },
    },
}


# ─── JSON extraction helper ───────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    try:
        start = text.find("{")
        end   = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


# ─── Agent 1: Catalog Validator ───────────────────────────────────────────────

def run_catalog_validator(
    client: anthropic.Anthropic,
    profile: dict,
    logger: AuditLogger,
) -> tuple[int, dict]:
    """
    Validates a supplier's UCP profile for structural correctness:
    capability naming, catalog capabilities, service transport declarations,
    payment handlers, and profile completeness.

    Maps to: Hosted Catalog intake validation at Amazon Business.
    Amazon co-developed UCP — the catalog.search + catalog.lookup capabilities
    are the protocol-level expression of what Hosted Catalog does.
    """

    prompt = f"""You are the Catalog Validator Agent in an enterprise procurement AI governance system.

Your task: Analyze this supplier's UCP (Universal Commerce Protocol) profile and produce a structured trust score (0–1000) based on catalog quality and structural compliance.

SUPPLIER PROFILE UNDER REVIEW:
{json.dumps(profile, indent=2)}

═══ UCP SPECIFICATION CONTEXT ═══

**Capability naming rules:**
- MUST use reverse-domain format: dev.ucp.shopping.checkout, com.vendor.service.feature
- dev.ucp.* namespace is controlled by the UCP body
- Vendors use their own domain prefix for extensions (e.g., com.amazon.b2b.hosted_catalog)
- VIOLATION examples: "customCheckout", "Fulfillment", "checkout", "v1" — none are valid

**Catalog capabilities (SEPARATE from checkout):**
- dev.ucp.shopping.catalog.search  — free-text + filter product discovery
- dev.ucp.shopping.catalog.lookup  — batch retrieval by product/variant ID
- Catalog responses are NOT transactional; checkout is authoritative
- For enterprise B2B (like Amazon Business Hosted Catalog), catalog search + lookup are critical

**AP2 Mandate capability (agentic commerce):**
- dev.ucp.shopping.ap2_mandate — enables autonomous agent purchases via SD-JWT+kb credentials
- MUST declare "extends": "dev.ucp.shopping.checkout"
- MUST include "config": {{"vp_formats_supported": {{"dc+sd-jwt": {{}}}}}}
- Once negotiated, session is Security Locked — cannot revert to unprotected checkout
- Two mandate artifacts: checkout_mandate (binds checkout terms) + payment_mandate (payment auth)
- Requires signing_keys with ES256 (EC P-256, JWK format) in profile

**Service transport bindings:**
- REST (HTTP/1.1+), MCP (Model Context Protocol / JSON-RPC), A2A (Agent-to-Agent), Embedded
- All endpoints MUST use HTTPS — HTTP is a critical violation
- MCP and A2A bindings signal agentic commerce readiness

**Profile discovery:**
- Businesses MUST publish at /.well-known/ucp over HTTPS
- No 3xx redirects permitted
- Cache-Control: public, max-age >= 60 required

═══ SCORING DIMENSIONS (0–200 each, total 0–1000) ═══

1. **Capability naming** — All capabilities in valid reverse-domain format?
2. **Catalog coverage** — Has catalog.search AND catalog.lookup? AP2 mandate with correct config?
3. **Transport security** — HTTPS-only endpoints? MCP/A2A bindings for agentic use?
4. **Payment handlers** — PCI-certified providers? Correct provider namespace format?
5. **Profile completeness** — well_known URL present? UCP version current (2025-01-01)? Signing keys (JWK/ES256)?

TIERS:
- 700–1000: GOLD — Full UCP compliance, ready for autonomous procurement
- 400–699:  SILVER — Partial compliance, conditional approval with human review
- 0–399:    BRONZE — Non-compliant, blocked at intake

Respond with ONLY valid JSON (no prose, no markdown fences):
{{
  "total_score": <integer 0-1000>,
  "dimension_scores": {{
    "capability_naming": <0-200>,
    "catalog_coverage": <0-200>,
    "transport_security": <0-200>,
    "payment_handlers": <0-200>,
    "profile_completeness": <0-200>
  }},
  "violations": ["<specific violation — be precise, cite UCP requirement>"],
  "strengths": ["<specific strength>"],
  "catalog_readiness": {{
    "has_catalog_search": <true|false>,
    "has_catalog_lookup": <true|false>,
    "has_ap2_mandate": <true|false>,
    "ap2_config_valid": <true|false>
  }},
  "tier": "<GOLD|SILVER|BRONZE>",
  "summary": "<2-3 sentence assessment>"
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    result_text = next((b.text for b in response.content if b.type == "text"), "{}")
    result = _extract_json(result_text)
    score  = result.get("total_score", 0)
    logger.log("catalog_validator", "profile_analysis", result, score=score)
    return score, result


# ─── Agent 2: Compliance Checker ──────────────────────────────────────────────

def run_compliance_checker(
    client: anthropic.Anthropic,
    profile: dict,
    catalog_score: int,
    logger: AuditLogger,
) -> tuple[int, dict]:
    """
    Security audit, AP2 cryptographic readiness, and regulatory compliance.

    Maps to: 25+ workstream regulatory compliance program at Amazon Business.
    Key UCP compliance requirements: RFC 9421 message signatures, JWS Detached
    Content (RFC 7515 App. F), JCS canonicalization (RFC 8785), ES256 keys.
    """

    prompt = f"""You are the Compliance Checker Agent in an enterprise procurement AI governance system.

Context: Catalog Validator scored this supplier {catalog_score}/1000. Now run a deep security and regulatory compliance audit.

SUPPLIER PROFILE:
{json.dumps(profile, indent=2)}

═══ UCP COMPLIANCE REQUIREMENTS ═══

**Transport & identity security:**
- ALL endpoints MUST use HTTPS — single HTTP endpoint = critical violation
- Business-to-platform webhooks MUST be signed per RFC 9421 (HTTP Message Signatures)
- Identity binding: UCP-Agent header identity must align with authenticated principal
- Signing keys MUST be published as JWK in profile's signing_keys array

**AP2 Mandate cryptographic requirements (for autonomous agent authorization):**
- Algorithms: ES256 (required), ES384, ES512 — signing_keys must include EC P-256 JWK
- Canonicalization: JCS (RFC 8785) for mandate payload before signing
- Business signs checkout response with JWS Detached Content (RFC 7515 Appendix F):
    merchant_authorization = "<header>..<signature>" (double-dot = detached payload)
- Two mandate artifacts: checkout_mandate (SD-JWT+kb, binds checkout hash) +
                         payment_mandate (bound to specific payment authorization)
- Security Locking: once AP2 negotiated, MUST NOT accept complete_checkout without ap2.checkout_mandate
- AP2 error codes supplier must handle: mandate_required, agent_missing_key,
  mandate_invalid_signature, mandate_expired, mandate_scope_mismatch, merchant_authorization_invalid

**Credential flow rules:**
- Credentials flow Platform → Business ONLY
- Businesses MUST NOT echo credentials back in responses
- PCI-DSS scope: minimize via provider-hosted tokenization (not raw card data)

**Protocol currency:**
- Current UCP version: 2025-01-01 (YYYY-MM-DD format)
- supported_versions map required for backward compatibility with older platform agents

═══ COMPLIANCE DOMAINS (0–200 each, total 0–1000) ═══

1. **Transport security** — HTTPS-only, RFC 9421 message signatures, no mixed protocols
2. **Identity & signing keys** — JWK keys present, EC P-256/ES256 for AP2, key rotation policy
3. **AP2 cryptographic readiness** — Correct mandate structure, JCS support, JWS Detached Content, error code handling
4. **Credential governance** — Platform→Business flow only, no credential echo, PCI-DSS tokenization
5. **Protocol currency** — UCP version (2025-01-01 preferred), supported_versions backward-compat path

Amazon Business compliance benchmark: 180–200 per domain.
Applicable frameworks: SOC 2, PCI-DSS, GDPR (EU suppliers), Amazon Vendor Standards.

Respond with ONLY valid JSON:
{{
  "total_score": <integer 0-1000>,
  "domain_scores": {{
    "transport_security": <0-200>,
    "identity_signing_keys": <0-200>,
    "ap2_cryptographic_readiness": <0-200>,
    "credential_governance": <0-200>,
    "protocol_currency": <0-200>
  }},
  "compliance_flags": ["<specific violation — cite RFC or UCP spec section where applicable>"],
  "regulatory_risks": ["<legal/regulatory exposure>"],
  "remediation_required": ["<must be fixed before any approval>"],
  "ap2_readiness": {{
    "signing_keys_present": <true|false>,
    "es256_supported": <true|false>,
    "jcs_canonicalization_ready": <true|false>,
    "session_locking_compliant": <true|false>
  }},
  "tier": "<GOLD|SILVER|BRONZE>",
  "summary": "<2-3 sentence compliance assessment>"
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    result_text = next((b.text for b in response.content if b.type == "text"), "{}")
    result = _extract_json(result_text)
    score  = result.get("total_score", 0)
    logger.log("compliance_checker", "compliance_audit", result, score=score)
    return score, result


# ─── Agent 3: Risk & Approval ─────────────────────────────────────────────────

def run_risk_approval(
    client: anthropic.Anthropic,
    profile: dict,
    catalog_score: int,
    compliance_score: int,
    logger: AuditLogger,
) -> tuple[int, dict]:
    """
    Final procurement decision with agentic autonomy authorization scope.

    Maps to: Decision Authority Matrix from the AI Governance PRD template.
    AP2 mandate authorization defines what the procurement agent can do
    autonomously vs. what requires human sign-off.
    """

    composite = (catalog_score + compliance_score) // 2

    prompt = f"""You are the Risk & Approval Agent — final decision authority in the enterprise procurement AI governance pipeline.

PIPELINE SCORES TO DATE:
- Catalog Validator:  {catalog_score}/1000
- Compliance Checker: {compliance_score}/1000
- Current Composite:  {composite}/1000

SUPPLIER PROFILE:
{json.dumps(profile, indent=2)}

═══ DECISION AUTHORITY MATRIX ═══

- APPROVED_AUTONOMOUS  (≥ 700, Gold):   AP2 mandates authorized; agent can transact within defined spend limits
- APPROVED_CONDITIONAL (400–699, Silver): Conditional — human sign-off required before activation
- REJECTED             (< 400, Bronze):  Blocked — remediation roadmap required before re-submission

═══ AGENTIC PROCUREMENT CONTEXT ═══

This platform governs Amazon Business Hosted Catalog — $500M+ GMS. Risk tolerance is LOW.

AP2 (Agent Payments Protocol) enables autonomous purchases where:
- The buying agent (platform) submits a checkout_mandate (SD-JWT+kb, cryptographically bound to checkout hash)
- The buying agent submits a payment_mandate (payment authorization, bound to checkout_mandate)
- The supplier verifies both before processing — no human in the loop
- Mandate scope is non-repudiable: the agent cannot exceed what the user's mandate authorized
- Fraud reduction: payment mandates are scoped to a specific checkout hash (prevents token replay)
- Delegation chain: agent acts within narrowed scope of what the human explicitly authorized

AP2 authorization governs: Which suppliers can receive autonomous orders from AI procurement agents?

═══ RISK DIMENSIONS (0–200 each, total 0–1000 — higher score = lower risk = better) ═══

1. **Supply chain risk** — Supplier concentration, geographic risk, business continuity signals
2. **Financial risk** — Payment handler maturity, PCI certification, fraud controls, chargeback exposure
3. **Operational risk** — Transport diversity (REST+MCP+A2A), fallback mechanisms, SLA signals
4. **Reputational risk** — Protocol standards adherence, UCP partnership tier, certification signals
5. **Agentic autonomy risk** — AP2 mandate scope controls, session locking compliance, mandate expiry handling, reversibility

Respond with ONLY valid JSON:
{{
  "risk_score": <integer 0-1000, higher = lower risk>,
  "final_composite_score": <integer — weighted average across all three agents>,
  "risk_dimensions": {{
    "supply_chain": <0-200>,
    "financial": <0-200>,
    "operational": <0-200>,
    "reputational": <0-200>,
    "agentic_autonomy": <0-200>
  }},
  "decision": "<APPROVED_AUTONOMOUS|APPROVED_CONDITIONAL|REJECTED>",
  "tier": "<GOLD|SILVER|BRONZE>",
  "conditions": ["<required conditions if conditional — empty if autonomous or rejected>"],
  "risk_mitigations": ["<required controls before activation>"],
  "agentic_authorization": {{
    "ap2_mandate_permitted": <true|false>,
    "autonomous_spend_limit": "<e.g. $50,000 per PO or 'not authorized'>",
    "human_review_cadence": "<e.g. quarterly or 'not required'>",
    "mandate_scope": "<what the procurement agent is authorized to do autonomously>",
    "session_lock_required": <true|false>
  }},
  "summary": "<3-4 sentence final decision rationale>"
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    result_text = next((b.text for b in response.content if b.type == "text"), "{}")
    result = _extract_json(result_text)
    score  = result.get("risk_score", 0)
    logger.log("risk_approval", "final_decision", result, score=score)
    return score, result


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def tier_badge(tier: str) -> str:
    cfg = {
        "GOLD":   ("#FFD700", "#000", "GOLD ✅"),
        "SILVER": ("#C0C0C0", "#000", "SILVER ⚠️"),
        "BRONZE": ("#CD7F32", "#fff", "BRONZE 🚫"),
    }
    bg, fg, label = cfg.get(tier, ("#666", "#fff", tier))
    return (
        f'<span style="background:{bg};color:{fg};padding:4px 14px;'
        f'border-radius:4px;font-weight:bold;font-size:0.85rem">{label}</span>'
    )


def score_bar(score: int, max_score: int = 1000):
    pct   = score / max_score * 100
    color = "#FFD700" if score >= 700 else "#C0C0C0" if score >= 400 else "#CD7F32"
    st.markdown(
        f'<div style="background:#2a2a2a;border-radius:6px;height:22px;width:100%;margin-bottom:6px">'
        f'<div style="background:{color};border-radius:6px;height:22px;width:{pct:.1f}%;'
        f'display:flex;align-items:center;padding-left:10px;'
        f'font-size:0.78rem;color:#000;font-weight:bold;min-width:70px">'
        f'{score}/{max_score}</div></div>',
        unsafe_allow_html=True,
    )


def render_audit_trail(logger: AuditLogger):
    st.divider()
    st.subheader("🔗 Hash-Chained Audit Trail")
    valid = logger.verify_chain()
    if valid:
        st.success(f"✅ Chain integrity verified — {len(logger.chain)} entries · SHA-256 · tamper-evident")
    else:
        st.error("⚠️ Chain integrity FAILED — modification detected")

    for entry in logger.chain:
        label = f"#{entry['seq']} · {entry['agent']} · {entry['action']} · {entry['timestamp'][:19]}Z"
        with st.expander(label, expanded=False):
            c1, c2 = st.columns([1, 2])
            with c1:
                if entry.get("score") is not None:
                    st.metric("Score", entry["score"])
                st.caption(f"**Hash:** `{entry['hash'][:28]}…`")
                st.caption(f"**Prev:** `{entry['prev_hash'][:28]}…`")
            with c2:
                st.json(entry["payload"], expanded=False)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Procurement AI Governance",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🏛️ Enterprise Procurement AI Governance System")
    st.caption(
        "Multi-agent trust pipeline for UCP-compliant supplier onboarding · "
        "Claude Opus 4.8 · Adaptive thinking · "
        "[github.com/ravriar29](https://github.com/ravriar29)"
    )
    st.divider()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Anthropic API Key", type="password", help="sk-ant-…")

        st.divider()
        st.subheader("📋 Supplier Profile")
        profile_choice = st.selectbox(
            "Select sample or paste custom JSON:",
            list(SAMPLE_PROFILES.keys()) + ["Custom JSON"],
        )

        if profile_choice == "Custom JSON":
            raw = st.text_area("Paste UCP profile JSON:", height=300,
                               placeholder='{"ucp": {"version": "2025-01-01"}, ...}')
            try:
                profile = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
                profile = {}
        else:
            profile = SAMPLE_PROFILES[profile_choice]
            st.json(profile, expanded=False)

        st.divider()
        show_audit = st.checkbox("Show audit trail", value=True)

        st.divider()
        st.markdown("""
**Trust Tiers**
- 🥇 **GOLD** 700–1000 — Autonomous
- 🥈 **SILVER** 400–699 — Conditional
- 🥉 **BRONZE** 0–399 — Blocked

**Pipeline Gates**
- Catalog → Compliance: ≥ 400
- Compliance → Risk: ≥ 600

---
**[Universal Commerce Protocol](https://ucp.dev)**
Open standard for agent-native commerce.
Co-developed by Amazon, Etsy, DoorDash & others.
AP2 mandates = cryptographic authorization
for autonomous AI procurement agents.
        """)

    # ── Splash (no API key) ───────────────────────────────────────────────────
    if not api_key:
        st.info("👈 Enter your Anthropic API key in the sidebar to begin.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
### What this system does

This governance pipeline mirrors the trust, safety, and auditability
infrastructure required when deploying agentic AI into enterprise procurement —
specifically for platforms implementing the
**[Universal Commerce Protocol (UCP)](https://ucp.dev)**.

UCP is an open standard co-developed by Amazon that enables decentralized,
agent-native commerce. The **AP2 Mandates** extension allows autonomous AI agents
to execute purchases on behalf of users using cryptographically verifiable
SD-JWT+kb credentials — with no human in the loop.

Before any supplier can receive autonomous orders from an AI procurement agent,
they must pass this three-agent governance pipeline.
            """)

        with col2:
            st.markdown("""
### Three-agent trust pipeline

| Agent | Role | UCP Focus |
|---|---|---|
| 🔍 Catalog Validator | Schema & capability structure | Reverse-domain naming, catalog.search + catalog.lookup |
| ⚖️ Compliance Checker | Security & crypto audit | RFC 9421, JWS Detached Content, JCS (RFC 8785), ES256 |
| 🎯 Risk & Approval | Final decision authority | AP2 mandate scope, spend limits, session locking |

Each agent uses **Claude Opus 4.8 with adaptive thinking.**

Every action is logged to a **SHA-256 hash-chained audit trail** — tamper-evident,
reconstructable, readable by compliance auditors without engineering support.

**Sample profiles to try:**
- **Amazon Business** → Gold, all capabilities, AP2 authorized
- **Acme Corp** → Partial, HTTP endpoints, no signing keys
- **Rogue Vendor** → Blocked at Gate 1
            """)
        return

    client = anthropic.Anthropic(api_key=api_key)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        run = st.button("▶ Run Governance Pipeline", type="primary", use_container_width=True)

    if not run:
        return
    if not profile:
        st.error("No profile loaded.")
        return

    logger = AuditLogger()
    logger.log("system", "pipeline_started", {
        "profile":   profile_choice,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # ── Agent 1: Catalog Validator ────────────────────────────────────────────
    st.subheader("🔍 Agent 1 — Catalog Validator")
    with st.spinner("Analyzing UCP profile structure and catalog capabilities…"):
        catalog_score, catalog_result = run_catalog_validator(client, profile, logger)

    tier = catalog_result.get("tier", "BRONZE")
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: score_bar(catalog_score)
    with c2: st.markdown(tier_badge(tier), unsafe_allow_html=True)
    with c3: st.metric("Score", f"{catalog_score}/1000")

    with st.expander("Catalog Validation Details", expanded=True):
        if ds := catalog_result.get("dimension_scores"):
            st.markdown("**Dimension Scores**")
            for k, v in ds.items():
                st.progress(v / 200, text=f"{k.replace('_', ' ').title()}: {v}/200")

        if cr := catalog_result.get("catalog_readiness"):
            st.markdown("**Catalog & AP2 Readiness**")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("catalog.search",   "✅" if cr.get("has_catalog_search") else "❌")
            rc2.metric("catalog.lookup",   "✅" if cr.get("has_catalog_lookup") else "❌")
            rc3.metric("ap2_mandate",      "✅" if cr.get("has_ap2_mandate")    else "❌")
            rc4.metric("ap2 config valid", "✅" if cr.get("ap2_config_valid")   else "❌")

        ca, cb = st.columns(2)
        with ca:
            if viol := catalog_result.get("violations"):
                st.markdown("**❌ Violations**")
                for v in viol: st.markdown(f"- {v}")
        with cb:
            if strs := catalog_result.get("strengths"):
                st.markdown("**✅ Strengths**")
                for s in strs: st.markdown(f"- {s}")
        if summary := catalog_result.get("summary"):
            st.info(summary)

    # ── Gate 1 ────────────────────────────────────────────────────────────────
    if catalog_score < GATE_CATALOG_TO_COMPLIANCE:
        logger.log("system", "pipeline_blocked", {
            "gate": "catalog_to_compliance", "score": catalog_score,
            "threshold": GATE_CATALOG_TO_COMPLIANCE,
        })
        st.error(
            f"🚧 **Blocked at Gate 1** — Catalog score {catalog_score} "
            f"below compliance gate ({GATE_CATALOG_TO_COMPLIANCE}). Supplier rejected at intake."
        )
        if show_audit: render_audit_trail(logger)
        return

    # ── Agent 2: Compliance Checker ───────────────────────────────────────────
    st.subheader("⚖️ Agent 2 — Compliance Checker")
    with st.spinner("Running security, AP2 cryptographic readiness, and regulatory audit…"):
        compliance_score, compliance_result = run_compliance_checker(
            client, profile, catalog_score, logger
        )

    tier = compliance_result.get("tier", "BRONZE")
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: score_bar(compliance_score)
    with c2: st.markdown(tier_badge(tier), unsafe_allow_html=True)
    with c3: st.metric("Score", f"{compliance_score}/1000")

    with st.expander("Compliance Audit Details", expanded=True):
        if ds := compliance_result.get("domain_scores"):
            st.markdown("**Domain Scores**")
            for k, v in ds.items():
                st.progress(v / 200, text=f"{k.replace('_', ' ').title()}: {v}/200")

        if ar := compliance_result.get("ap2_readiness"):
            st.markdown("**AP2 Cryptographic Readiness**")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Signing Keys",       "✅" if ar.get("signing_keys_present")      else "❌")
            rc2.metric("ES256 / EC P-256",   "✅" if ar.get("es256_supported")           else "❌")
            rc3.metric("JCS (RFC 8785)",      "✅" if ar.get("jcs_canonicalization_ready") else "❌")
            rc4.metric("Session Locking",    "✅" if ar.get("session_lock_compliant")    else "❌")

        ca, cb = st.columns(2)
        with ca:
            if flags := compliance_result.get("compliance_flags"):
                st.markdown("**🚩 Compliance Flags**")
                for f in flags: st.markdown(f"- {f}")
        with cb:
            if risks := compliance_result.get("regulatory_risks"):
                st.markdown("**⚠️ Regulatory Risks**")
                for r in risks: st.markdown(f"- {r}")
        if rem := compliance_result.get("remediation_required"):
            st.warning("**Remediation Required Before Any Approval:**")
            for item in rem: st.markdown(f"- {item}")
        if summary := compliance_result.get("summary"):
            st.info(summary)

    # ── Gate 2 ────────────────────────────────────────────────────────────────
    if compliance_score < GATE_COMPLIANCE_TO_RISK:
        logger.log("system", "pipeline_blocked", {
            "gate": "compliance_to_risk", "score": compliance_score,
            "threshold": GATE_COMPLIANCE_TO_RISK,
        })
        st.error(
            f"🚧 **Blocked at Gate 2** — Compliance score {compliance_score} "
            f"below risk gate ({GATE_COMPLIANCE_TO_RISK}). Escalated for human review."
        )
        if show_audit: render_audit_trail(logger)
        return

    # ── Agent 3: Risk & Approval ──────────────────────────────────────────────
    st.subheader("🎯 Agent 3 — Risk & Approval")
    with st.spinner("Rendering final procurement decision and AP2 mandate authorization…"):
        risk_score, risk_result = run_risk_approval(
            client, profile, catalog_score, compliance_score, logger
        )

    decision    = risk_result.get("decision", "REJECTED")
    final_score = risk_result.get("final_composite_score",
                                  (catalog_score + compliance_score + risk_score) // 3)
    tier        = risk_result.get("tier", "BRONZE")

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: score_bar(final_score)
    with c2: st.markdown(tier_badge(tier), unsafe_allow_html=True)
    with c3: st.metric("Final Score", f"{final_score}/1000")

    with st.expander("Risk Assessment Details", expanded=True):
        if rd := risk_result.get("risk_dimensions"):
            st.markdown("**Risk Dimensions**")
            for k, v in rd.items():
                st.progress(v / 200, text=f"{k.replace('_', ' ').title()}: {v}/200")

        if ag := risk_result.get("agentic_authorization"):
            st.markdown("**🤖 Agentic Autonomy Authorization (AP2)**")
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("AP2 Mandate", "Permitted ✅" if ag.get("ap2_mandate_permitted") else "Denied ❌")
            rc2.metric("Spend Limit", ag.get("autonomous_spend_limit", "—"))
            rc3.metric("Human Review", ag.get("human_review_cadence", "—"))
            if note := ag.get("mandate_scope"):
                st.caption(f"**Mandate scope:** {note}")
            if ag.get("session_lock_required"):
                st.caption("🔒 Session locking required — AP2 once negotiated cannot revert to unprotected checkout")

        if conds := risk_result.get("conditions"):
            st.warning("**Approval Conditions:**")
            for c in conds: st.markdown(f"- {c}")
        if mits := risk_result.get("risk_mitigations"):
            st.markdown("**Required Controls:**")
            for m in mits: st.markdown(f"- {m}")
        if summary := risk_result.get("summary"):
            st.info(summary)

    # ── Final Decision ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 Final Governance Decision")

    if decision == "APPROVED_AUTONOMOUS":
        st.success(
            f"✅ **APPROVED — AUTONOMOUS PROCUREMENT AUTHORIZED** · "
            f"Composite: {final_score}/1000 · Tier: GOLD · AP2 mandates enabled"
        )
    elif decision == "APPROVED_CONDITIONAL":
        st.warning(
            f"⚠️ **APPROVED — CONDITIONAL** · "
            f"Composite: {final_score}/1000 · Tier: SILVER · Human sign-off required before activation"
        )
    else:
        st.error(
            f"🚫 **REJECTED** · "
            f"Composite: {final_score}/1000 · Tier: BRONZE · Remediation required before re-submission"
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Catalog Validator",  f"{catalog_score}/1000")
    c2.metric("Compliance Checker", f"{compliance_score}/1000")
    c3.metric("Risk & Approval",    f"{risk_score}/1000")

    logger.log("system", "pipeline_completed", {
        "decision":              decision,
        "final_composite_score": final_score,
        "catalog_score":         catalog_score,
        "compliance_score":      compliance_score,
        "risk_score":            risk_score,
    })

    if show_audit:
        render_audit_trail(logger)


if __name__ == "__main__":
    main()
