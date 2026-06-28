"""
Amazon Business — Hosted Catalog AI Assistant
Amazon Business-style UI with floating AI chat widget.
Overview page + product browsing + Rufus-style conversational catalog builder.

Built by Rav Riar | Sr PM Technical, Amazon Business
Claude Opus 4.8 + Streamlit
"""

import streamlit as st
import anthropic
import json

MODEL = "claude-opus-4-8"

# ─── Product Catalog ──────────────────────────────────────────────────────────

CATALOG = [
    {"id":"B09-DESK-002","title":"FlexiSpot E1 Electric Standing Desk 55\"",       "category":"Desks",            "img":"🗃️","unit_price":279.00,"availability":"available","min_qty":10, "max_qty":5000, "lead_days":5, "rating":4.6,"reviews":12847,"tags":["standing","ergonomic","popular"]},
    {"id":"B08-DESK-001","title":"AmazonBasics Adjustable Desk 48\"",               "category":"Desks",            "img":"🗃️","unit_price":149.99,"availability":"available","min_qty":1,  "max_qty":10000,"lead_days":3, "rating":4.3,"reviews":8231, "tags":["budget","adjustable"]},
    {"id":"B07-DESK-003","title":"Fully Jarvis Bamboo Standing Desk 60\"",          "category":"Desks",            "img":"🗃️","unit_price":549.00,"availability":"sourcing", "min_qty":50, "max_qty":None,  "lead_days":None,"rating":4.8,"reviews":3102, "tags":["premium","sustainable"]},
    {"id":"B09-CHR-002", "title":"HON Ignition 2.0 Ergonomic Task Chair",          "category":"Chairs",           "img":"🪑","unit_price":249.00,"availability":"available","min_qty":25, "max_qty":5000, "lead_days":7, "rating":4.5,"reviews":9403, "tags":["ergonomic","lumbar","popular"]},
    {"id":"B08-CHR-001", "title":"AmazonBasics Mid-Back Mesh Office Chair",         "category":"Chairs",           "img":"🪑","unit_price":119.99,"availability":"available","min_qty":1,  "max_qty":20000,"lead_days":3, "rating":4.1,"reviews":21560,"tags":["budget","mesh"]},
    {"id":"B07-CHR-003", "title":"Herman Miller Aeron Chair (Size B)",              "category":"Chairs",           "img":"🪑","unit_price":1395.00,"availability":"sourcing","min_qty":50, "max_qty":None,  "lead_days":None,"rating":4.9,"reviews":5671, "tags":["premium","ergonomic"]},
    {"id":"B08-MON-001", "title":"Dell 24\" FHD IPS Monitor P2422H",               "category":"Monitors",         "img":"🖥️","unit_price":199.99,"availability":"available","min_qty":5,  "max_qty":10000,"lead_days":4, "rating":4.6,"reviews":17832,"tags":["standard","FHD","popular"]},
    {"id":"B09-MON-002", "title":"LG 27\" 4K UHD USB-C Monitor 27UK850",           "category":"Monitors",         "img":"🖥️","unit_price":349.00,"availability":"available","min_qty":10, "max_qty":3000, "lead_days":5, "rating":4.7,"reviews":6290, "tags":["4K","USB-C"]},
    {"id":"B07-MON-003", "title":"Samsung 34\" Ultrawide Curved Monitor",           "category":"Monitors",         "img":"🖥️","unit_price":699.00,"availability":"sourcing", "min_qty":25, "max_qty":None,  "lead_days":None,"rating":4.5,"reviews":2140, "tags":["ultrawide","premium"]},
    {"id":"B08-KB-001",  "title":"Logitech MK540 Wireless Keyboard & Mouse Combo", "category":"Keyboards & Mice", "img":"⌨️","unit_price":49.99, "availability":"available","min_qty":1,  "max_qty":50000,"lead_days":2, "rating":4.4,"reviews":34120,"tags":["wireless","combo","budget"]},
    {"id":"B09-KB-002",  "title":"Microsoft Sculpt Ergonomic Desktop Set",          "category":"Keyboards & Mice", "img":"⌨️","unit_price":89.99, "availability":"available","min_qty":10, "max_qty":10000,"lead_days":3, "rating":4.3,"reviews":11870,"tags":["ergonomic","wireless"]},
    {"id":"B08-CAM-001", "title":"Logitech C920 HD Pro Webcam 1080p",              "category":"Webcams",          "img":"📷","unit_price":69.99, "availability":"available","min_qty":1,  "max_qty":20000,"lead_days":2, "rating":4.5,"reviews":28943,"tags":["standard","1080p","popular"]},
    {"id":"B09-CAM-002", "title":"Poly Studio P5 Professional Webcam",              "category":"Webcams",          "img":"📷","unit_price":99.99, "availability":"available","min_qty":10, "max_qty":5000, "lead_days":4, "rating":4.6,"reviews":4320, "tags":["professional"]},
    {"id":"B08-HS-001",  "title":"Jabra Evolve 20 USB Mono Headset",               "category":"Headsets",         "img":"🎧","unit_price":44.99, "availability":"available","min_qty":1,  "max_qty":20000,"lead_days":2, "rating":4.3,"reviews":7650, "tags":["budget","UC-certified"]},
    {"id":"B09-HS-002",  "title":"Poly Voyager Focus 2 Wireless Headset",           "category":"Headsets",         "img":"🎧","unit_price":199.99,"availability":"available","min_qty":10, "max_qty":5000, "lead_days":4, "rating":4.7,"reviews":3891, "tags":["wireless","ANC"]},
    {"id":"B08-DOCK-001","title":"Anker 13-in-1 USB-C Docking Station",            "category":"Docking Stations", "img":"🔌","unit_price":89.99, "availability":"available","min_qty":1,  "max_qty":10000,"lead_days":3, "rating":4.4,"reviews":9210, "tags":["USB-C","universal"]},
    {"id":"B09-LAP-001", "title":"Lenovo ThinkPad L14 Gen 4 (i5, 16GB, 512GB)",   "category":"Laptops",          "img":"💻","unit_price":799.00, "availability":"sourcing","min_qty":10, "max_qty":None,  "lead_days":None,"rating":4.5,"reviews":2341, "tags":["business","reliable"]},
    {"id":"B08-LAP-002", "title":"Dell Latitude 5540 (i7, 16GB, 512GB)",           "category":"Laptops",          "img":"💻","unit_price":1099.00,"availability":"sourcing","min_qty":25, "max_qty":None,  "lead_days":None,"rating":4.6,"reviews":1892, "tags":["business","popular"]},
    {"id":"B07-LAP-003", "title":"Apple MacBook Air M2 (16GB, 512GB)",              "category":"Laptops",          "img":"💻","unit_price":1299.00,"availability":"sourcing","min_qty":50, "max_qty":None,  "lead_days":None,"rating":4.8,"reviews":8712, "tags":["Apple","premium"]},
    {"id":"B08-OFF-001", "title":"AmazonBasics Office Supply Starter Kit",          "category":"Office Supplies",  "img":"📎","unit_price":24.99, "availability":"available","min_qty":1,  "max_qty":100000,"lead_days":1, "rating":4.2,"reviews":45230,"tags":["bundle","essentials"]},
]

CATALOG_BY_ID = {p["id"]: p for p in CATALOG}
ALL_CATEGORIES = sorted(set(p["category"] for p in CATALOG))

QUICK_TEMPLATES = {
    "🏠 WFH Setup": (
        "WFH Scenario — please fill in your details:\n\n"
        "Items needed: [e.g. desk, chair, monitor, keyboard & mouse, webcam]\n"
        "Number of employees: [e.g. 500]\n"
        "Budget per person: $[e.g. 400]\n"
        "Shipping speed needed: [e.g. standard / within 30 days / urgent]\n"
        "Anything else: [e.g. ergonomic preferred, no premium brands]"
    ),
    "🏥 Office / Facility": (
        "Office/Facility Scenario — please fill in your details:\n\n"
        "Items needed: [e.g. keyboards, webcams, headsets, office supplies]\n"
        "Number of locations or employees: [e.g. 80 locations, 20 staff each]\n"
        "Budget per person or per location: $[e.g. 150/person]\n"
        "Shipping speed needed: [e.g. fast — within 2 weeks]\n"
        "Anything else: [e.g. tight budget, telehealth stations]"
    ),
    "🚀 New Hire Onboarding": (
        "New Hire Onboarding Scenario — please fill in your details:\n\n"
        "Items needed: [e.g. laptop, monitor, docking station, keyboard & mouse]\n"
        "Number of new hires: [e.g. 200 engineers]\n"
        "Budget per person: $[e.g. 2500]\n"
        "Shipping speed needed: [e.g. first 50 kits within 2 weeks]\n"
        "Anything else: [e.g. prefer MacBook or Dell, all remote employees]"
    ),
}

# ─── CSS ─────────────────────────────────────────────────────────────────────

CSS = """
<style>
/* ── Global: Amazon Business light theme ── */
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: #F2F0EB !important; }
.block-container { padding-top: 0 !important; max-width: 1300px !important; }

/* ── Fix all Streamlit headings to be dark ── */
h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #0F1111 !important;
}

/* ── Sidebar (left filter panel) ── */
section[data-testid="stSidebar"] {
    background: #fff !important;
    border-right: 1px solid #ddd !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown { color: #111 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #111 !important; }

/* ── Top header bar ── */
.amzb-header {
    background: #fff;
    border-bottom: 1px solid #ddd;
    padding: 10px 0 8px 0;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 16px;
}
.amzb-logo {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: #000;
}
.amzb-logo-orange { color: #E47911; }
.amzb-logo-biz { font-size: 0.65rem; color: #E47911; font-weight: 700; letter-spacing: 1px; display: block; margin-top: -4px; }
.amzb-tagline { font-size: 0.78rem; color: #555; }

/* ── Orange nav strip ── */
.amzb-nav {
    background: #232F3E;
    padding: 7px 16px;
    font-size: 0.8rem;
    color: #ddd;
    display: flex;
    gap: 24px;
    margin-bottom: 0;
}
.amzb-nav a { color: #ddd !important; text-decoration: none; }
.amzb-nav a:hover { color: #FF9900 !important; }

/* ── Page tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #fff;
    border-bottom: 2px solid #e47911;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem;
    font-weight: 600;
    color: #555;
    padding: 10px 20px;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    background: #fff !important;
    color: #E47911 !important;
    border-bottom: 3px solid #E47911 !important;
}

/* ── Product cards ── */
.prod-card {
    background: #fff;
    border: 1px solid #DDD;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 12px;
    transition: box-shadow 0.15s;
}
.prod-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.prod-img-box {
    background: #F7F7F7;
    border: 1px solid #eee;
    border-radius: 4px;
    width: 100%;
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.8rem;
    margin-bottom: 10px;
}
.prod-title { font-size: 0.82rem; color: #0066C0; font-weight: 500; margin-bottom: 5px; line-height: 1.35; min-height: 44px; }
.prod-stars { color: #E47911; font-size: 0.78rem; }
.prod-reviews { color: #007185; font-size: 0.74rem; }
.prod-bizprice-label { font-size: 0.68rem; color: #fff; background: #E47911; padding: 1px 6px; border-radius: 2px; font-weight: 700; display: inline-block; margin-bottom: 2px; }
.prod-price { font-size: 1.1rem; font-weight: 700; color: #0F1111; }
.prod-per-unit { font-size: 0.72rem; color: #666; }
.prod-avail-yes { font-size: 0.73rem; color: #007600; font-weight: 600; margin: 4px 0; }
.prod-avail-sourcing { font-size: 0.73rem; color: #B7791F; font-weight: 600; margin: 4px 0; }
.prod-add-btn {
    background: #FFD814;
    color: #111;
    border: 1px solid #FFA41C;
    border-radius: 20px;
    padding: 6px 0;
    width: 100%;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    margin-top: 8px;
    display: block;
}
.prod-added-btn {
    background: #E7F4E4;
    color: #007600;
    border: 1px solid #007600;
    border-radius: 20px;
    padding: 6px 0;
    width: 100%;
    font-size: 0.78rem;
    font-weight: 600;
    text-align: center;
    margin-top: 8px;
    display: block;
}

/* ── Catalog sidebar panel ── */
.catalog-box {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 12px;
}
.catalog-box-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0F1111;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
    margin-bottom: 10px;
}
.cat-item {
    font-size: 0.76rem;
    color: #0F1111;
    padding: 5px 0;
    border-bottom: 1px solid #f5f5f5;
    display: flex;
    justify-content: space-between;
    gap: 6px;
}
.cat-item-name { flex: 1; }
.cat-item-price { color: #B12704; font-weight: 700; white-space: nowrap; }
.cat-total { font-size: 0.85rem; font-weight: 700; color: #0F1111; margin-top: 8px; display: flex; justify-content: space-between; }

/* ── Chat panel (persistent right column) ── */
.chat-panel {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 100%;
}
.chat-panel-header {
    background: #232F3E;
    color: #fff;
    padding: 12px 14px;
    font-size: 0.85rem;
    font-weight: 700;
    border-radius: 10px 10px 0 0;
}
.chat-panel-header .chat-sub { font-size: 0.72rem; color: #aaa; font-weight: 400; margin-top: 1px; }
.chat-msgs {
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: #F7F7F7;
    min-height: 200px;
    max-height: 320px;
}
.msg-agent {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 12px 12px 12px 2px;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: #111;
    max-width: 90%;
    line-height: 1.4;
}
.msg-user {
    background: #E47911;
    color: #fff;
    border-radius: 12px 12px 2px 12px;
    padding: 8px 12px;
    font-size: 0.8rem;
    max-width: 90%;
    margin-left: auto;
    line-height: 1.4;
}
.msg-agent-name { font-size: 0.68rem; color: #888; margin-bottom: 2px; font-weight: 600; }

/* ── Overview page ── */
.hero-section {
    background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
    color: #fff;
    padding: 48px 40px;
    border-radius: 8px;
    margin-bottom: 24px;
}
.hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 12px; line-height: 1.2; }
.hero-sub { font-size: 1rem; color: #ccc; margin-bottom: 24px; line-height: 1.6; }
.hero-cta {
    background: #E47911;
    color: #fff;
    border: none;
    border-radius: 4px;
    padding: 12px 28px;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    display: inline-block;
}
.value-card {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 20px;
    height: 100%;
}
.value-icon { font-size: 2rem; margin-bottom: 10px; }
.value-title { font-size: 1rem; font-weight: 700; color: #0F1111; margin-bottom: 6px; }
.value-text { font-size: 0.82rem; color: #555; line-height: 1.55; }
.step-box {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 16px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}
.step-num {
    background: #E47911;
    color: #fff;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.9rem;
    flex-shrink: 0;
}
.step-title { font-size: 0.88rem; font-weight: 700; color: #0F1111; margin-bottom: 3px; }
.step-text { font-size: 0.78rem; color: #555; line-height: 1.45; }
.stat-box {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 20px;
    text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 800; color: #E47911; }
.stat-label { font-size: 0.78rem; color: #555; margin-top: 4px; }

/* ── Streamlit button overrides ── */
/* Default: yellow Amazon "Add to Cart" style */
.stButton > button {
    background: #FFD814 !important;
    color: #111 !important;
    border: 1px solid #FFA41C !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    width: 100% !important;
}
.stButton > button:hover { background: #F0C14B !important; }
/* Orange "catalog" buttons: wrap in a div.catalog-btn */
div.catalog-btn > div > button {
    background: #E47911 !important;
    color: #fff !important;
    border: 1px solid #C96A09 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 0.73rem !important;
    width: 100% !important;
}
div.catalog-btn > div > button:hover { background: #C96A09 !important; }
/* Green "in catalog" buttons: wrap in div.in-catalog-btn */
div.in-catalog-btn > div > button {
    background: #E7F4E4 !important;
    color: #007600 !important;
    border: 1px solid #007600 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 0.73rem !important;
    width: 100% !important;
}
/* Chat send button */
div.chat-send-btn > div > button {
    background: #E47911 !important;
    color: #fff !important;
    border: 1px solid #C96A09 !important;
    border-radius: 4px !important;
    width: 100% !important;
}
div[data-testid="stTextArea"] textarea {
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
    background: #fff !important;
}
div[data-testid="stTextInput"] input {
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
    background: #fff !important;
}
.stCheckbox label { font-size: 0.82rem !important; color: #111 !important; }
.stSelectbox label { font-size: 0.82rem !important; }
</style>
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    try:
        s = text.find("{"); e = text.rfind("}") + 1
        return json.loads(text[s:e])
    except Exception:
        return {}

def stars_html(r: float) -> str:
    return "★" * int(r) + "☆" * (5 - int(r))

def fmt_price(p: float) -> str:
    dollars = int(p)
    cents   = int(round((p - dollars) * 100))
    return f"<sup style='font-size:0.65rem;vertical-align:super'>${dollars}</sup><span style='font-size:1.1rem;font-weight:700'>{cents:02d}</span>"


# ─── Agent ────────────────────────────────────────────────────────────────────

def call_agent(client, history: list, user_msg: str, catalog_ids: list, requirements: dict) -> dict:
    catalog_str = json.dumps(CATALOG, indent=2)

    system = f"""You are the Amazon Business AI Catalog Assistant — the B2B equivalent of Rufus.

CONTEXT — What is a Hosted Catalog:
A Hosted Catalog is a curated set of pre-approved items at contracted prices that a company's employees are permitted to purchase. It prevents overspending by restricting employees to only approved items at pre-negotiated prices and quantities. Example: Nike goes remote — admin creates a catalog with exactly 5 items (desk, chair, monitor, keyboard, webcam) so no employee can order a $1,500 chair or a monitor they don't need.

YOUR JOB:
- Help procurement admins discover and select items for their Hosted Catalog
- Be conversational and specific — 2-4 sentences, then let products do the talking
- Recommend products that match the admin's budget, headcount, and requirements
- When admin says "add [item]" or "build me a full catalog", include IDs in catalog_add
- When showing products, pick the best 4-6 most relevant — not all 20

AMAZON BUSINESS CATALOG:
{catalog_str}

CURRENTLY IN ADMIN'S CATALOG: {json.dumps([CATALOG_BY_ID.get(i,{{}}).get("title") for i in catalog_ids])}
REQUIREMENTS ON FILE: {json.dumps(requirements)}

Return ONLY valid JSON:
{{
  "message": "<conversational reply — 2-4 sentences, specific>",
  "product_ids": ["<up to 6 most relevant product IDs>"],
  "catalog_add": ["<IDs to add — only when admin explicitly requests or asks to build full catalog>"],
  "catalog_remove": ["<IDs to remove>"],
  "req_update": {{"headcount": <int|null>, "budget_per_person": <float|null>, "company": "<str|null>", "timeline_days": <int|null>}}
}}"""

    msgs = [{"role": h["role"], "content": h["content"]} for h in history[-8:]]
    msgs.append({"role": "user", "content": user_msg})

    with client.messages.stream(
        model=MODEL, max_tokens=1500, thinking={"type": "adaptive"},
        system=system, messages=msgs,
    ) as stream:
        resp = stream.get_final_message()

    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    return _extract_json(text)


# ─── Pages ────────────────────────────────────────────────────────────────────

def page_overview():
    st.markdown("""
<div class="hero-section">
  <div class="hero-title">Build your company's Hosted Catalog<br>in minutes — not months.</div>
  <div class="hero-sub">
    Amazon Business Hosted Catalog gives your employees a curated set of approved items
    at pre-negotiated prices — so they always buy the right thing at the right price.
    Our AI assistant makes building that catalog faster than ever.
  </div>
</div>
""", unsafe_allow_html=True)

    # Value props
    st.markdown("### Why Hosted Catalog?")
    c1, c2, c3 = st.columns(3)
    cards = [
        ("💰", "Control Costs", "Employees can only purchase from a pre-approved list at contracted prices. No surprise $1,500 chairs. No off-contract spending. Every purchase stays within your negotiated budget."),
        ("✅", "Stay Compliant", "Every item in the catalog has been vetted and approved by your procurement team. Compliance is built in — employees can't accidentally buy from unapproved vendors."),
        ("⚡", "Move Fast", "Contracted items are ready to order immediately — no approval delays for routine purchases. Your team gets what they need, fast, without the procurement bottleneck."),
    ]
    for col, (icon, title, text) in zip([c1, c2, c3], cards):
        col.markdown(f"""
<div class="value-card">
  <div class="value-icon">{icon}</div>
  <div class="value-title">{title}</div>
  <div class="value-text">{text}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Real-world example
    st.markdown("### Real-world example: Nike goes remote")
    st.markdown("""
<div style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:20px 24px;margin-bottom:24px">
  <div style="font-size:0.88rem;color:#333;line-height:1.7">
    Nike decides all 5,000 corporate employees will work from home. Each employee needs a desk, chair, monitor, keyboard, and webcam.
    <br><br>
    <strong>Without a Hosted Catalog:</strong> Employees go to Amazon Business and search freely. One person orders a $150 desk. Another orders a $1,200 standing desk. Someone buys three monitors. Costs spiral and procurement has no visibility.
    <br><br>
    <strong>With a Hosted Catalog:</strong> Nike's procurement admin creates a catalog with exactly 5 approved items — each at a contracted price Amazon Business has negotiated for Nike's volume. Employees can only order from those 5 items. The $279 standing desk is the desk. The $249 ergonomic chair is the chair. Budget is controlled. Compliance is automatic.
    <br><br>
    <strong>The old way to build that catalog:</strong> 6–8 weeks of calls with Amazon Business sales reps, manual price negotiation, back-and-forth on quantities, slow approval loops.
    <br><br>
    <strong>With AI:</strong> Nike's admin describes what they need in one paragraph. The AI finds the right items from the catalog, flags what needs vendor negotiation, and delivers a draft catalog — ready to review in minutes.
  </div>
</div>
""", unsafe_allow_html=True)

    # How it works
    st.markdown("### How it works")
    steps = [
        ("Tell us what you need", "Describe your company's requirements in plain English — employees, categories, budget, timeline. No forms to fill out."),
        ("AI finds the right items", "The assistant searches the Amazon Business catalog and surfaces the best matches for your criteria — not 1,000 results, the right ones."),
        ("Review and add to catalog", "Browse AI-recommended items. Add what you want. The assistant flags anything that needs vendor negotiation and prepares the sourcing request."),
        ("Activate your catalog", "Your Hosted Catalog goes live. Employees can order immediately from the approved list. Contracted prices are locked in."),
    ]
    for i, (title, text) in enumerate(steps, 1):
        st.markdown(f"""
<div class="step-box" style="margin-bottom:10px">
  <div class="step-num">{i}</div>
  <div>
    <div class="step-title">{title}</div>
    <div class="step-text">{text}</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    st.markdown("### By the numbers")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("6–8 wks", "Traditional catalog creation time"),
        ("< 30 min", "AI-assisted catalog creation"),
        ("100%", "Price compliance for every employee purchase"),
        ("$0", "Off-contract spend when catalog is active"),
    ]
    for col, (num, label) in zip([s1, s2, s3, s4], stats):
        col.markdown(f"""
<div class="stat-box">
  <div class="stat-num">{num}</div>
  <div class="stat-label">{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Works with
    st.markdown("### Works with your procurement system")
    st.markdown("""
<div style="background:#fff;border:1px solid #ddd;border-radius:6px;padding:16px 20px;font-size:0.82rem;color:#555;line-height:1.7">
    Amazon Business Hosted Catalog integrates with <strong>SAP Ariba, Coupa, Oracle, Jaggaer, GEP, and other procurement platforms</strong>
    via punch-out catalogs and EDI integrations. Your employees access the catalog directly through the procurement tool
    your company already uses — no new software to learn.
    <br><br>
    The Universal Commerce Protocol (UCP) — co-developed by Amazon — is the open standard that makes
    these integrations seamless and agent-native. AI procurement agents can query the catalog, verify
    compliance, and place orders autonomously within your approved parameters.
</div>
""", unsafe_allow_html=True)


def page_browse(client, api_key):
    """Product browsing (left) + persistent AI chat panel (right)."""

    # ── Session state init ────────────────────────────────────────────────
    for key, default in [
        ("messages", []), ("catalog_ids", []), ("qty_map", {}),
        ("requirements", {}), ("ai_products", []), ("cart_ids", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    catalog_ids  = st.session_state.catalog_ids
    qty_map      = st.session_state.qty_map
    requirements = st.session_state.requirements

    # ── Left sidebar: filters ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔍 Filter Results")
        selected_cats = []
        for cat in ALL_CATEGORIES:
            if st.checkbox(cat, value=True, key=f"cat_{cat}"):
                selected_cats.append(cat)
        st.markdown("---")
        max_price  = st.slider("Max unit price ($)", 25, 1500, 1500, 25)
        avail_only = st.checkbox("Show In Stock only", value=False)
        st.markdown("---")

        # Cart summary
        cart_ids = st.session_state.cart_ids
        if cart_ids:
            st.markdown("### 🛒 Cart")
            cart_total = 0
            for pid in cart_ids:
                prod = CATALOG_BY_ID.get(pid)
                if not prod: continue
                qty = qty_map.get(pid, 1)
                line = prod["unit_price"] * qty
                cart_total += line
                short = prod["title"][:28] + "…" if len(prod["title"]) > 28 else prod["title"]
                st.markdown(f'<div class="cat-item"><div class="cat-item-name">{prod["img"]} {short}</div><div class="cat-item-price">${line:,.0f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cat-total"><span>Cart Total</span><span style="color:#B12704">${cart_total:,.0f}</span></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Proceed to Checkout →", use_container_width=True):
                st.success("Redirecting to Amazon Business checkout…")
            st.markdown("---")

        # Catalog summary
        if catalog_ids:
            st.markdown("### 🗂️ My Hosted Catalog")
            cat_total = 0; sourcing = 0
            for pid in catalog_ids:
                prod = CATALOG_BY_ID.get(pid)
                if not prod: continue
                qty = qty_map.get(pid, 1)
                line = prod["unit_price"] * qty
                cat_total += line
                if prod["availability"] == "sourcing": sourcing += 1
                short = prod["title"][:28] + "…" if len(prod["title"]) > 28 else prod["title"]
                st.markdown(f'<div class="cat-item"><div class="cat-item-name">{prod["img"]} {short}</div><div class="cat-item-price">${line:,.0f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cat-total"><span>Contract Value</span><span style="color:#B12704">${cat_total:,.0f}</span></div>', unsafe_allow_html=True)
            if sourcing:
                st.caption(f"⏳ {sourcing} item(s) need vendor negotiation")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Activate Catalog", use_container_width=True):
                st.success("Submitted to Amazon Business! Your vendor team will follow up within 24 hours.")
            if st.button("🗑️ Clear Catalog", use_container_width=True):
                st.session_state.catalog_ids = []; st.session_state.qty_map = {}; st.rerun()

    # ── Main layout: product grid (left) + AI chat (right) ───────────────
    col_products, col_chat = st.columns([3, 1], gap="medium")

    # ── Product grid ──────────────────────────────────────────────────────
    with col_products:
        filtered = [p for p in CATALOG
                    if p["category"] in selected_cats
                    and p["unit_price"] <= max_price
                    and (not avail_only or p["availability"] == "available")]

        ai_products = st.session_state.ai_products
        if ai_products:
            pinned   = [p for p in CATALOG if p["id"] in ai_products]
            rest     = [p for p in filtered if p["id"] not in ai_products]
            filtered = pinned + [p for p in rest if p not in pinned]

        headcount = requirements.get("headcount", 1) or 1
        ai_note   = ' &nbsp;·&nbsp; <span style="color:#E47911;font-weight:600">✨ AI picks shown first</span>' if ai_products else ""

        st.markdown(f"""
<div style="font-size:0.82rem;color:#555;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #ddd">
  1–{min(len(filtered),18)} of <strong>{len(filtered)}</strong> results{ai_note}
</div>""", unsafe_allow_html=True)

        cols_per_row = 2
        rows = [filtered[i:i+cols_per_row] for i in range(0, min(len(filtered), 18), cols_per_row)]

        for row in rows:
            pcols = st.columns(cols_per_row, gap="small")
            for pcol, prod in zip(pcols, row):
                with pcol:
                    pid        = prod["id"]
                    in_catalog = pid in catalog_ids
                    in_cart    = pid in st.session_state.cart_ids
                    qty        = qty_map.get(pid, headcount)

                    avail_html = '<div class="prod-avail-yes">✓ In Stock</div>' if prod["availability"] == "available" else '<div class="prod-avail-sourcing">⏳ Needs Sourcing</div>'
                    lead_html  = f'<div style="font-size:0.7rem;color:#666">Ships in {prod["lead_days"]} days</div>' if prod.get("lead_days") else '<div style="font-size:0.7rem;color:#B7791F">Contact vendor for availability</div>'

                    st.markdown(f"""
<div class="prod-card">
  <div class="prod-img-box">{prod['img']}</div>
  <div class="prod-title">{prod['title']}</div>
  <div class="prod-stars">{stars_html(prod['rating'])}</div>
  <div class="prod-reviews">{prod['reviews']:,} business ratings</div>
  <div style="margin:6px 0"><span class="prod-bizprice-label">Business Price</span></div>
  <div class="prod-price">${prod['unit_price']:,.2f} <span class="prod-per-unit">/ unit</span></div>
  <div style="font-size:0.72rem;color:#555;margin-bottom:4px">×{qty:,} = ${prod['unit_price']*qty:,.0f} total</div>
  {avail_html}{lead_html}
</div>""", unsafe_allow_html=True)

                    # Add to Cart (primary yellow button)
                    cart_label = "✓ In Cart" if in_cart else "🛒 Add to Cart"
                    if st.button(cart_label, key=f"cart_{pid}", use_container_width=True):
                        if in_cart:
                            st.session_state.cart_ids.remove(pid)
                        else:
                            st.session_state.cart_ids.append(pid)
                            st.session_state.qty_map[pid] = qty
                        st.rerun()

                    # Add to Catalog (secondary orange button)
                    if in_catalog:
                        st.markdown('<div class="in-catalog-btn">', unsafe_allow_html=True)
                        if st.button("✓ In Catalog", key=f"rem_{pid}", use_container_width=True):
                            st.session_state.catalog_ids.remove(pid)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="catalog-btn">', unsafe_allow_html=True)
                        if st.button("＋ Add to Catalog", key=f"add_{pid}", use_container_width=True):
                            st.session_state.catalog_ids.append(pid)
                            st.session_state.qty_map[pid] = qty
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Chat panel (persistent right column) ───────────────────────────
    with col_chat:
        st.markdown("""
<div style="background:#232F3E;color:#fff;padding:12px 14px;border-radius:10px 10px 0 0;margin-bottom:0">
  <div style="font-size:0.88rem;font-weight:700">💬 AI Catalog Assistant</div>
  <div style="font-size:0.72rem;color:#aaa;margin-top:2px">Powered by Claude Opus 4.8</div>
</div>
<div style="background:#fff;border:1px solid #ddd;border-top:none;border-radius:0 0 10px 10px;padding:12px;min-height:200px">
""", unsafe_allow_html=True)

        if not api_key:
            st.markdown("""
<div style="font-size:0.78rem;color:#555;text-align:center;padding:20px 8px">
  Add your Anthropic API key in the sidebar to activate the AI assistant.
</div>""", unsafe_allow_html=True)
        else:
            # Chat messages
            if not st.session_state.messages:
                st.markdown("""
<div style="font-size:0.78rem;color:#555;line-height:1.5;margin-bottom:8px">
  Tell me what your company needs, or pick a scenario to get started:
</div>""", unsafe_allow_html=True)
                for i, (label, template) in enumerate(QUICK_TEMPLATES.items()):
                    st.markdown('<div class="catalog-btn">', unsafe_allow_html=True)
                    clicked = st.button(label, key=f"qp_{i}", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    if clicked:
                        # Clear the widget so the new value takes effect
                        st.session_state.pop("chat_msg", None)
                        st.session_state["chat_prefill"] = template
                        st.rerun()
            else:
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="margin-bottom:6px"><div class="msg-agent-name">🤖 Amazon Business AI</div><div class="msg-agent">{msg["content"]}</div></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if api_key:
            st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
            prefill = st.session_state.pop("chat_prefill", None)
            if prefill is not None:
                st.session_state["chat_msg"] = prefill
            user_msg = st.text_area("", height=160,
                                    placeholder="e.g. desks + chairs for 500 employees, $400/person, standard shipping",
                                    label_visibility="collapsed", key="chat_msg")
            st.markdown('<div class="chat-send-btn">', unsafe_allow_html=True)
            send = st.button("Send ➤", key="send_chat", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.messages:
                if st.button("Clear chat", key="clear_chat", use_container_width=True):
                    st.session_state.messages    = []
                    st.session_state.ai_products = []
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            if send and user_msg.strip():
                with st.spinner("Searching catalog…"):
                    result = call_agent(
                        client,
                        st.session_state.messages,
                        user_msg.strip(),
                        catalog_ids,
                        requirements,
                    )

                st.session_state.messages.append({"role": "user",     "content": user_msg.strip()})
                st.session_state.messages.append({"role": "assistant", "content": result.get("message", "Let me find that.")})

                if result.get("product_ids"):
                    st.session_state.ai_products = result["product_ids"]

                for pid in result.get("catalog_add", []):
                    if pid not in st.session_state.catalog_ids:
                        st.session_state.catalog_ids.append(pid)
                        hc = (result.get("req_update") or {}).get("headcount") or requirements.get("headcount", 1) or 1
                        st.session_state.qty_map[pid] = hc

                for pid in result.get("catalog_remove", []):
                    if pid in st.session_state.catalog_ids:
                        st.session_state.catalog_ids.remove(pid)

                for k, v in (result.get("req_update") or {}).items():
                    if v is not None:
                        st.session_state.requirements[k] = v

                hc = st.session_state.requirements.get("headcount", 1) or 1
                for pid in st.session_state.catalog_ids:
                    if pid not in st.session_state.qty_map:
                        st.session_state.qty_map[pid] = hc

                st.rerun()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Amazon Business — Hosted Catalog AI",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    # Header
    st.markdown("""
<div class="amzb-header">
  <div>
    <span class="amzb-logo">amazon<span class="amzb-logo-orange">business</span></span>
    <span class="amzb-logo-biz">HOSTED CATALOG AI</span>
  </div>
  <div class="amzb-tagline">Build your company's approved purchasing catalog — powered by AI</div>
</div>
<div class="amzb-nav">
  <a href="#">Solutions</a>
  <a href="#">Supplies</a>
  <a href="#">Delivery</a>
  <a href="#">Industries</a>
  <a href="#">Prime Business</a>
  <a href="#" style="color:#E47911;font-weight:700">✨ Catalog AI</a>
</div>
""", unsafe_allow_html=True)

    # API key in sidebar
    with st.sidebar:
        api_key = st.text_input("Anthropic API Key", type="password",
                                help="Required for AI assistant. sk-ant-…",
                                key="api_key_input")
        if not api_key:
            st.caption("👆 Add API key to activate the AI assistant.")

    client = anthropic.Anthropic(api_key=api_key) if api_key else None

    tab1, tab2 = st.tabs(["📖  What is Hosted Catalog?", "🛒  Browse & Build Catalog"])

    with tab1:
        page_overview()

    with tab2:
        page_browse(client, api_key)


if __name__ == "__main__":
    main()
