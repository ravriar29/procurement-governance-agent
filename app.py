"""
Amazon Business Hosted Catalog AI Assistant
Agentic procurement assistant for enterprise catalog creation.

Transforms a procurement admin's natural language request into a curated
hosted catalog — reducing catalog creation from 6-8 weeks to minutes.

Built by Rav Riar | Sr PM Technical, Amazon Business
Claude Opus 4.8 + Streamlit
UCP: dev.ucp.shopping.catalog.search + catalog.lookup
"""

import streamlit as st
import anthropic
import json
from datetime import datetime, timezone

MODEL = "claude-opus-4-8"

# ─── Simulated Amazon Business Catalog ───────────────────────────────────────
# In production this would be a live UCP catalog.search / catalog.lookup call
# to Amazon Business. Here we simulate the catalog data the agent reasons over.

CATALOG = [
    # ── Desks ──
    {"id": "B08-DESK-001", "title": "AmazonBasics Classic Adjustable Desk 48\"",
     "category": "desks", "tags": ["budget", "adjustable"],
     "unit_price": 149.99, "availability": "available",
     "min_qty": 1, "max_qty": 10000, "lead_days": 3},
    {"id": "B09-DESK-002", "title": "FlexiSpot E1 Electric Standing Desk 55\"",
     "category": "desks", "tags": ["standing", "ergonomic", "popular"],
     "unit_price": 279.00, "availability": "available",
     "min_qty": 10, "max_qty": 5000, "lead_days": 5},
    {"id": "B07-DESK-003", "title": "Fully Jarvis Bamboo Standing Desk 60\"",
     "category": "desks", "tags": ["premium", "standing", "sustainable"],
     "unit_price": 549.00, "availability": "sourcing_required",
     "min_qty": 50, "max_qty": None, "lead_days": None},

    # ── Chairs ──
    {"id": "B08-CHR-001", "title": "AmazonBasics Mid-Back Mesh Office Chair",
     "category": "chairs", "tags": ["budget", "mesh"],
     "unit_price": 119.99, "availability": "available",
     "min_qty": 1, "max_qty": 20000, "lead_days": 3},
    {"id": "B09-CHR-002", "title": "HON Ignition 2.0 Ergonomic Task Chair",
     "category": "chairs", "tags": ["ergonomic", "popular", "lumbar"],
     "unit_price": 249.00, "availability": "available",
     "min_qty": 25, "max_qty": 5000, "lead_days": 7},
    {"id": "B07-CHR-003", "title": "Herman Miller Aeron Chair (Size B)",
     "category": "chairs", "tags": ["premium", "ergonomic"],
     "unit_price": 1395.00, "availability": "sourcing_required",
     "min_qty": 50, "max_qty": None, "lead_days": None},

    # ── Monitors ──
    {"id": "B08-MON-001", "title": "Dell 24\" FHD IPS Monitor P2422H",
     "category": "monitors", "tags": ["standard", "FHD", "popular"],
     "unit_price": 199.99, "availability": "available",
     "min_qty": 5, "max_qty": 10000, "lead_days": 4},
    {"id": "B09-MON-002", "title": "LG 27\" 4K UHD USB-C Monitor 27UK850",
     "category": "monitors", "tags": ["4K", "USB-C", "premium"],
     "unit_price": 349.00, "availability": "available",
     "min_qty": 10, "max_qty": 3000, "lead_days": 5},
    {"id": "B07-MON-003", "title": "Samsung 34\" Ultrawide Curved Monitor",
     "category": "monitors", "tags": ["ultrawide", "premium", "creative"],
     "unit_price": 699.00, "availability": "sourcing_required",
     "min_qty": 25, "max_qty": None, "lead_days": None},

    # ── Keyboards & Mice ──
    {"id": "B08-KB-001", "title": "Logitech MK540 Wireless Keyboard & Mouse Combo",
     "category": "keyboards", "tags": ["wireless", "combo", "budget", "popular"],
     "unit_price": 49.99, "availability": "available",
     "min_qty": 1, "max_qty": 50000, "lead_days": 2},
    {"id": "B09-KB-002", "title": "Microsoft Sculpt Ergonomic Desktop (KB + Mouse)",
     "category": "keyboards", "tags": ["ergonomic", "wireless", "split"],
     "unit_price": 89.99, "availability": "available",
     "min_qty": 10, "max_qty": 10000, "lead_days": 3},
    {"id": "B07-KB-003", "title": "Logitech MX Keys Advanced Wireless Keyboard",
     "category": "keyboards", "tags": ["premium", "wireless", "backlit"],
     "unit_price": 109.99, "availability": "available",
     "min_qty": 10, "max_qty": 5000, "lead_days": 3},

    # ── Webcams ──
    {"id": "B08-CAM-001", "title": "Logitech C920 HD Pro Webcam 1080p",
     "category": "webcams", "tags": ["standard", "1080p", "popular"],
     "unit_price": 69.99, "availability": "available",
     "min_qty": 1, "max_qty": 20000, "lead_days": 2},
    {"id": "B09-CAM-002", "title": "Poly Studio P5 Professional Webcam",
     "category": "webcams", "tags": ["professional", "noise-cancelling"],
     "unit_price": 99.99, "availability": "available",
     "min_qty": 10, "max_qty": 5000, "lead_days": 4},
    {"id": "B07-CAM-003", "title": "Logitech Brio 4K Ultra HD Webcam",
     "category": "webcams", "tags": ["4K", "premium", "HDR"],
     "unit_price": 149.99, "availability": "sourcing_required",
     "min_qty": 50, "max_qty": None, "lead_days": None},

    # ── Headsets ──
    {"id": "B08-HS-001", "title": "Jabra Evolve 20 USB Mono Headset",
     "category": "headsets", "tags": ["budget", "mono", "UC-certified"],
     "unit_price": 44.99, "availability": "available",
     "min_qty": 1, "max_qty": 20000, "lead_days": 2},
    {"id": "B09-HS-002", "title": "Poly Voyager Focus 2 Wireless Headset",
     "category": "headsets", "tags": ["wireless", "ANC", "professional"],
     "unit_price": 199.99, "availability": "available",
     "min_qty": 10, "max_qty": 5000, "lead_days": 4},

    # ── Docking Stations ──
    {"id": "B08-DOCK-001", "title": "Anker 13-in-1 USB-C Docking Station",
     "category": "docking_stations", "tags": ["USB-C", "budget", "universal"],
     "unit_price": 89.99, "availability": "available",
     "min_qty": 1, "max_qty": 10000, "lead_days": 3},
    {"id": "B09-DOCK-002", "title": "CalDigit TS4 Thunderbolt 4 Dock",
     "category": "docking_stations", "tags": ["Thunderbolt", "premium", "Mac"],
     "unit_price": 349.00, "availability": "sourcing_required",
     "min_qty": 25, "max_qty": None, "lead_days": None},

    # ── Laptops ──
    {"id": "B09-LAP-001", "title": "Lenovo ThinkPad L14 Gen 4 (i5, 16GB, 512GB)",
     "category": "laptops", "tags": ["business", "reliable", "mid-range"],
     "unit_price": 799.00, "availability": "sourcing_required",
     "min_qty": 10, "max_qty": None, "lead_days": None},
    {"id": "B08-LAP-002", "title": "Dell Latitude 5540 (i7, 16GB, 512GB)",
     "category": "laptops", "tags": ["business", "premium", "popular"],
     "unit_price": 1099.00, "availability": "sourcing_required",
     "min_qty": 25, "max_qty": None, "lead_days": None},
    {"id": "B07-LAP-003", "title": "Apple MacBook Air M2 (16GB, 512GB)",
     "category": "laptops", "tags": ["Apple", "premium", "creative"],
     "unit_price": 1299.00, "availability": "sourcing_required",
     "min_qty": 50, "max_qty": None, "lead_days": None},

    # ── Office Supplies ──
    {"id": "B08-OFF-001", "title": "AmazonBasics Office Supply Starter Kit",
     "category": "office_supplies", "tags": ["bundle", "budget", "popular"],
     "unit_price": 24.99, "availability": "available",
     "min_qty": 1, "max_qty": 100000, "lead_days": 1},
    {"id": "B09-OFF-002", "title": "3M Post-it Notes + Stapler + Tape Bundle",
     "category": "office_supplies", "tags": ["popular", "essentials"],
     "unit_price": 19.99, "availability": "available",
     "min_qty": 1, "max_qty": 100000, "lead_days": 1},
]

# ─── Demo Scenarios ───────────────────────────────────────────────────────────

SCENARIOS = {
    "🏃 Nike — WFH Rollout": (
        "Nike is going fully remote for all corporate employees. "
        "We need to equip 5,000 employees with complete work-from-home setups. "
        "Budget is $400 per employee. We need standing desks, ergonomic chairs, "
        "monitors, wireless keyboard and mouse, and webcams. "
        "Standard options preferred — nothing premium. Timeline is 60 days."
    ),
    "🏥 Regional Hospital Network": (
        "We're a hospital network across 80 locations. Each location needs a recurring "
        "supply of office essentials — keyboards, mice, webcams for telehealth stations, "
        "and headsets for admin staff. About 20 units per category per location. "
        "Budget is tight. Need items that ship reliably and fast."
    ),
    "🚀 Tech Startup Scaling": (
        "We're hiring 200 engineers over the next 3 months and need to kit them out fast. "
        "Each person needs a laptop (prefer MacBook or Dell), monitor, docking station, "
        "and keyboard. Budget is $2,500 per person. Speed matters — "
        "we need the first batch of 50 sets within 2 weeks."
    ),
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    try:
        start = text.find("{")
        end   = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


def avail_badge(availability: str) -> str:
    if availability == "available":
        return '<span style="background:#1a7a3c;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.75rem;font-weight:bold">✅ Available Now</span>'
    elif availability == "limited":
        return '<span style="background:#b36200;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.75rem;font-weight:bold">⚠️ Limited Stock</span>'
    else:
        return '<span style="background:#8b0000;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.75rem;font-weight:bold">🔄 Needs Sourcing</span>'


# ─── Agent 1: Requirements Extractor ─────────────────────────────────────────

def extract_requirements(client: anthropic.Anthropic, request: str) -> dict:
    """
    Parses a procurement admin's natural language request into structured
    requirements: company, headcount, categories needed, budget, timeline,
    and any special constraints.
    """
    prompt = f"""You are a procurement requirements analyst for Amazon Business.

A procurement admin has submitted the following request. Extract their structured requirements.

REQUEST:
{request}

Extract and return ONLY valid JSON:
{{
  "company_name": "<inferred or 'Not specified'>",
  "use_case": "<1 sentence — what is this catalog for>",
  "headcount": <integer or null>,
  "budget_per_person": <float or null>,
  "total_budget_estimate": <float or null — headcount * budget_per_person if both known>,
  "categories_needed": ["<category names — use: desks, chairs, monitors, keyboards, webcams, headsets, docking_stations, laptops, office_supplies>"],
  "tier_preference": "<budget|standard|premium — infer from request>",
  "timeline_days": <integer or null>,
  "special_requirements": ["<any constraints: ergonomic, sustainability, Mac only, etc.>"],
  "quantity_per_category": {{
    "<category>": <integer>
  }}
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    return _extract_json(text)


# ─── Agent 2: Catalog Scout ───────────────────────────────────────────────────

def scout_catalog(client: anthropic.Anthropic, requirements: dict) -> dict:
    """
    Matches structured requirements against the Amazon Business catalog.
    Returns best matches per category, categorized as:
      - available_now: in catalog, contracted price, ships within lead_days
      - needs_sourcing: exists but requires vendor manager negotiation
      - not_covered: category not in catalog at all

    In production this calls dev.ucp.shopping.catalog.search + catalog.lookup.
    """
    catalog_json = json.dumps(CATALOG, indent=2)

    prompt = f"""You are the Amazon Business Catalog Scout — an AI agent that searches the Amazon Business catalog to match a customer's procurement requirements.

CUSTOMER REQUIREMENTS:
{json.dumps(requirements, indent=2)}

AMAZON BUSINESS CATALOG (simulated):
{catalog_json}

Your job: For each category the customer needs, identify the best 1-2 matches from the catalog.

Selection logic:
- Match the customer's tier_preference (budget/standard/premium)
- Respect their budget_per_person if specified — don't recommend items that blow the per-person budget when summed
- Check that max_qty >= quantity needed (or null = negotiable)
- Prefer "available" items over "sourcing_required" when quality is comparable
- For "sourcing_required" items, still recommend if they're the best fit — flag them as needing vendor negotiation

Return ONLY valid JSON:
{{
  "matches": {{
    "<category>": {{
      "recommended": {{
        "id": "<product id>",
        "title": "<product title>",
        "unit_price": <float>,
        "total_cost": <float — unit_price * quantity_needed>,
        "availability": "<available|sourcing_required>",
        "lead_days": <integer or null>,
        "reason": "<1 sentence why this is the best match>"
      }},
      "alternative": {{
        "id": "<product id>",
        "title": "<product title>",
        "unit_price": <float>,
        "total_cost": <float>,
        "availability": "<available|sourcing_required>",
        "lead_days": <integer or null>,
        "reason": "<1 sentence>"
      }} or null
    }}
  }},
  "not_covered": ["<categories that have no catalog match at all>"],
  "catalog_coverage_pct": <integer 0-100 — what % of needed categories have available-now items>,
  "total_available_cost": <float — sum of recommended items that are available_now>,
  "total_sourcing_cost": <float — sum of recommended items that need sourcing>,
  "scout_summary": "<2-3 sentences: what's ready, what needs work, any budget flags>"
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    return _extract_json(text)


# ─── Agent 3: Catalog Curator ─────────────────────────────────────────────────

def curate_catalog(client: anthropic.Anthropic, requirements: dict, scout_results: dict) -> dict:
    """
    Takes the scout results and assembles the final Hosted Catalog:
    - Selects the single best item per category
    - Calculates total contract value
    - Drafts the vendor sourcing request for items needing negotiation
    - Recommends contract term
    """
    prompt = f"""You are the Amazon Business Catalog Curator — the final step in the AI-assisted Hosted Catalog creation process.

CUSTOMER REQUIREMENTS:
{json.dumps(requirements, indent=2)}

CATALOG SCOUT RESULTS:
{json.dumps(scout_results, indent=2)}

Your job: Finalize the Hosted Catalog and draft any vendor sourcing requests.

A Hosted Catalog is a curated, contracted set of items that a company's employees
are allowed to purchase. Items in the catalog have pre-negotiated prices and quantities.
The goal is to give employees a controlled, simple buying experience while the company
controls costs and ensures compliance.

Return ONLY valid JSON:
{{
  "hosted_catalog": [
    {{
      "line_item": <integer starting at 1>,
      "category": "<category>",
      "product_id": "<id>",
      "product_title": "<title>",
      "contracted_unit_price": <float>,
      "quantity_contracted": <integer>,
      "total_line_value": <float>,
      "availability_status": "<Available Now|Pending Vendor Negotiation>",
      "estimated_delivery": "<e.g. 3-5 business days or Pending negotiation>"
    }}
  ],
  "catalog_summary": {{
    "total_items": <integer>,
    "items_available_now": <integer>,
    "items_pending_negotiation": <integer>,
    "total_contract_value": <float>,
    "recommended_contract_term_months": <integer>,
    "estimated_monthly_spend": <float>,
    "coverage_of_needs_pct": <integer 0-100>
  }},
  "vendor_sourcing_request": {{
    "needed": <true|false>,
    "items": [
      {{
        "product_title": "<title>",
        "category": "<category>",
        "quantity_needed": <integer>,
        "target_unit_price": <float or null>,
        "required_by_date": "<date string or 'Flexible'>",
        "notes": "<any special requirements for this item>"
      }}
    ],
    "request_summary": "<2-3 sentence message to Amazon Business vendor managers>"
  }},
  "time_to_value": {{
    "traditional_weeks": "6-8 weeks",
    "ai_assisted": "<honest estimate — e.g. '~20 minutes for available items; 1-2 weeks for sourced items'>",
    "items_you_can_activate_today": <integer — count of available_now items>
  }},
  "curator_notes": "<2-3 sentences of final recommendations or caveats for the admin>"
}}"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    return _extract_json(text)


# ─── UI ───────────────────────────────────────────────────────────────────────

def render_product_card(item: dict, qty: int):
    avail = item.get("availability", "")
    price = item.get("unit_price", 0)
    total = price * qty
    badge = avail_badge(avail)
    lead  = f"{item.get('lead_days')} business days" if item.get("lead_days") else "Pending negotiation"

    st.markdown(f"""
<div style="border:1px solid #333;border-radius:8px;padding:14px;margin-bottom:8px;background:#1a1a1a">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div style="flex:1">
      <div style="font-weight:600;font-size:0.95rem;margin-bottom:4px">{item['title']}</div>
      <div style="margin-bottom:6px">{badge}</div>
      <div style="color:#aaa;font-size:0.8rem">ID: {item['id']} &nbsp;·&nbsp; Ships in: {lead}</div>
    </div>
    <div style="text-align:right;min-width:130px">
      <div style="font-size:1.1rem;font-weight:bold;color:#ff9900">${price:,.2f}<span style="font-size:0.75rem;color:#aaa">/unit</span></div>
      <div style="font-size:0.85rem;color:#ccc">×{qty:,} = <strong>${total:,.0f}</strong></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Amazon Business — Hosted Catalog AI",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:4px">
  <div style="font-size:2rem">🛒</div>
  <div>
    <div style="font-size:1.5rem;font-weight:700">Amazon Business — Hosted Catalog AI Assistant</div>
    <div style="color:#aaa;font-size:0.85rem">Agentic procurement assistant · Tell us what you need · Get a curated catalog in minutes</div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Setup")
        api_key = st.text_input("Anthropic API Key", type="password", help="sk-ant-…")
        st.divider()
        st.markdown("""
**What this does**

You describe what your company needs in plain English. The AI agent:

1. **Extracts** your requirements — headcount, categories, budget, timeline
2. **Searches** the Amazon Business catalog for best matches
3. **Curates** your Hosted Catalog — contracted items ready to activate
4. **Drafts** a vendor sourcing request for anything that needs negotiation

**Traditional catalog creation:** 6–8 weeks
**With AI:** Minutes for available items

---
Built by [Rav Riar](https://github.com/ravriar29) · Sr PM Technical, Amazon Business
        """)

    # No API key splash
    if not api_key:
        st.info("👈 Enter your Anthropic API key in the sidebar to get started.")
        st.markdown("""
### The problem this solves

A company like Nike decides to go fully remote. Their procurement admin needs to set up a
**Hosted Catalog** — a curated set of approved items (desk, chair, monitor, keyboard, webcam)
at pre-negotiated prices, so employees can buy only what's approved, at the right price,
without going rogue.

**Today:** The admin has to manually search through thousands of Amazon Business results,
work with an Amazon Business sales rep, negotiate contracts, go back and forth — **6 to 8 weeks**
before a single employee can place an order.

**With Agentic AI:** The admin describes what they need in one paragraph. The AI agent
searches the catalog, finds the right items for their budget and headcount, identifies what's
available now vs. what needs a vendor conversation, and delivers a draft Hosted Catalog —
**in minutes, not months.**

---

**Pick a scenario below to see it in action once you've added your API key.**
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
**🏃 Nike — WFH Rollout**
5,000 employees, $400/person budget,
desks + chairs + monitors + webcams,
60-day deadline
            """)
        with col2:
            st.markdown("""
**🏥 Regional Hospital Network**
80 locations, keyboards + webcams
for telehealth + headsets for admin,
tight budget, fast shipping needed
            """)
        with col3:
            st.markdown("""
**🚀 Tech Startup Scaling**
200 engineers, $2,500/person,
MacBook + monitor + dock,
first 50 sets in 2 weeks
            """)
        return

    client = anthropic.Anthropic(api_key=api_key)

    # ── Input Section ─────────────────────────────────────────────────────────
    st.subheader("📋 What does your company need?")

    # Scenario quick-select buttons
    st.caption("Jump-start with a demo scenario:")
    scen_cols = st.columns(len(SCENARIOS))
    selected_scenario = None
    for i, (label, text) in enumerate(SCENARIOS.items()):
        if scen_cols[i].button(label, use_container_width=True):
            selected_scenario = text

    if selected_scenario:
        st.session_state["request_text"] = selected_scenario

    request_text = st.text_area(
        "Describe your procurement need:",
        value=st.session_state.get("request_text", ""),
        height=120,
        placeholder="e.g. Nike is going fully remote. We need to equip 5,000 employees with work-from-home setups. Budget is $400 per employee. We need desks, ergonomic chairs, monitors, keyboards, and webcams. Timeline is 60 days.",
        key="request_input",
    )

    if selected_scenario:
        st.session_state["request_text"] = selected_scenario

    run = st.button("🔍 Build My Hosted Catalog", type="primary", disabled=not request_text.strip())

    if not run or not request_text.strip():
        return

    st.divider()

    # ── Agent 1: Requirements Extraction ─────────────────────────────────────
    with st.status("🧠 Analyzing your requirements…", expanded=True) as status:
        st.write("Reading your request and extracting structured requirements…")
        requirements = extract_requirements(client, request_text)
        status.update(label="✅ Requirements extracted", state="complete")

    st.subheader("📌 What I understood")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Company", requirements.get("company_name", "—"))
    r2.metric("Employees", f"{requirements.get('headcount', '—'):,}" if requirements.get("headcount") else "—")
    r3.metric("Budget / Person", f"${requirements.get('budget_per_person', 0):,.0f}" if requirements.get("budget_per_person") else "—")
    r4.metric("Timeline", f"{requirements.get('timeline_days', '—')} days" if requirements.get("timeline_days") else "—")

    cats  = requirements.get("categories_needed", [])
    specs = requirements.get("special_requirements", [])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Categories needed:** {', '.join(cats) if cats else '—'}")
        st.markdown(f"**Tier preference:** {requirements.get('tier_preference', '—').title()}")
    with c2:
        if specs:
            st.markdown(f"**Special requirements:** {', '.join(specs)}")
        est = requirements.get("total_budget_estimate")
        if est:
            st.markdown(f"**Total estimated budget:** ${est:,.0f}")

    if requirements.get("use_case"):
        st.info(f"💡 {requirements['use_case']}")

    st.divider()

    # ── Agent 2: Catalog Scout ────────────────────────────────────────────────
    with st.status("🔎 Searching Amazon Business catalog…", expanded=True) as status:
        st.write("Matching your requirements against available catalog items…")
        scout = scout_catalog(client, requirements)
        status.update(label="✅ Catalog search complete", state="complete")

    st.subheader("📦 Catalog Search Results")

    # Coverage summary
    coverage = scout.get("catalog_coverage_pct", 0)
    avail_cost = scout.get("total_available_cost", 0)
    sourcing_cost = scout.get("total_sourcing_cost", 0)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Catalog Coverage", f"{coverage}%")
    s2.metric("Items Available Now", f"${avail_cost:,.0f}")
    s3.metric("Needs Sourcing", f"${sourcing_cost:,.0f}")
    s4.metric("Total Est. Value", f"${avail_cost + sourcing_cost:,.0f}")

    if scout.get("scout_summary"):
        st.info(scout["scout_summary"])

    # Per-category results
    matches = scout.get("matches", {})
    qty_map = requirements.get("quantity_per_category", {})

    if matches:
        st.markdown("**Best matches per category:**")
        for category, match_data in matches.items():
            qty = qty_map.get(category, requirements.get("headcount", 1) or 1)
            rec = match_data.get("recommended")
            alt = match_data.get("alternative")

            with st.expander(f"**{category.replace('_', ' ').title()}** — {qty:,} units needed", expanded=True):
                if rec:
                    st.markdown("**Recommended:**")
                    # Find in catalog for full data
                    cat_item = next((c for c in CATALOG if c["id"] == rec.get("id")), None)
                    if cat_item:
                        render_product_card(cat_item, qty)
                    else:
                        st.markdown(f"**{rec.get('title')}** — ${rec.get('unit_price', 0):,.2f}/unit · {avail_badge(rec.get('availability', ''))}", unsafe_allow_html=True)
                    if rec.get("reason"):
                        st.caption(f"Why: {rec['reason']}")

                if alt:
                    st.markdown("**Alternative:**")
                    cat_item = next((c for c in CATALOG if c["id"] == alt.get("id")), None)
                    if cat_item:
                        render_product_card(cat_item, qty)
                    if alt.get("reason"):
                        st.caption(f"Why: {alt['reason']}")

    not_covered = scout.get("not_covered", [])
    if not_covered:
        st.warning(f"⚠️ **Not in catalog:** {', '.join(not_covered)} — these will need to be sourced separately.")

    st.divider()

    # ── Agent 3: Catalog Curator ──────────────────────────────────────────────
    with st.status("📋 Curating your Hosted Catalog…", expanded=True) as status:
        st.write("Selecting best item per category, calculating contract value, drafting vendor requests…")
        catalog_result = curate_catalog(client, requirements, scout)
        status.update(label="✅ Hosted Catalog ready", state="complete")

    # ── Final Hosted Catalog ──────────────────────────────────────────────────
    st.subheader("🛒 Your Draft Hosted Catalog")

    summary = catalog_result.get("catalog_summary", {})
    items_now = summary.get("items_available_now", 0)
    items_pending = summary.get("items_pending_negotiation", 0)
    total_val = summary.get("total_contract_value", 0)
    monthly = summary.get("estimated_monthly_spend", 0)
    term = summary.get("recommended_contract_term_months", 12)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Total Contract Value", f"${total_val:,.0f}")
    f2.metric("Available to Activate", f"{items_now} items")
    f3.metric("Pending Negotiation", f"{items_pending} items")
    f4.metric(f"Est. Monthly Spend", f"${monthly:,.0f}")

    # Line items table
    catalog_items = catalog_result.get("hosted_catalog", [])
    if catalog_items:
        # Separate available vs pending
        available_items = [i for i in catalog_items if i.get("availability_status") == "Available Now"]
        pending_items   = [i for i in catalog_items if i.get("availability_status") != "Available Now"]

        if available_items:
            st.markdown("### ✅ Available Now — Activate Today")
            for item in available_items:
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                col_a.markdown(f"**{item.get('product_title', '—')}**")
                col_b.markdown(f"${item.get('contracted_unit_price', 0):,.2f}/unit")
                col_c.markdown(f"Qty: {item.get('quantity_contracted', 0):,}")
                col_d.markdown(f"**${item.get('total_line_value', 0):,.0f}**")
                st.caption(f"Ships in: {item.get('estimated_delivery', '—')} &nbsp;·&nbsp; ID: {item.get('product_id', '—')}")
                st.divider()

        if pending_items:
            st.markdown("### 🔄 Pending Vendor Negotiation")
            for item in pending_items:
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                col_a.markdown(f"**{item.get('product_title', '—')}**")
                col_b.markdown(f"${item.get('contracted_unit_price', 0):,.2f}/unit")
                col_c.markdown(f"Qty: {item.get('quantity_contracted', 0):,}")
                col_d.markdown(f"**${item.get('total_line_value', 0):,.0f}**")
                st.caption(f"Status: Submitted to Amazon Business vendor team for pricing & availability confirmation")
                st.divider()

    if catalog_result.get("curator_notes"):
        st.info(f"💡 {catalog_result['curator_notes']}")

    # ── Vendor Sourcing Request ────────────────────────────────────────────────
    vendor_req = catalog_result.get("vendor_sourcing_request", {})
    if vendor_req.get("needed") and vendor_req.get("items"):
        st.divider()
        st.subheader("📨 Vendor Sourcing Request — Auto-Generated")
        st.caption("The following request will be submitted to your Amazon Business vendor manager to negotiate pricing and availability.")

        if vendor_req.get("request_summary"):
            st.markdown(f"""
<div style="border-left:3px solid #ff9900;padding:12px 16px;background:#1a1a1a;border-radius:4px;margin-bottom:12px">
{vendor_req['request_summary']}
</div>""", unsafe_allow_html=True)

        for req_item in vendor_req["items"]:
            with st.container():
                vi1, vi2, vi3 = st.columns([3, 1, 1])
                vi1.markdown(f"**{req_item.get('product_title', '—')}** ({req_item.get('category', '').replace('_', ' ').title()})")
                vi2.markdown(f"Qty: {req_item.get('quantity_needed', '—'):,}" if isinstance(req_item.get('quantity_needed'), int) else f"Qty: {req_item.get('quantity_needed', '—')}")
                target = req_item.get('target_unit_price')
                vi3.markdown(f"Target: ${target:,.2f}/unit" if target else "Target: Negotiate")
                if req_item.get("notes"):
                    st.caption(req_item["notes"])

        st.button("📤 Submit to Amazon Business Vendor Team", type="secondary")

    # ── Time to Value ──────────────────────────────────────────────────────────
    st.divider()
    st.subheader("⏱️ Time to Value")

    ttv = catalog_result.get("time_to_value", {})
    activate_today = ttv.get("items_you_can_activate_today", items_now)

    t1, t2, t3 = st.columns(3)
    t1.metric(
        "Traditional Catalog Creation",
        ttv.get("traditional_weeks", "6-8 weeks"),
        delta="Manual process through sales team",
        delta_color="off",
    )
    t2.metric(
        "AI-Assisted",
        ttv.get("ai_assisted", "Minutes for available items"),
        delta="↓ dramatically faster",
        delta_color="normal",
    )
    t3.metric(
        "Items You Can Activate Right Now",
        f"{activate_today} of {len(catalog_items)} items",
        delta="No negotiation needed",
        delta_color="normal",
    )


if __name__ == "__main__":
    main()
