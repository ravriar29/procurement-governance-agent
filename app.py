"""
Amazon Business — Hosted Catalog AI Assistant
B2B Rufus-style agentic procurement experience.

Procurement admin describes what their company needs.
AI agent finds the right items, builds the Hosted Catalog.

Built by Rav Riar | Sr PM Technical, Amazon Business
Claude Opus 4.8 + Streamlit
"""

import streamlit as st
import anthropic
import json

MODEL = "claude-opus-4-8"

# ─── Simulated Amazon Business Catalog ───────────────────────────────────────

CATALOG = [
    {"id": "B09-DESK-002", "title": "FlexiSpot E1 Electric Standing Desk 55\"",      "category": "Desks",           "emoji": "🗂️",  "unit_price": 279.00, "availability": "available", "min_qty": 10,  "max_qty": 5000,   "lead_days": 5,  "tags": ["standing","ergonomic","popular"], "rating": 4.6, "reviews": 12847},
    {"id": "B08-DESK-001", "title": "AmazonBasics Adjustable Desk 48\"",              "category": "Desks",           "emoji": "🗂️",  "unit_price": 149.99, "availability": "available", "min_qty": 1,   "max_qty": 10000,  "lead_days": 3,  "tags": ["budget","adjustable"],            "rating": 4.3, "reviews": 8231},
    {"id": "B07-DESK-003", "title": "Fully Jarvis Bamboo Standing Desk 60\"",         "category": "Desks",           "emoji": "🗂️",  "unit_price": 549.00, "availability": "sourcing",  "min_qty": 50,  "max_qty": None,   "lead_days": None,"tags": ["premium","sustainable"],         "rating": 4.8, "reviews": 3102},
    {"id": "B09-CHR-002",  "title": "HON Ignition 2.0 Ergonomic Task Chair",         "category": "Chairs",          "emoji": "🪑",  "unit_price": 249.00, "availability": "available", "min_qty": 25,  "max_qty": 5000,   "lead_days": 7,  "tags": ["ergonomic","lumbar","popular"],   "rating": 4.5, "reviews": 9403},
    {"id": "B08-CHR-001",  "title": "AmazonBasics Mid-Back Mesh Chair",               "category": "Chairs",          "emoji": "🪑",  "unit_price": 119.99, "availability": "available", "min_qty": 1,   "max_qty": 20000,  "lead_days": 3,  "tags": ["budget","mesh"],                 "rating": 4.1, "reviews": 21560},
    {"id": "B07-CHR-003",  "title": "Herman Miller Aeron Chair (Size B)",             "category": "Chairs",          "emoji": "🪑",  "unit_price": 1395.00,"availability": "sourcing",  "min_qty": 50,  "max_qty": None,   "lead_days": None,"tags": ["premium","ergonomic"],           "rating": 4.9, "reviews": 5671},
    {"id": "B08-MON-001",  "title": "Dell 24\" FHD IPS Monitor P2422H",              "category": "Monitors",        "emoji": "🖥️", "unit_price": 199.99, "availability": "available", "min_qty": 5,   "max_qty": 10000,  "lead_days": 4,  "tags": ["standard","FHD","popular"],      "rating": 4.6, "reviews": 17832},
    {"id": "B09-MON-002",  "title": "LG 27\" 4K UHD USB-C Monitor 27UK850",          "category": "Monitors",        "emoji": "🖥️", "unit_price": 349.00, "availability": "available", "min_qty": 10,  "max_qty": 3000,   "lead_days": 5,  "tags": ["4K","USB-C"],                    "rating": 4.7, "reviews": 6290},
    {"id": "B07-MON-003",  "title": "Samsung 34\" Ultrawide Curved Monitor",          "category": "Monitors",        "emoji": "🖥️", "unit_price": 699.00, "availability": "sourcing",  "min_qty": 25,  "max_qty": None,   "lead_days": None,"tags": ["ultrawide","premium"],           "rating": 4.5, "reviews": 2140},
    {"id": "B08-KB-001",   "title": "Logitech MK540 Wireless Keyboard & Mouse Combo","category": "Keyboards & Mice","emoji": "⌨️", "unit_price": 49.99,  "availability": "available", "min_qty": 1,   "max_qty": 50000,  "lead_days": 2,  "tags": ["wireless","combo","budget"],      "rating": 4.4, "reviews": 34120},
    {"id": "B09-KB-002",   "title": "Microsoft Sculpt Ergonomic Desktop Set",         "category": "Keyboards & Mice","emoji": "⌨️", "unit_price": 89.99,  "availability": "available", "min_qty": 10,  "max_qty": 10000,  "lead_days": 3,  "tags": ["ergonomic","wireless"],           "rating": 4.3, "reviews": 11870},
    {"id": "B08-CAM-001",  "title": "Logitech C920 HD Pro Webcam 1080p",             "category": "Webcams",         "emoji": "📷", "unit_price": 69.99,  "availability": "available", "min_qty": 1,   "max_qty": 20000,  "lead_days": 2,  "tags": ["standard","1080p","popular"],    "rating": 4.5, "reviews": 28943},
    {"id": "B09-CAM-002",  "title": "Poly Studio P5 Professional Webcam",             "category": "Webcams",         "emoji": "📷", "unit_price": 99.99,  "availability": "available", "min_qty": 10,  "max_qty": 5000,   "lead_days": 4,  "tags": ["professional","noise-cancel"],   "rating": 4.6, "reviews": 4320},
    {"id": "B08-HS-001",   "title": "Jabra Evolve 20 USB Mono Headset",              "category": "Headsets",        "emoji": "🎧", "unit_price": 44.99,  "availability": "available", "min_qty": 1,   "max_qty": 20000,  "lead_days": 2,  "tags": ["budget","UC-certified"],         "rating": 4.3, "reviews": 7650},
    {"id": "B09-HS-002",   "title": "Poly Voyager Focus 2 Wireless Headset",          "category": "Headsets",        "emoji": "🎧", "unit_price": 199.99, "availability": "available", "min_qty": 10,  "max_qty": 5000,   "lead_days": 4,  "tags": ["wireless","ANC","professional"], "rating": 4.7, "reviews": 3891},
    {"id": "B08-DOCK-001", "title": "Anker 13-in-1 USB-C Docking Station",           "category": "Docking Stations","emoji": "🔌", "unit_price": 89.99,  "availability": "available", "min_qty": 1,   "max_qty": 10000,  "lead_days": 3,  "tags": ["USB-C","universal"],             "rating": 4.4, "reviews": 9210},
    {"id": "B09-LAP-001",  "title": "Lenovo ThinkPad L14 Gen 4 (i5, 16GB, 512GB)",  "category": "Laptops",         "emoji": "💻", "unit_price": 799.00, "availability": "sourcing",  "min_qty": 10,  "max_qty": None,   "lead_days": None,"tags": ["business","reliable"],           "rating": 4.5, "reviews": 2341},
    {"id": "B08-LAP-002",  "title": "Dell Latitude 5540 (i7, 16GB, 512GB)",          "category": "Laptops",         "emoji": "💻", "unit_price": 1099.00,"availability": "sourcing",  "min_qty": 25,  "max_qty": None,   "lead_days": None,"tags": ["business","popular"],            "rating": 4.6, "reviews": 1892},
    {"id": "B07-LAP-003",  "title": "Apple MacBook Air M2 (16GB, 512GB)",             "category": "Laptops",         "emoji": "💻", "unit_price": 1299.00,"availability": "sourcing",  "min_qty": 50,  "max_qty": None,   "lead_days": None,"tags": ["Apple","premium"],               "rating": 4.8, "reviews": 8712},
    {"id": "B08-OFF-001",  "title": "AmazonBasics Office Supply Starter Kit",         "category": "Office Supplies", "emoji": "📎", "unit_price": 24.99,  "availability": "available", "min_qty": 1,   "max_qty": 100000, "lead_days": 1,  "tags": ["bundle","essentials"],           "rating": 4.2, "reviews": 45230},
]

CATALOG_BY_ID = {p["id"]: p for p in CATALOG}

QUICK_STARTS = [
    "Nike is going fully remote for 5,000 employees. Need desks, ergonomic chairs, monitors, keyboard & mouse, and webcams. Budget is $400 per person. Standard options, nothing premium. 60 days.",
    "Hospital network, 80 locations, 20 staff each. Need keyboards, webcams for telehealth, and headsets for admin. Tight budget, fast shipping is critical.",
    "Tech startup hiring 200 engineers over 3 months. Need laptops (prefer MacBook or Dell), monitors, and docking stations. $2,500 per person. First 50 sets in 2 weeks.",
]

# ─── CSS — Amazon-style skin ──────────────────────────────────────────────────

AMAZON_CSS = """
<style>
/* ── Reset Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp { background: #EAEDED !important; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #232F3E !important; }
section[data-testid="stSidebar"] * { color: #fff !important; }
section[data-testid="stSidebar"] .stTextInput input { color: #111 !important; }
section[data-testid="stSidebar"] hr { border-color: #444 !important; }

/* ── Header ── */
.amz-header {
    background: #131921;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 0;
}
.amz-logo { color: #FF9900; font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px; }
.amz-logo span { color: #fff; }
.amz-logo-tag { color: #ccc; font-size: 0.7rem; margin-top: -2px; }
.amz-nav {
    background: #232F3E;
    padding: 6px 24px;
    font-size: 0.82rem;
    color: #ddd;
    display: flex;
    gap: 20px;
    margin-bottom: 12px;
}
.amz-nav span { cursor: pointer; }
.amz-nav span:hover { color: #FF9900; }

/* ── Chat bubbles ── */
.chat-wrap { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.bubble-user {
    background: #FF9900;
    color: #111;
    padding: 10px 14px;
    border-radius: 18px 18px 4px 18px;
    max-width: 88%;
    margin-left: auto;
    font-size: 0.88rem;
    font-weight: 500;
}
.bubble-agent {
    background: #fff;
    color: #111;
    padding: 10px 14px;
    border-radius: 18px 18px 18px 4px;
    max-width: 88%;
    border: 1px solid #ddd;
    font-size: 0.88rem;
    line-height: 1.5;
}
.bubble-agent-name {
    font-size: 0.72rem;
    color: #888;
    margin-bottom: 3px;
    font-weight: 600;
}

/* ── Product cards ── */
.prod-card {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 10px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}
.prod-img {
    width: 72px;
    height: 72px;
    background: #f5f5f5;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    flex-shrink: 0;
    border: 1px solid #eee;
}
.prod-info { flex: 1; min-width: 0; }
.prod-title { font-size: 0.88rem; color: #0F1111; font-weight: 500; margin-bottom: 3px; line-height: 1.3; }
.prod-title a { color: #007185; text-decoration: none; }
.prod-rating { font-size: 0.78rem; color: #007185; margin-bottom: 2px; }
.prod-stars { color: #FF9900; }
.prod-price { font-size: 1.15rem; color: #B12704; font-weight: 700; margin-bottom: 2px; }
.prod-price-sub { font-size: 0.75rem; color: #555; }
.prod-badge-contracted {
    display: inline-block;
    background: #007600;
    color: #fff;
    font-size: 0.7rem;
    padding: 2px 7px;
    border-radius: 3px;
    font-weight: 600;
    margin-bottom: 4px;
}
.prod-badge-sourcing {
    display: inline-block;
    background: #8B4513;
    color: #fff;
    font-size: 0.7rem;
    padding: 2px 7px;
    border-radius: 3px;
    font-weight: 600;
    margin-bottom: 4px;
}
.prod-avail-yes { font-size: 0.78rem; color: #007600; font-weight: 600; }
.prod-avail-no  { font-size: 0.78rem; color: #8B4513; font-weight: 600; }

/* ── Catalog panel ── */
.catalog-panel {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 14px;
}
.catalog-header {
    font-size: 1rem;
    font-weight: 700;
    color: #0F1111;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
}
.catalog-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 6px 0;
    border-bottom: 1px solid #f5f5f5;
    gap: 8px;
}
.catalog-item-title { font-size: 0.78rem; color: #0F1111; flex: 1; line-height: 1.3; }
.catalog-item-price { font-size: 0.82rem; color: #B12704; font-weight: 700; white-space: nowrap; }
.catalog-total {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 2px solid #eee;
    display: flex;
    justify-content: space-between;
    font-weight: 700;
    font-size: 0.9rem;
}
.activate-btn {
    background: #FF9900;
    color: #111;
    border: none;
    border-radius: 20px;
    padding: 8px 0;
    width: 100%;
    font-weight: 700;
    font-size: 0.88rem;
    cursor: pointer;
    margin-top: 10px;
    text-align: center;
    display: block;
}
.sourcing-note {
    background: #FFF3CD;
    border: 1px solid #FFD700;
    border-radius: 4px;
    padding: 8px 10px;
    font-size: 0.75rem;
    color: #5D4037;
    margin-top: 8px;
}

/* ── Misc ── */
.section-label {
    font-size: 0.75rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    font-weight: 600;
}
.time-banner {
    background: #E8F4FD;
    border: 1px solid #B3D7F5;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.83rem;
    color: #0F1111;
    margin-top: 10px;
}
.stButton > button {
    background: #FF9900 !important;
    color: #111 !important;
    border: 1px solid #FF8C00 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: #FFB347 !important;
}
div[data-testid="stTextArea"] textarea {
    border-radius: 4px !important;
    border: 2px solid #FF9900 !important;
    font-size: 0.88rem !important;
}
</style>
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────

def stars(rating: float) -> str:
    full = int(rating)
    return "★" * full + "☆" * (5 - full)


def _extract_json(text: str) -> dict:
    try:
        start = text.find("{")
        end   = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


def product_card_html(product: dict, qty: int, in_catalog: bool) -> str:
    avail     = product.get("availability", "")
    price     = product.get("unit_price", 0)
    total     = price * qty
    rating    = product.get("rating", 0)
    reviews   = product.get("reviews", 0)
    emoji     = product.get("emoji", "📦")
    lead      = f"In Stock — ships in {product['lead_days']} business days" if product.get("lead_days") else "Contact vendor for availability"
    badge     = '<span class="prod-badge-contracted">✓ Contracted Price</span>' if avail == "available" else '<span class="prod-badge-sourcing">⏳ Needs Sourcing</span>'
    avail_txt = f'<div class="prod-avail-yes">✓ {lead}</div>' if avail == "available" else f'<div class="prod-avail-no">⏳ {lead}</div>'
    added_note = '<div style="font-size:0.75rem;color:#007600;font-weight:600;margin-top:4px">✓ Added to catalog</div>' if in_catalog else ""

    return f"""
<div class="prod-card">
  <div class="prod-img">{emoji}</div>
  <div class="prod-info">
    <div class="prod-title">{product['title']}</div>
    <div class="prod-rating"><span class="prod-stars">{stars(rating)}</span> {rating} ({reviews:,} business ratings)</div>
    {badge}
    <div class="prod-price">${price:,.2f} <span style="font-size:0.78rem;color:#555;font-weight:400">/ unit</span></div>
    <div class="prod-price-sub">×{qty:,} units = <strong>${total:,.0f} total</strong></div>
    {avail_txt}
    {added_note}
  </div>
</div>"""


def catalog_panel_html(catalog_items: list, qty_map: dict) -> str:
    if not catalog_items:
        return """
<div class="catalog-panel">
  <div class="catalog-header">🗂️ Your Hosted Catalog</div>
  <div style="color:#888;font-size:0.82rem;text-align:center;padding:20px 0">
    Your catalog is empty.<br>Ask the assistant to find items.
  </div>
</div>"""

    items_html = ""
    total = 0
    sourcing_count = 0

    for item_id in catalog_items:
        prod = CATALOG_BY_ID.get(item_id)
        if not prod:
            continue
        qty   = qty_map.get(item_id, 1)
        price = prod["unit_price"]
        line  = price * qty
        total += line
        if prod["availability"] == "sourcing":
            sourcing_count += 1
        short_title = prod["title"][:42] + "…" if len(prod["title"]) > 42 else prod["title"]
        items_html += f"""
<div class="catalog-item">
  <div class="catalog-item-title">{prod['emoji']} {short_title}<br><span style="color:#888;font-size:0.72rem">×{qty:,} units</span></div>
  <div class="catalog-item-price">${line:,.0f}</div>
</div>"""

    sourcing_note = f'<div class="sourcing-note">⏳ {sourcing_count} item(s) need vendor negotiation — will be submitted to Amazon Business team.</div>' if sourcing_count else ""

    return f"""
<div class="catalog-panel">
  <div class="catalog-header">🗂️ Your Hosted Catalog <span style="color:#888;font-size:0.78rem;font-weight:400">({len(catalog_items)} items)</span></div>
  {items_html}
  <div class="catalog-total">
    <span>Est. Contract Value</span>
    <span style="color:#B12704">${total:,.0f}</span>
  </div>
  {sourcing_note}
  <div class="activate-btn">Activate Catalog</div>
  <div class="time-banner">
    ⚡ Traditional catalog creation: <strong>6–8 weeks</strong><br>
    🤖 AI-assisted: <strong>minutes</strong>
  </div>
</div>"""


# ─── Agent ────────────────────────────────────────────────────────────────────

def chat_agent(client: anthropic.Anthropic, history: list, user_msg: str,
               catalog_ids: list, requirements: dict) -> dict:
    """
    Single Claude call that handles the full Rufus-style conversation:
    - Understands what the admin is asking
    - Returns a conversational response
    - Returns product IDs to surface from the catalog
    - Handles add/remove from catalog
    """
    catalog_json = json.dumps(CATALOG, indent=2)
    current_catalog = json.dumps([CATALOG_BY_ID.get(i, {}) for i in catalog_ids], indent=2)

    system = f"""You are the Amazon Business AI Catalog Assistant — the B2B equivalent of Amazon's Rufus shopping assistant.

Your job: Help procurement admins build Hosted Catalogs for their companies.

WHAT IS A HOSTED CATALOG:
A Hosted Catalog is a curated set of pre-approved items at contracted prices that a company's employees can purchase. It prevents overspending by setting guardrails — only approved items at negotiated prices. Example: Nike goes remote, admin creates a catalog with exactly 5 items (desk, chair, monitor, keyboard, webcam) all under $300/each, so no employee can buy a $1,000 chair.

YOUR BEHAVIOR:
- Be conversational, helpful, like a knowledgeable Amazon Business rep
- When the admin describes their needs, identify which CATALOG items best match
- Recommend specific items from the catalog (use real IDs and titles)
- If an item is "sourcing" status, acknowledge it needs vendor negotiation but still recommend it if it's the best fit
- Help the admin refine their selections — too many results is not helpful, narrow it down
- When admin says "add [item] to my catalog" or equivalent, include its ID in catalog_add
- Keep responses concise — 2-4 sentences max, then let the products do the talking

FULL AMAZON BUSINESS CATALOG:
{catalog_json}

CURRENT ADMIN'S CATALOG:
{current_catalog if catalog_ids else "Empty — nothing added yet"}

EXTRACTED REQUIREMENTS SO FAR:
{json.dumps(requirements, indent=2) if requirements else "None yet"}

Respond with ONLY valid JSON — no prose outside the JSON:
{{
  "message": "<your conversational response — 2-4 sentences, friendly and specific>",
  "product_ids": ["<IDs of products to display — max 6, most relevant first>"],
  "catalog_add": ["<IDs to add to the admin's catalog — only if they explicitly asked to add, or you're building a full catalog on their request>"],
  "catalog_remove": ["<IDs to remove — if asked>"],
  "requirements_update": {{
    "company": "<if mentioned>",
    "headcount": <integer or null>,
    "budget_per_person": <float or null>,
    "timeline_days": <integer or null>
  }},
  "show_time_savings": <true if catalog is now substantially complete>
}}"""

    messages = []
    for h in history[-8:]:  # last 8 turns for context
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})

    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=system,
        messages=messages,
    ) as stream:
        response = stream.get_final_message()

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    return _extract_json(text)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Amazon Business — Catalog AI",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject Amazon CSS
    st.markdown(AMAZON_CSS, unsafe_allow_html=True)

    # Amazon-style header
    st.markdown("""
<div class="amz-header">
  <div>
    <div class="amz-logo">amazon<span>business</span></div>
    <div class="amz-logo-tag">Hosted Catalog AI Assistant</div>
  </div>
</div>
<div class="amz-nav">
  <span>📋 All Categories</span>
  <span>🖥️ Computers & Monitors</span>
  <span>🪑 Office Furniture</span>
  <span>⌨️ Peripherals</span>
  <span>💼 Office Supplies</span>
  <span style="color:#FF9900;font-weight:600">✨ AI Catalog Builder</span>
</div>
""", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        api_key = st.text_input("Anthropic API Key", type="password", help="sk-ant-…")
        st.divider()
        st.markdown("""
**What is a Hosted Catalog?**

A curated set of approved items at contracted prices — so employees buy only what's approved, at the right price.

**Today:** 6–8 weeks of back-and-forth with Amazon Business sales reps.

**With AI:** Describe what you need. Get your catalog in minutes.

---
Built by [Rav Riar](https://github.com/ravriar29)
Sr PM Technical · Amazon Business
        """)

        if st.button("🗑️ Reset Conversation", use_container_width=True):
            for key in ["messages", "products", "catalog_ids", "qty_map", "requirements"]:
                st.session_state.pop(key, None)
            st.rerun()

    # Session state init
    if "messages"    not in st.session_state: st.session_state.messages    = []
    if "products"    not in st.session_state: st.session_state.products    = []
    if "catalog_ids" not in st.session_state: st.session_state.catalog_ids = []
    if "qty_map"     not in st.session_state: st.session_state.qty_map     = {}
    if "requirements"not in st.session_state: st.session_state.requirements= {}

    if not api_key:
        st.markdown("""
<div style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:24px;max-width:700px;margin:20px auto">
  <div style="font-size:1.3rem;font-weight:700;margin-bottom:8px">👋 Welcome to Amazon Business Catalog AI</div>
  <div style="color:#555;font-size:0.9rem;margin-bottom:16px">
    Tell the AI assistant what your company needs. It will search the Amazon Business catalog,
    find the right items for your budget and headcount, and build your Hosted Catalog —
    reducing weeks of work to minutes.
  </div>
  <div style="font-size:0.85rem;font-weight:600;margin-bottom:8px">Try asking:</div>
  <div style="background:#f5f5f5;border-radius:4px;padding:10px 14px;font-size:0.83rem;color:#333;margin-bottom:6px">
    "Nike is going remote — 5,000 employees need desks, chairs, monitors, keyboard and mouse, webcams. $400/person budget."
  </div>
  <div style="background:#f5f5f5;border-radius:4px;padding:10px 14px;font-size:0.83rem;color:#333;margin-bottom:6px">
    "We're a hospital with 80 locations. Need keyboards, webcams for telehealth, and headsets for admin staff. Tight budget."
  </div>
  <div style="background:#f5f5f5;border-radius:4px;padding:10px 14px;font-size:0.83rem;color:#333">
    "200 engineers joining over 3 months. Need MacBooks or Dell laptops, monitors, docking stations. $2,500/person."
  </div>
  <div style="margin-top:16px;color:#888;font-size:0.8rem">👈 Add your Anthropic API key in the sidebar to get started.</div>
</div>
""", unsafe_allow_html=True)
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Main layout: chat+products | catalog
    col_main, col_catalog = st.columns([2, 1], gap="medium")

    with col_main:
        # ── Chat history ──────────────────────────────────────────────────────
        if st.session_state.messages:
            bubbles_html = '<div class="chat-wrap">'
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    bubbles_html += f'<div class="bubble-user">{msg["content"]}</div>'
                else:
                    bubbles_html += f'<div><div class="bubble-agent-name">🤖 Amazon Business AI</div><div class="bubble-agent">{msg["content"]}</div></div>'
            bubbles_html += "</div>"
            st.markdown(bubbles_html, unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:16px;margin-bottom:12px">
  <div style="font-size:1rem;font-weight:700;margin-bottom:4px">🤖 Amazon Business AI Catalog Assistant</div>
  <div style="font-size:0.85rem;color:#555">
    Hi! I'm here to help you build your company's Hosted Catalog. Tell me what you need —
    your company size, what items you're looking for, and your budget — and I'll find the
    right products from the Amazon Business catalog.
  </div>
</div>""", unsafe_allow_html=True)

        # ── Quick-start chips ────────────────────────────────────────────────
        if not st.session_state.messages:
            st.markdown('<div class="section-label">Quick-start scenarios</div>', unsafe_allow_html=True)
            qc1, qc2, qc3 = st.columns(3)
            labels = ["🏃 Nike WFH Rollout", "🏥 Hospital Network", "🚀 Tech Startup"]
            for i, (col, label, scenario) in enumerate(zip([qc1, qc2, qc3], labels, QUICK_STARTS)):
                if col.button(label, key=f"qs_{i}", use_container_width=True):
                    st.session_state["prefill"] = scenario
                    st.rerun()

        # ── Input ────────────────────────────────────────────────────────────
        prefill = st.session_state.pop("prefill", "")
        user_input = st.text_area(
            "",
            value=prefill,
            placeholder="What does your company need? (e.g. 'Nike going remote, 5,000 employees, need desks, chairs, monitors, webcams, $400/person')",
            height=80,
            label_visibility="collapsed",
            key="chat_input",
        )
        send = st.button("Send ➤", use_container_width=False)

        # ── Process message ──────────────────────────────────────────────────
        if send and user_input.strip():
            with st.spinner("🤖 Amazon Business AI is thinking…"):
                result = chat_agent(
                    client,
                    st.session_state.messages,
                    user_input.strip(),
                    st.session_state.catalog_ids,
                    st.session_state.requirements,
                )

            # Update conversation
            st.session_state.messages.append({"role": "user",      "content": user_input.strip()})
            st.session_state.messages.append({"role": "assistant",  "content": result.get("message", "Let me find that for you.")})

            # Update products shown
            if result.get("product_ids"):
                st.session_state.products = result["product_ids"]

            # Update catalog
            for pid in result.get("catalog_add", []):
                if pid not in st.session_state.catalog_ids:
                    st.session_state.catalog_ids.append(pid)
            for pid in result.get("catalog_remove", []):
                if pid in st.session_state.catalog_ids:
                    st.session_state.catalog_ids.remove(pid)

            # Update requirements
            req_update = result.get("requirements_update", {})
            if req_update:
                for k, v in req_update.items():
                    if v is not None:
                        st.session_state.requirements[k] = v

            # Set qty for catalog items based on headcount
            headcount = st.session_state.requirements.get("headcount", 1) or 1
            for pid in st.session_state.catalog_ids:
                if pid not in st.session_state.qty_map:
                    st.session_state.qty_map[pid] = headcount

            st.rerun()

        # ── Product results ──────────────────────────────────────────────────
        if st.session_state.products:
            st.markdown('<div class="section-label" style="margin-top:16px">Search Results — Amazon Business Catalog</div>', unsafe_allow_html=True)
            headcount = st.session_state.requirements.get("headcount", 1) or 1

            for pid in st.session_state.products:
                prod = CATALOG_BY_ID.get(pid)
                if not prod:
                    continue
                qty        = st.session_state.qty_map.get(pid, headcount)
                in_catalog = pid in st.session_state.catalog_ids

                st.markdown(product_card_html(prod, qty, in_catalog), unsafe_allow_html=True)

                if not in_catalog:
                    if st.button(f"＋ Add to Catalog — {prod['title'][:35]}…" if len(prod['title']) > 35 else f"＋ Add to Catalog — {prod['title']}",
                                 key=f"add_{pid}", use_container_width=False):
                        st.session_state.catalog_ids.append(pid)
                        st.session_state.qty_map[pid] = qty
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"✓ Added **{prod['title']}** to your catalog ({qty:,} units at ${prod['unit_price']:,.2f}/unit = ${prod['unit_price']*qty:,.0f} total)."
                        })
                        st.rerun()
                else:
                    if st.button(f"✓ Remove from Catalog — {prod['title'][:32]}…" if len(prod['title']) > 32 else f"✓ Remove from Catalog — {prod['title']}",
                                 key=f"rem_{pid}", use_container_width=False):
                        st.session_state.catalog_ids.remove(pid)
                        st.session_state.qty_map.pop(pid, None)
                        st.rerun()

    # ── Catalog panel (right column) ──────────────────────────────────────────
    with col_catalog:
        st.markdown(
            catalog_panel_html(st.session_state.catalog_ids, st.session_state.qty_map),
            unsafe_allow_html=True,
        )

        # Requirements summary
        req = st.session_state.requirements
        if req:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div style="font-size:0.75rem;color:#555;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Requirements on file</div>""", unsafe_allow_html=True)
            if req.get("company"):
                st.caption(f"🏢 **Company:** {req['company']}")
            if req.get("headcount"):
                st.caption(f"👥 **Employees:** {req['headcount']:,}")
            if req.get("budget_per_person"):
                st.caption(f"💰 **Budget/person:** ${req['budget_per_person']:,.0f}")
            if req.get("timeline_days"):
                st.caption(f"📅 **Timeline:** {req['timeline_days']} days")


if __name__ == "__main__":
    main()
