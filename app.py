import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import base64

# ── Page Config ──
st.set_page_config(page_title="IFRS Accounting Copilot", page_icon="📘", layout="wide")

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #002060 0%, #0050A0 100%);
    padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;
}
.main-header h1 { color: white !important; font-size: 1.8rem !important; font-weight: 700 !important; margin-bottom: 0.3rem !important; }
.main-header p { color: #B0C4DE !important; font-size: 0.95rem !important; margin: 0 !important; }

.section-card {
    background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
    padding: 1.2rem; margin-bottom: 0.4rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.section-title {
    font-size: 1rem; font-weight: 700; color: #002060; margin-bottom: 0.6rem;
    display: flex; align-items: center; gap: 0.5rem;
}

/* Reduce gaps between Streamlit columns/blocks */
.stColumns { gap: 0.3rem !important; }
div[data-testid="stVerticalBlock"] > div { margin-bottom: 0 !important; padding-bottom: 0 !important; }
div[data-testid="stVerticalBlock"] > div:has(> div.stMarkdown) { margin-bottom: 0 !important; }

/* Kill all empty Streamlit spacer divs */
.element-container:empty { display: none !important; }
div[data-testid="stVerticalBlock"] > div:empty { display: none !important; margin: 0 !important; padding: 0 !important; min-height: 0 !important; }

/* Reduce Streamlit's default block spacing */
.block-container { padding-top: 1rem !important; }
div[data-testid="stExpander"] { margin-bottom: 0.3rem !important; }

/* Thin blue divider between sections */
.blue-divider {
    border: none; border-top: 2px solid #002060; margin: 0.5rem 0; opacity: 0.3;
}

/* Sidebar example buttons - slightly smaller font */
section[data-testid="stSidebar"] button {
    font-size: 0.82rem !important;
    padding: 0.4rem 0.6rem !important;
    line-height: 1.3 !important;
}
.ifrs-tag {
    background: #002060; color: white; padding: 0.4rem 1rem; border-radius: 6px;
    font-weight: 600; font-size: 1.1rem; display: inline-block; margin-bottom: 0.5rem;
}
.journal-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.journal-table th {
    background: #002060; color: white; padding: 0.6rem 1rem; text-align: left;
    font-size: 0.85rem; font-weight: 600;
}
.journal-table td { padding: 0.5rem 1rem; border-bottom: 1px solid #E8E8E8; font-size: 0.85rem; color: #333; }
.journal-table tr:nth-child(even) { background: #F8FAFC; }

.disclosure-item {
    background: #F0F7FF; border-left: 3px solid #002060; padding: 0.6rem 1rem;
    margin-bottom: 0.5rem; border-radius: 0 6px 6px 0; font-size: 0.9rem; color: #333;
}
.memo-section {
    background: #FAFBFC; border-left: 4px solid #002060; padding: 1rem 1.2rem;
    margin-bottom: 0.8rem; border-radius: 0 8px 8px 0;
}
.memo-label { font-weight: 700; color: #002060; font-size: 0.9rem; margin-bottom: 0.3rem; }

.compare-col {
    background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
    padding: 1.2rem; height: 100%;
}
.compare-header-a {
    background: #002060; color: white; padding: 0.5rem 1rem; border-radius: 6px;
    font-weight: 600; text-align: center; margin-bottom: 1rem;
}
.compare-header-b {
    background: #0050A0; color: white; padding: 0.5rem 1rem; border-radius: 6px;
    font-weight: 600; text-align: center; margin-bottom: 1rem;
}

.impact-positive { color: #2E7D32; font-weight: 600; }
.impact-negative { color: #C62828; font-weight: 600; }
.impact-neutral { color: #F57F17; font-weight: 600; }

.caveat-box {
    background: #FFF8E1; border: 1px solid #FFD54F; border-radius: 8px;
    padding: 1rem 1.2rem; margin-top: 1.5rem; font-size: 0.82rem; color: #5D4037;
}
.ref-box {
    background: #F3E5F5; border: 1px solid #CE93D8; border-radius: 8px;
    padding: 0.8rem 1rem; margin-top: 0.5rem; font-size: 0.8rem; color: #4A148C;
}
.context-bar {
    background: #F0F4F8; border: 1px solid #D0D8E0; border-radius: 8px;
    padding: 0.6rem 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #555;
}
.powered-by {
    text-align: center; color: #999; font-size: 0.75rem; margin-top: 2rem;
    padding-top: 1rem; border-top: 1px solid #EEE;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

.copy-btn {
    background: #E8F0FE; color: #002060; border: 1px solid #C2D7F0; border-radius: 4px;
    padding: 0.2rem 0.6rem; font-size: 0.75rem; cursor: pointer; font-weight: 600;
    margin-left: 0.5rem;
}
.copy-btn:hover { background: #D0E2FF; }

.history-item {
    background: #F8FAFC; border: 1px solid #E0E0E0; border-radius: 6px;
    padding: 0.5rem 0.8rem; margin-bottom: 0.4rem; font-size: 0.8rem; color: #333;
    cursor: pointer;
}
.history-item:hover { background: #E8F0FE; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ──
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = ""
if "last_mode" not in st.session_state:
    st.session_state.last_mode = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "pw_hash" not in st.session_state:
    st.session_state.pw_hash = ""

MAX_FREE_ANALYSES = 5  # Free tier limit

# ── Persistent usage tracking via file storage ──
import hashlib, os, json as json_lib

USAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".usage_data")
os.makedirs(USAGE_DIR, exist_ok=True)

def get_usage_file(password_hash):
    return os.path.join(USAGE_DIR, f"{password_hash}.json")

def load_usage(password_hash):
    fpath = get_usage_file(password_hash)
    if os.path.exists(fpath):
        try:
            with open(fpath, 'r') as f:
                data = json_lib.load(f)
                return data.get("count", 0)
        except:
            return 0
    return 0

def save_usage(password_hash, count):
    fpath = get_usage_file(password_hash)
    with open(fpath, 'w') as f:
        json_lib.dump({"count": count}, f)

# ── Password Gate ──
if not st.session_state.authenticated:
    st.markdown("""
    <div class="main-header">
        <h1>📘 IFRS Accounting Copilot</h1>
        <p>AI-powered IFRS treatment analysis, audit memos, and scenario comparison.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Access Required")
    st.markdown("This tool is part of the **Exploring AI in Finance** series by Akshita Gagrani.")
    
    pw_col1, pw_col2 = st.columns([2, 3])
    with pw_col1:
        password = st.text_input("Enter access code:", type="password", placeholder="Enter free or premium code")
        if st.button("🔓 Access Tool", type="primary", use_container_width=True):
            free_password = st.secrets.get("APP_PASSWORD", "ifrs2025")
            premium_password = st.secrets.get("PREMIUM_PASSWORD", "ifrspro2025")
            if password == premium_password:
                st.session_state.authenticated = True
                st.session_state.is_premium = True
                st.session_state.pw_hash = hashlib.md5(password.encode()).hexdigest()
                st.rerun()
            elif password == free_password:
                st.session_state.authenticated = True
                st.session_state.is_premium = False
                st.session_state.pw_hash = hashlib.md5(password.encode()).hexdigest()
                # Load persisted usage count
                st.session_state.usage_count = load_usage(st.session_state.pw_hash)
                st.rerun()
            else:
                st.error("Incorrect code. DM Akshita on LinkedIn for access.")
        
        st.markdown("""
        <div style="margin-top:1.5rem; color:#888; font-size:0.85rem;">
            Don't have a code? <a href="https://www.linkedin.com/in/akshita-gagrani-02457091" target="_blank">DM Akshita on LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)
    
    with pw_col2:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E0E0E0; border-radius:10px; padding:1rem 1.2rem; margin-top:0.5rem;">
            <div style="font-weight:700; color:#002060; font-size:0.95rem; margin-bottom:0.5rem;">What you get:</div>
            <div style="font-size:0.82rem; color:#555; line-height:1.6;">
                ✅ IFRS treatment with paragraph references<br>
                ✅ Journal entries & disclosure drafts<br>
                ✅ Audit-ready technical memos<br>
                ✅ Side-by-side treatment comparison<br>
                ✅ Upload contracts (PDF) for auto-analysis<br>
                ✅ 19 jurisdictions • 10 languages
            </div>
            <div style="margin-top:0.8rem; font-size:0.78rem; color:#888;">
                🆓 Free: 5 analyses + unlimited follow-ups &nbsp;|&nbsp; 💎 Premium: unlimited — DM for details
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# Show tier badge after login
if st.session_state.is_premium:
    st.markdown('<div style="background:#E8F5E9;border:1px solid #4CAF50;border-radius:6px;padding:0.4rem 1rem;font-size:0.82rem;color:#2E7D32;margin-bottom:0.5rem;">💎 <strong>Premium Access</strong> — Unlimited analyses</div>', unsafe_allow_html=True)


# ── Copy to Clipboard JS ──
st.markdown("""
<script>
function copyToClipboard(elementId, btnId) {
    var text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text).then(function() {
        var btn = document.getElementById(btnId);
        btn.innerText = 'Copied ✓';
        setTimeout(function() { btn.innerText = '📋 Copy'; }, 2000);
    });
}
</script>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="main-header">
    <h1>📘 IFRS Accounting Copilot</h1>
    <p>Describe a transaction in plain English — get IFRS treatment, journal entries, disclosure drafts, and audit-ready memos in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Gemini Setup ──
def get_model():
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        st.error("⚠️ Google API key not configured. Add GOOGLE_API_KEY to Streamlit secrets.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.5-flash')

# ── Context Panel ──
with st.expander("⚙️ **Set Your Context** (industry, geography, entity type, language) — improves accuracy", expanded=False):
    ctx_c1, ctx_c2, ctx_c3, ctx_c4 = st.columns(4)
    with ctx_c1:
        industry = st.selectbox("Industry", [
            "General / Not specified", "Banking & Financial Services", "Insurance",
            "Real Estate & Construction", "Technology / SaaS", "Telecom",
            "Manufacturing", "Retail & Consumer", "Oil & Gas / Energy",
            "Healthcare & Pharma", "Transport & Logistics", "Government / Public Sector",
            "Professional Services", "Hospitality", "Education", "Other"
        ])
    with ctx_c2:
        geography = st.selectbox("Jurisdiction", [
            "IFRS (Global / No specific jurisdiction)",
            "UAE",
            "Saudi Arabia (KSA)",
            "GCC — Bahrain, Kuwait, Oman, Qatar",
            "European Union",
            "United Kingdom (UK-adopted IFRS)",
            "India (Ind AS)",
            "Australia (AASB)",
            "Singapore (SFRS)",
            "Hong Kong (HKFRS)",
            "South Africa (JSE)",
            "Canada (IFRS / ASPE)",
            "Nigeria (FRCN)",
            "Kenya / East Africa",
            "Egypt",
            "United States (US GAAP)",
            "China (CAS)",
            "Japan (J-GAAP / IFRS optional)",
            "Other"
        ])
    with ctx_c3:
        entity_type = st.selectbox("Entity Type", [
            "Listed / Public Company", "Private Company (Full IFRS)",
            "SME (IFRS for SMEs)", "Government Entity (IPSAS)",
            "Not-for-Profit", "Other"
        ])
    with ctx_c4:
        currency = st.text_input("Functional Currency", value="USD", max_chars=5)

    ctx_c5, ctx_c6 = st.columns(2)
    with ctx_c5:
        reporting_period = st.text_input("Reporting Period (optional)", placeholder="e.g., FY ending 31 Dec 2025", max_chars=50)
    with ctx_c6:
        output_language = st.selectbox("Output Language", [
            "English", "Arabic (العربية)", "French (Français)", "Spanish (Español)",
            "Portuguese (Português)", "Hindi (हिन्दी)", "Chinese (中文)",
            "Bahasa Indonesia", "Turkish (Türkçe)", "German (Deutsch)"
        ])

def get_context_string():
    parts = []
    if industry != "General / Not specified":
        parts.append(f"Industry: {industry}")
    if geography != "IFRS (Global / No specific jurisdiction)":
        parts.append(f"Jurisdiction: {geography}")
    if entity_type != "Listed / Public Company":
        parts.append(f"Entity: {entity_type}")
    if currency != "USD":
        parts.append(f"Currency: {currency}")
    if reporting_period:
        parts.append(f"Period: {reporting_period}")
    if output_language != "English":
        parts.append(f"Language: {output_language}")
    return " | ".join(parts) if parts else ""

ctx_str = get_context_string()
if ctx_str:
    st.markdown(f'<div class="context-bar">📎 <strong>Context applied:</strong> {ctx_str}</div>', unsafe_allow_html=True)

# Jurisdiction-specific warnings
if "United States" in geography:
    st.markdown("""
    <div style="background:#FFF3E0;border:1px solid #FF9800;border-radius:8px;padding:1rem;margin-bottom:1rem;font-size:0.88rem;color:#E65100;">
        <strong>⚠️ US GAAP Jurisdiction Selected:</strong> This tool is built for IFRS. The US follows US GAAP (ASC Codification), 
        a fundamentally different framework. Analysis below follows IFRS but will flag key US GAAP differences where material. 
        For definitive US GAAP treatment, consult the ASC Codification directly.
    </div>
    """, unsafe_allow_html=True)
elif "China" in geography:
    st.markdown("""
    <div style="background:#FFF3E0;border:1px solid #FF9800;border-radius:8px;padding:1rem;margin-bottom:1rem;font-size:0.88rem;color:#E65100;">
        <strong>⚠️ China (CAS) Selected:</strong> This tool is built for IFRS. Chinese Accounting Standards are substantially converged 
        with IFRS but have practical differences. Analysis below follows IFRS with CAS differences flagged where known.
    </div>
    """, unsafe_allow_html=True)
elif "Japan" in geography:
    st.markdown("""
    <div style="background:#FFF3E0;border:1px solid #FF9800;border-radius:8px;padding:1rem;margin-bottom:1rem;font-size:0.88rem;color:#E65100;">
        <strong>⚠️ Japan Selected:</strong> Most Japanese entities follow J-GAAP, not IFRS. If your entity uses IFRS (voluntary adoption), 
        the analysis below applies. If J-GAAP applies, treatment may differ significantly — particularly for goodwill, OCI recycling, and revenue.
    </div>
    """, unsafe_allow_html=True)

# ── Context for prompts ──
def build_context_block():
    block = f"""
Entity Context:
- Industry: {industry}
- Jurisdiction: {geography}
- Entity Type: {entity_type}
- Functional Currency: {currency}
- Reporting Period: {reporting_period if reporting_period else 'Not specified'}
"""
    # ── Jurisdiction-specific notes ──
    if geography == "UAE":
        block += ("- Note: UAE follows full IFRS as adopted. Consider RERA regulations for real estate. "
                  "Corporate Tax Law effective June 2023 (9% above AED 375K) — consider IAS 12 implications including deferred tax. "
                  "Free zone entities may have 0% rate — assess qualifying income rules. "
                  "ADGM/DIFC entities may have additional regulatory reporting requirements.\n")
    elif geography == "Saudi Arabia (KSA)":
        block += ("- Note: KSA follows full IFRS. Zakat is applicable to Saudi/GCC-owned entities (not income tax) — "
                  "account for Zakat under IAS 12 or as a levy under IFRIC 21 depending on entity's policy. "
                  "SOCPA may issue interpretations that differ from IASB. Consider Vision 2030 implications for government contracts.\n")
    elif "GCC" in geography:
        block += ("- Note: GCC countries (Bahrain, Kuwait, Oman, Qatar) follow full IFRS. "
                  "Central bank reporting requirements may impose additional disclosure for banking/insurance entities. "
                  "Kuwait has specific CMA requirements for listed entities. Oman has additional SOCPA-equivalent guidance via OAAA. "
                  "Qatar QFC entities may have additional regulatory overlays.\n")
    elif geography == "European Union":
        block += ("- Note: EU follows IFRS as endorsed by EFRAG. Known carve-outs include IAS 39 macro hedge accounting "
                  "(portfolio fair value hedge for interest rate risk not available under IFRS 9 as endorsed). "
                  "CSRD/ESRS sustainability reporting may interact with IFRS disclosures. "
                  "EU Taxonomy alignment may affect asset classification and disclosure.\n")
    elif "United Kingdom" in geography:
        block += ("- Note: UK follows UK-adopted IFRS post-Brexit, endorsed by UK Endorsement Board (UKEB). "
                  "Currently identical to IASB IFRS for most standards, but future divergence possible. "
                  "FRS 101 (reduced disclosure) available for qualifying subsidiaries. "
                  "FRS 102 applies to entities not using full IFRS. FCA/PRA may impose additional requirements for regulated entities.\n")
    elif "India" in geography:
        block += ("- Note: India follows Ind AS (converged with IFRS but with significant carve-outs). "
                  "Key differences: Ind AS 115 — no concept of variable consideration constraint identical to IFRS 15; "
                  "Ind AS 116 — largely aligned but SEBI has additional lease disclosure requirements; "
                  "Ind AS 109 — differs on fair value through OCI for equity instruments; "
                  "Ind AS 103 — common control transactions under Appendix C (pooling of interest allowed). "
                  "RBI guidelines override Ind AS for banking entities on specific items (e.g., NPA provisioning). "
                  "Flag any Ind AS-specific deviations from IFRS clearly.\n")
    elif "Australia" in geography:
        block += ("- Note: Australia follows AASB standards — largely IFRS-identical with 'Aus' paragraphs for additional guidance. "
                  "Reduced disclosure regime available under AASB 1060 for non-publicly accountable entities. "
                  "ASIC may issue regulatory guidance that affects application. "
                  "Not-for-profit entities follow modified AASB standards (AASB 1058 for income, AASB 15/16 with modifications).\n")
    elif "Singapore" in geography:
        block += ("- Note: Singapore follows SFRS(I) — fully converged with IFRS. "
                  "ACRA filing requirements may differ from IFRS disclosure. "
                  "SGX listing rules impose additional disclosure for listed entities. "
                  "SFRS for Small Entities available for qualifying private companies.\n")
    elif "Hong Kong" in geography:
        block += ("- Note: Hong Kong follows HKFRS — fully converged with IFRS, issued by HKICPA. "
                  "HKEX listing rules require additional disclosures beyond HKFRS requirements. "
                  "SFC may impose additional requirements for regulated entities. "
                  "Hong Kong Financial Reporting Standard for Private Entities available for qualifying entities.\n")
    elif "South Africa" in geography:
        block += ("- Note: South Africa follows full IFRS for listed entities (JSE requirement). "
                  "IFRS for SMEs available for non-listed entities. "
                  "B-BBEE (Broad-Based Black Economic Empowerment) reporting may interact with financial disclosures. "
                  "SARB requirements overlay for banking entities. King IV governance code may affect disclosure.\n")
    elif "Canada" in geography:
        block += ("- Note: Canada — publicly accountable entities must use IFRS (as issued by IASB, adopted by AcSB). "
                  "Private enterprises may use ASPE (Accounting Standards for Private Enterprises) — a separate framework, not IFRS. "
                  "If ASPE applies, flag that IFRS treatment provided may not be applicable. "
                  "Not-for-profit entities follow ASNPO. Rate-regulated entities have specific guidance under IFRS 14/IAS-equivalent.\n")
    elif "Nigeria" in geography:
        block += ("- Note: Nigeria follows full IFRS for public interest entities (FRCN requirement since 2012). "
                  "SMEs may use IFRS for SMEs. CBN (Central Bank of Nigeria) guidelines override IFRS for banks on specific items "
                  "(e.g., prudential provisioning vs IFRS 9 ECL). "
                  "FRCN may issue local interpretations. SEC Nigeria has additional disclosure requirements for listed entities.\n")
    elif "Kenya" in geography:
        block += ("- Note: Kenya / East Africa follows full IFRS (adopted by ICPAK). "
                  "Capital Markets Authority (CMA) Kenya imposes additional disclosure requirements for listed entities. "
                  "IFRS for SMEs widely used for non-public entities. "
                  "Similar adoption across East African Community (Uganda, Tanzania, Rwanda) but local regulatory overlays may differ.\n")
    elif "Egypt" in geography:
        block += ("- Note: Egypt adopted full IFRS effective 2023 for listed entities (replacing Egyptian Accounting Standards). "
                  "Legacy EAS practices may still influence application in transition period. "
                  "FRA (Financial Regulatory Authority) requirements apply for non-banking financial institutions. "
                  "CBE guidelines overlay for banking entities.\n")
    elif "United States" in geography:
        block += ("- IMPORTANT: This tool is built for IFRS. The United States follows US GAAP (ASC Codification), "
                  "which is a fundamentally different framework. The analysis below follows IFRS but will flag key "
                  "US GAAP differences where material. Key divergence areas include: "
                  "lease accounting (ASC 842 vs IFRS 16 — operating lease on-balance-sheet treatment differs), "
                  "revenue recognition (ASC 606 vs IFRS 15 — largely converged but differences in licensing and variable consideration), "
                  "inventory (LIFO permitted under US GAAP, prohibited under IFRS), "
                  "development costs (expensed under US GAAP except software, capitalised under IAS 38), "
                  "impairment (one-step under IFRS/IAS 36, two-step under ASC 360). "
                  "For definitive US GAAP treatment, consult the ASC Codification directly.\n")
    elif "China" in geography:
        block += ("- Note: China follows Chinese Accounting Standards (CAS) — substantially converged with IFRS since 2006 "
                  "but with practical differences in application. Key differences: fair value measurement less prevalent in practice, "
                  "government grants treatment differs from IAS 20 in some cases, related party disclosures may follow "
                  "Chinese regulatory definitions. MOF (Ministry of Finance) issues interpretations. "
                  "Hong Kong-listed Chinese companies ('H-shares') must reconcile CAS to HKFRS.\n")
    elif "Japan" in geography:
        block += ("- Note: Japan — IFRS is optional for listed entities (voluntary adoption since 2010, ~250+ companies use it). "
                  "Most entities follow J-GAAP (ASBJ standards), which differs significantly from IFRS in areas like "
                  "goodwill (amortised under J-GAAP, not under IFRS), recycling of OCI items, and revenue recognition. "
                  "Modified International Standards (JMIS) also available as an intermediate option. "
                  "If J-GAAP applies, flag that IFRS treatment may not be applicable.\n")

    # ── Entity type notes ──
    if entity_type == "SME (IFRS for SMEs)":
        block += ("- Note: Apply IFRS for SMEs (revised 2015 / 2024 amendments). Simplified recognition and measurement. "
                  "Key simplifications: no OCI recycling, simplified financial instruments (Section 11/12), "
                  "goodwill amortised, simplified lease accounting. Flag where full IFRS treatment would materially differ.\n")
    elif entity_type == "Government Entity (IPSAS)":
        block += ("- Note: Government entities may follow IPSAS (International Public Sector Accounting Standards), not IFRS. "
                  "IPSAS is converging with IFRS but differences exist in revenue (IPSAS 23/47), provisions, and non-exchange transactions. "
                  "Analysis below follows IFRS — flag where IPSAS treatment would differ.\n")

    # ── Industry-specific notes ──
    if "Banking" in industry or "Insurance" in industry:
        block += ("- Note: Apply industry-specific standards — IFRS 9 (ECL provisioning, classification), IFRS 17 (insurance contracts), "
                  "IFRS 7 (financial instrument disclosures). Consider Basel III/IV regulatory capital implications. "
                  "Central bank prudential requirements may override IFRS on specific items.\n")
    elif "Real Estate" in industry:
        block += ("- Note: Consider IFRS 15 (revenue — over time vs point in time for property development), "
                  "IFRS 16 (leases — lessor and lessee), IAS 40 (investment property — cost vs fair value model choice), "
                  "IAS 23 (borrowing costs capitalisation for qualifying assets).\n")
    elif "SaaS" in industry or "Technology" in industry:
        block += ("- Note: Key focus areas — IFRS 15 (multi-element arrangements, SaaS vs license distinction, "
                  "principal vs agent), IAS 38 (capitalisation of development costs — criteria in IAS 38.57), "
                  "IFRS 16 (data center/server leases), IFRS 2 (share-based payments common in tech).\n")
    elif "Oil & Gas" in industry:
        block += ("- Note: Consider IFRS 6 (exploration and evaluation), IAS 16/IAS 38 (development assets), "
                  "IAS 37 (decommissioning provisions), IFRS 16 (rig/equipment leases), "
                  "IAS 36 (impairment — commodity price sensitivity). Joint arrangements under IFRS 11 are common.\n")
    elif "Healthcare" in industry:
        block += ("- Note: Consider IFRS 15 (revenue — bundled services, variable consideration for insurance reimbursements), "
                  "IAS 38 (R&D capitalisation for pharma — Phase III criteria), IAS 37 (litigation/regulatory provisions), "
                  "IFRS 2 (share-based payments for biotech).\n")
    elif "Manufacturing" in industry:
        block += ("- Note: Consider IAS 2 (inventory — costing methods, NRV assessment), IAS 16 (PP&E — component accounting, "
                  "useful life assessment), IAS 36 (impairment of production assets), IAS 37 (warranty provisions), "
                  "IFRS 15 (bill-and-hold, consignment arrangements).\n")
    elif "Telecom" in industry:
        block += ("- Note: Consider IFRS 15 (multi-element arrangements — handset + service, contract modifications, "
                  "significant financing component), IFRS 16 (tower leases, IRU arrangements), "
                  "IAS 38 (spectrum license capitalisation), IFRIC 12 (service concession arrangements).\n")
    elif "Retail" in industry:
        block += ("- Note: Consider IFRS 15 (loyalty programmes, gift cards, returns — refund liabilities), "
                  "IFRS 16 (store leases — major balance sheet item), IAS 2 (inventory valuation, shrinkage), "
                  "IAS 36 (store-level impairment).\n")
    elif "Transport" in industry:
        block += ("- Note: Consider IFRS 16 (fleet/aircraft/vessel leases — major impact), IFRS 15 (freight revenue — "
                  "over time, bill of lading), IAS 37 (maintenance provisions for aircraft/vessels), "
                  "IAS 16 (component accounting for major assets), IAS 36 (route-level impairment).\n")
    elif "Hospitality" in industry:
        block += ("- Note: Consider IFRS 15 (loyalty programmes, package deals, management fees), "
                  "IFRS 16 (hotel/property leases), IAS 40 (owned hotel properties — PP&E vs investment property classification), "
                  "IAS 36 (property-level impairment), IAS 37 (onerous contract provisions).\n")

    # ── Language and currency instructions ──
    lang_name = output_language.split(" (")[0] if " (" in output_language else output_language
    if lang_name != "English":
        block += f"- LANGUAGE INSTRUCTION: Respond entirely in {lang_name}. All section headings, explanations, and narrative must be in {lang_name}. Keep IFRS standard names and account names in English for technical accuracy.\n"
    
    block += f"- CURRENCY INSTRUCTION: Use {currency} as the currency symbol in all illustrative journal entries and amounts. Do not default to $ or USD unless {currency} is USD.\n"

    return block

# ── System Prompts ──
BASE_RULES = """
CRITICAL RULES FOR IFRS REFERENCES:
- Only cite specific IFRS paragraph numbers (e.g., IFRS 16.22) when you are highly confident they are correct
- When uncertain about a specific paragraph number, reference the standard and section generally (e.g., "IFRS 16, Recognition section")
- Prefer referencing well-known paragraphs that are unlikely to have changed (e.g., IFRS 15.9 for the 5-step model)
- Base all guidance on IFRS standards as issued by the IASB
- If the jurisdiction has known carve-outs or local modifications, flag them explicitly
- If the transaction is ambiguous and could fall under multiple standards, present both paths with decision criteria
- Always flag areas requiring significant professional judgment
CRITICAL RULES FOR AMOUNTS IN JOURNAL ENTRIES:
- If the user provides specific amounts in their transaction description, use those EXACT amounts in journal entries and calculations
- If the user does NOT provide amounts, use "XXX" as placeholder in ALL journal entries (e.g., "Dr Right-of-Use Asset XXX / Cr Lease Liability XXX")
- NEVER invent or assume illustrative amounts. Either use the user's actual numbers or use XXX
- Use the entity's functional currency symbol alongside amounts (e.g., "AED XXX" or "USD 500,000")

CRITICAL RULES FOR CONCISENESS:
- Be CONCISE. Every field value must be short, sharp bullet points — NOT paragraphs or essays
- Max 1-2 sentences per bullet point. No bullet should exceed 25 words
- Lead with the conclusion or action, not the background
- Strip all filler words: "it should be noted that", "in accordance with", "it is important to consider"
- For journal entries: only show the most critical entries (initial recognition + one subsequent period). Do NOT show every monthly entry
- For key_paragraphs: max 4-5 references, not exhaustive lists
- For conditions/notes/errors: max 3-4 bullets each, prioritized by materiality
- Put anything secondary or edge-case into practical_notes or common_errors — keep main sections tight
- Think: "What would a senior accountant need to see in 30 seconds?"
"""

PROMPT_QUICK = """You are an expert IFRS technical accounting advisor with 20+ years at a Big 4 firm.
Analyze the transaction and provide a complete IFRS treatment.

""" + BASE_RULES + """

Respond ONLY in this JSON format. No markdown, no backticks, no preamble:
{
    "applicable_standard": {
        "primary": "IFRS XX - Standard Name",
        "secondary": ["Other relevant standard — one line reason (max 2 items)"],
        "why": "One sentence: why this standard applies",
        "key_paragraphs": ["Max 4-5 key references, e.g., IFRS 16.22 — brief label"]
    },
    "recognition": {
        "criteria": "One sentence: when to recognize",
        "timing": "One sentence: specific trigger point",
        "conditions": ["Max 3 bullet points, each under 20 words"],
        "industry_considerations": "One sentence or null"
    },
    "measurement": {
        "initial": "2-3 bullet points: how to measure at day one",
        "subsequent": "1-2 bullet points: ongoing measurement",
        "method": "One line: measurement method",
        "rates_assumptions": "Key inputs needed (e.g., IBR, useful life) — one line"
    },
    "journal_entries": [
        {
            "timing": "When posted (e.g., At inception, Monthly)",
            "description": "One line: what this records",
            "entries": [
                {"account": "Account Name", "debit": "Amount", "credit": ""},
                {"account": "Account Name", "debit": "", "credit": "Amount"}
            ]
        }
    ],
    "disclosure_draft": {
        "accounting_policy": "2-3 sentences max, audit-ready wording",
        "note_disclosures": ["Max 4 items: specific disclosure requirements, one line each"],
        "quantitative_disclosures": ["Max 3 items: tables/schedules required"]
    },
    "practical_notes": ["Max 3 items: most important practical points, one sentence each"],
    "key_judgments": ["Max 3 items: judgment areas with brief explanation"],
    "jurisdiction_notes": "One sentence or null",
    "complexity_rating": "Low / Medium / High",
    "common_errors": ["Max 3 items: most frequent mistakes, one sentence each"]
}"""

PROMPT_MEMO = """You are a Big 4 technical accounting director writing a formal accounting position memo.
Write a structured technical memo that could be shared with external auditors.

""" + BASE_RULES + """

Respond ONLY in this JSON format. No markdown, no backticks, no preamble:
{
    "memo_title": "Technical Accounting Memo: [Topic]",
    "prepared_by": "IFRS Accounting Copilot (AI-generated — requires review)",
    "date": "Current date",
    "issue": {
        "summary": "2-3 sentences max: the accounting issue",
        "background": "2-3 sentences: transaction facts only",
        "question": "One sentence: the specific question"
    },
    "relevant_guidance": {
        "primary_standard": "IFRS XX - Name",
        "key_paragraphs": ["Max 4 items: paragraph + one-line description of what it says"],
        "interpretations": ["Max 2 items: relevant IFRIC/agenda decisions or empty list"],
        "industry_guidance": "One sentence or null"
    },
    "analysis": {
        "approach": "One sentence: methodology",
        "application": "3-5 bullet points: step-by-step application to these facts",
        "key_judgments": [
            {
                "judgment": "One sentence: the judgment area",
                "our_position": "One sentence: conclusion and why",
                "sensitivity": "One sentence: what changes if different"
            }
        ]
    },
    "conclusion": {
        "recommended_treatment": "2-3 sentences: clear recommendation",
        "journal_entries": [
            {
                "description": "One line",
                "entries": [
                    {"account": "Account", "debit": "Amount", "credit": ""}
                ]
            }
        ],
        "disclosure_impact": "One sentence"
    },
    "alternative_views": [
        {
            "alternative": "One sentence: the alternative",
            "why_rejected": "One sentence: why not",
            "risk_if_adopted": "One sentence: what goes wrong"
        }
    ],
    "audit_considerations": {
        "likely_auditor_questions": ["Max 3 questions, one sentence each"],
        "suggested_responses": ["Max 3 responses, one sentence each"],
        "supporting_evidence": ["Max 3 items: documents to prepare"]
    },
    "jurisdiction_notes": "One sentence or null"
}"""

PROMPT_COMPARE = """You are an IFRS expert comparing two possible accounting treatments for a transaction.
Provide a balanced side-by-side comparison showing financial statement impact.

""" + BASE_RULES + """

Respond ONLY in this JSON format. No markdown, no backticks, no preamble:
{
    "transaction_summary": "2 sentences: what the transaction is and why two treatments exist",
    "treatment_a": {
        "name": "Treatment A name",
        "standard": "IFRS XX",
        "description": "2-3 sentences max: how it works",
        "journal_entries": [
            {"description": "One line", "entries": [{"account": "Account", "debit": "Amt", "credit": ""}]}
        ],
        "pnl_impact": {"revenue": "One line", "operating_expense": "One line", "depreciation": "One line", "interest": "One line", "ebitda": "One line — direction + magnitude", "net_profit": "One line"},
        "balance_sheet_impact": {"assets": "One line", "liabilities": "One line", "equity": "One line"},
        "ratio_impact": {"leverage": "Higher/Lower + why", "ebitda_margin": "Higher/Lower + why", "roe": "Higher/Lower + why"},
        "pros": ["Max 3 items, one sentence each"],
        "cons": ["Max 3 items, one sentence each"]
    },
    "treatment_b": {
        "name": "Treatment B name",
        "standard": "IFRS XX or exemption",
        "description": "2-3 sentences max",
        "journal_entries": [
            {"description": "One line", "entries": [{"account": "Account", "debit": "Amt", "credit": ""}]}
        ],
        "pnl_impact": {"revenue": "One line", "operating_expense": "One line", "depreciation": "One line", "interest": "One line", "ebitda": "One line", "net_profit": "One line"},
        "balance_sheet_impact": {"assets": "One line", "liabilities": "One line", "equity": "One line"},
        "ratio_impact": {"leverage": "Higher/Lower + why", "ebitda_margin": "Higher/Lower + why", "roe": "Higher/Lower + why"},
        "pros": ["Max 3 items"],
        "cons": ["Max 3 items"]
    },
    "recommendation": {
        "preferred": "One sentence: which and why",
        "reasoning": "2 sentences: considering entity context",
        "risk_of_wrong_choice": "One sentence"
    },
    "auditor_perspective": "One sentence"
}"""

# ── Examples ──
EXAMPLES = {
    "Quick Treatment": [
        "We signed a 5-year office lease with 6 months rent-free period. Monthly rent $10,000 with 3% annual escalation",
        "Customer paid $500K upfront for a 3-year SaaS license with annual support and implementation services",
        "Issued $10M convertible bonds — 5% coupon, 3-year term, convertible to equity at maturity",
        "Acquired 60% of a subsidiary for $2M. Fair value of net assets is $2.5M",
        "Granted 10,000 employee stock options, exercise price $15, vesting over 3 years, share price $18",
        "Restructuring provision — closing a factory, estimated costs $2M including severance for 50 employees",
        "Sold a building (carrying value $3M) for $5M and leased it back for 10 years at market rent",
        "Construction contract spanning 18 months with milestone payments, total contract value $8M",
        "Imported inventory worth $1M — currently held at cost but net realisable value has dropped to $750K",
        "Government grant of $500K received for purchase of pollution control equipment worth $2M"
    ],
    "Audit Memo": [
        "Management wants to capitalize internal development costs for a new mobile app — $300K spent over 6 months",
        "Revenue recognition for a multi-element arrangement: hardware + software + 3-year support contract totaling $1.2M",
        "Goodwill impairment testing — CGU carrying amount $5M, management's recoverable amount estimate $4.2M",
        "Classification of a sublease — head lease is 10 years, sublease is 8 years",
        "Expected credit loss provisioning methodology for a portfolio of trade receivables across 3 geographies"
    ],
    "Compare Treatments": [
        "5-year equipment lease — capitalize vs short-term/low-value exemption",
        "Investment property — cost model vs fair value model (IAS 40)",
        "Development costs — capitalize under IAS 38 vs expense as incurred",
        "Revenue from long-term contract — over time vs point in time recognition",
        "Foreign operation — translate at closing rate vs temporal method"
    ]
}

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🔧 Analysis Mode")
    mode = st.radio("Select mode:", ["⚡ Quick Treatment", "📄 Audit Memo", "⚖️ Compare Treatments"], label_visibility="collapsed")
    
    clean_mode = mode.split(" ", 1)[1]
    
    st.markdown("---")
    st.markdown(f"### 💡 Example Transactions")
    st.markdown(f"*Examples for {clean_mode} mode:*")
    
    example_key = clean_mode
    for ex in EXAMPLES.get(example_key, EXAMPLES["Quick Treatment"]):
        if st.button(ex, key=f"ex_{hash(ex)}", use_container_width=True):
            st.session_state.selected_example = ex
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        "This tool provides **indicative IFRS guidance** based on AI analysis. "
        "It is **not a substitute** for professional accounting advice. "
        "Always validate with your auditor or technical team."
    )
    
    # Session history
    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 🕐 Session History")
        for i, item in enumerate(reversed(st.session_state.history)):
            trunc = item["transaction"][:60] + "..." if len(item["transaction"]) > 60 else item["transaction"]
            if st.button(f"🔹 {item['mode']}: {trunc}", key=f"hist_{i}", use_container_width=True):
                st.session_state.selected_example = item["transaction"]
                st.rerun()
    
    st.markdown("---")
    st.markdown(
        '<div class="powered-by">Built by Akshita Gagrani<br>Exploring AI in Finance Series</div>',
        unsafe_allow_html=True
    )

# ── Mode display ──
mode_descriptions = {
    "Quick Treatment": "Get the full IFRS treatment: standard, recognition, measurement, journal entries, disclosure draft, and practical notes.",
    "Audit Memo": "Generate a structured technical accounting memo: issue, guidance, analysis, conclusion, alternative views — ready to share with auditors.",
    "Compare Treatments": "Compare two possible accounting treatments side by side: P&L impact, balance sheet impact, ratio impact, and recommendation."
}
st.markdown(f"**Mode: {clean_mode}** — {mode_descriptions[clean_mode]}")

# ── Input ──
st.markdown("### Describe your transaction")
input_tab1, input_tab2 = st.tabs(["✏️ Type a Transaction", "📄 Upload a Document"])

with input_tab1:
    # Load selected example into session state if available
    if "selected_example" in st.session_state:
        st.session_state.transaction_input = st.session_state.pop("selected_example")
    
    transaction = st.text_area(
        "What happened? Be as specific as you can — amounts, dates, terms, parties involved.",
        height=120,
        placeholder="e.g., We signed a 5-year office lease starting Jan 2025. Monthly rent $10,000 with 3% annual escalation and a 6-month rent-free period.",
        key="transaction_input"
    )
    uploaded_file = None

with input_tab2:
    st.markdown("Upload a contract, agreement, or financial document (PDF). The AI will extract and analyze the IFRS-relevant content.")
    uploaded_file_input = st.file_uploader(
        "Upload PDF document",
        type=["pdf"],
        help="Max 30MB. Best results with text-based PDFs. Scanned documents may have reduced accuracy."
    )
    upload_context = st.text_input(
        "What should the AI focus on? (optional)",
        placeholder="e.g., Analyze the lease terms and provide IFRS 16 treatment",
        key="upload_focus"
    )
    if uploaded_file_input:
        uploaded_file = uploaded_file_input
        transaction = upload_context if upload_context else "Analyze this document and provide the relevant IFRS accounting treatment, journal entries, and disclosure requirements."
    else:
        if not transaction:
            transaction = ""

# Usage counter display (only for free tier)
if not st.session_state.is_premium:
    remaining = MAX_FREE_ANALYSES - st.session_state.usage_count
    if remaining <= 2 and remaining > 0:
        st.markdown(f'<div style="background:#FFF3E0;border:1px solid #FF9800;border-radius:6px;padding:0.5rem 1rem;font-size:0.82rem;color:#E65100;">⚠️ {remaining} free analyses remaining. Upgrade to Premium for unlimited access.</div>', unsafe_allow_html=True)
    elif remaining <= 0:
        payment_url = st.secrets.get("PAYMENT_URL", "https://www.linkedin.com/in/akshita-gagrani-02457091")
        st.markdown(f"""
        <div style="background:#FFEBEE;border:1px solid #EF5350;border-radius:8px;padding:1.2rem;font-size:0.9rem;color:#C62828;">
            <strong>🔒 Free trial ended.</strong> You've used all 5 free analyses.<br><br>
            Upgrade to <strong>Premium ($9.99/month)</strong> for unlimited analyses, document uploads, and all features.<br><br>
            <a href="{payment_url}" target="_blank" style="display:inline-block; background:#002060; color:white; padding:0.5rem 1.5rem; border-radius:6px; text-decoration:none; font-weight:600; font-size:0.9rem;">💳 Upgrade to Premium</a>
            <span style="margin-left:1rem; font-size:0.82rem; color:#888;">or DM <a href="https://www.linkedin.com/in/akshita-gagrani-02457091" target="_blank">Akshita on LinkedIn</a></span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background:#F0F4F8;border:1px solid #D0D8E0;border-radius:6px;padding:0.4rem 1rem;font-size:0.78rem;color:#666;">🆓 Free trial: {remaining} of {MAX_FREE_ANALYSES} analyses remaining | Follow-up questions are unlimited</div>', unsafe_allow_html=True)

can_analyze = st.session_state.is_premium or (st.session_state.usage_count < MAX_FREE_ANALYSES)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True, disabled=(not can_analyze))
with col_btn2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.rerun()

# ── PDF Export Helper ──
def generate_pdf_content(result, mode_name, transaction_text, ctx):
    """Generate a simple HTML-based printable report"""
    timestamp = datetime.now().strftime("%d %B %Y, %H:%M")
    ctx_line = f"<p><strong>Context:</strong> {ctx}</p>" if ctx else ""
    
    html = f"""
    <html><head><style>
        body {{ font-family: Arial, sans-serif; font-size: 11px; color: #333; margin: 40px; }}
        h1 {{ color: #002060; font-size: 18px; border-bottom: 2px solid #002060; padding-bottom: 8px; }}
        h2 {{ color: #002060; font-size: 14px; margin-top: 20px; }}
        h3 {{ color: #0050A0; font-size: 12px; }}
        .tag {{ background: #002060; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold; display: inline-block; }}
        table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
        th {{ background: #002060; color: white; padding: 6px 10px; text-align: left; font-size: 10px; }}
        td {{ padding: 5px 10px; border-bottom: 1px solid #E0E0E0; font-size: 10px; }}
        .caveat {{ background: #FFF8E1; border: 1px solid #FFD54F; padding: 10px; margin-top: 20px; font-size: 10px; border-radius: 6px; }}
        .meta {{ color: #888; font-size: 9px; }}
    </style></head><body>
    <h1>📘 IFRS Accounting Copilot — {mode_name}</h1>
    <p class="meta">Generated: {timestamp} | AI-generated guidance — requires professional review</p>
    {ctx_line}
    <p><strong>Transaction:</strong> {transaction_text}</p>
    <hr>
    """
    
    if mode_name == "Quick Treatment":
        r = result
        html += f'<h2>Applicable Standard</h2><div class="tag">{r["applicable_standard"]["primary"]}</div>'
        html += f'<p>{r["applicable_standard"]["why"]}</p>'
        if r["applicable_standard"].get("key_paragraphs"):
            html += "<p><strong>Key paragraphs:</strong> " + ", ".join(r["applicable_standard"]["key_paragraphs"]) + "</p>"
        
        html += f'<h2>Recognition</h2><p><strong>Criteria:</strong> {r["recognition"]["criteria"]}</p>'
        html += f'<p><strong>Timing:</strong> {r["recognition"]["timing"]}</p>'
        
        html += f'<h2>Measurement</h2><p><strong>Initial:</strong> {r["measurement"]["initial"]}</p>'
        html += f'<p><strong>Subsequent:</strong> {r["measurement"]["subsequent"]}</p>'
        
        html += '<h2>Journal Entries</h2>'
        for je in r["journal_entries"]:
            html += f'<h3>{je.get("timing", "")} — {je["description"]}</h3>'
            html += '<table><tr><th>Account</th><th>Debit</th><th>Credit</th></tr>'
            for e in je["entries"]:
                html += f'<tr><td>{e["account"]}</td><td>{e.get("debit","")}</td><td>{e.get("credit","")}</td></tr>'
            html += '</table>'
        
        if r.get("disclosure_draft"):
            html += '<h2>Disclosure Draft</h2>'
            html += f'<p><strong>Accounting Policy:</strong> {r["disclosure_draft"].get("accounting_policy", "")}</p>'
            if r["disclosure_draft"].get("note_disclosures"):
                html += '<ul>'
                for d in r["disclosure_draft"]["note_disclosures"]:
                    html += f'<li>{d}</li>'
                html += '</ul>'
        
        if r.get("key_judgments"):
            html += '<h2>Key Judgments</h2><ul>'
            for kj in r["key_judgments"]:
                html += f'<li>{kj}</li>'
            html += '</ul>'
    
    elif mode_name == "Audit Memo":
        r = result
        html += f'<h1>{r.get("memo_title", "Technical Accounting Memo")}</h1>'
        html += f'<p class="meta">Prepared by: {r.get("prepared_by", "IFRS Copilot")} | {r.get("date", timestamp)}</p>'
        
        html += '<h2>1. Issue</h2>'
        html += f'<p>{r["issue"]["summary"]}</p>'
        html += f'<p><strong>Background:</strong> {r["issue"]["background"]}</p>'
        html += f'<p><strong>Question:</strong> {r["issue"]["question"]}</p>'
        
        html += '<h2>2. Relevant Guidance</h2>'
        html += f'<p><strong>Primary Standard:</strong> {r["relevant_guidance"]["primary_standard"]}</p>'
        if r["relevant_guidance"].get("key_paragraphs"):
            html += '<ul>'
            for p in r["relevant_guidance"]["key_paragraphs"]:
                html += f'<li>{p}</li>'
            html += '</ul>'
        
        html += '<h2>3. Analysis</h2>'
        html += f'<p>{r["analysis"]["application"]}</p>'
        
        html += '<h2>4. Conclusion</h2>'
        html += f'<p>{r["conclusion"]["recommended_treatment"]}</p>'
        
        if r.get("alternative_views"):
            html += '<h2>5. Alternative Views</h2>'
            for av in r["alternative_views"]:
                html += f'<p><strong>{av["alternative"]}</strong><br>Rejected because: {av["why_rejected"]}</p>'
        
        if r.get("audit_considerations"):
            html += '<h2>6. Audit Considerations</h2>'
            if r["audit_considerations"].get("likely_auditor_questions"):
                html += '<ul>'
                for q in r["audit_considerations"]["likely_auditor_questions"]:
                    html += f'<li>{q}</li>'
                html += '</ul>'
    
    html += """
    <div class="caveat">
        <strong>⚠️ Disclaimer:</strong> This is AI-generated indicative guidance based on IFRS standards as issued by the IASB.
        It is not a substitute for professional accounting advice. The actual treatment may vary based on specific facts,
        circumstances, and jurisdictional requirements. Always consult with your auditor or technical accounting team.
        Verify all paragraph references against the current IFRS standards (eIFRS or IFRS Red Book).
    </div>
    </body></html>
    """
    return html

def get_download_link(html_content, filename):
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="background:#002060;color:white;padding:0.5rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.9rem;">📥 Download as HTML Report</a>'

# ── Render functions ──
def render_quick(result):
    r = result
    
    # Standard - single HTML block
    if r.get("applicable_standard"):
        std_html = '<div class="section-card"><div class="section-title">📌 Applicable Standard</div>'
        std_html += f'<div class="ifrs-tag">{r["applicable_standard"].get("primary", "See analysis")}</div>'
        if r["applicable_standard"].get("secondary"):
            for sec in r["applicable_standard"]["secondary"]:
                std_html += f'<p style="margin:3px 0;font-size:0.9rem;"><strong>Also relevant:</strong> {sec}</p>'
        if r["applicable_standard"].get("why"):
            std_html += f'<p style="margin:4px 0;"><strong>Why:</strong> {r["applicable_standard"]["why"]}</p>'
        if r["applicable_standard"].get("key_paragraphs"):
            std_html += f'<div class="ref-box">📖 <strong>Key references:</strong> {", ".join(r["applicable_standard"]["key_paragraphs"])}</div>'
        complexity = r.get("complexity_rating", "Medium")
        cmap = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
        std_html += f'<p style="margin:6px 0;"><strong>Complexity:</strong> <span style="color:{cmap.get(complexity,"#FF9800")};font-weight:700;">{complexity}</span></p>'
        std_html += '</div>'
        st.markdown(std_html, unsafe_allow_html=True)
    
    # Recognition & Measurement - single HTML block to avoid Streamlit gaps
    rm_html = '<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:4px;">'
    
    if r.get('recognition'):
        rm_html += '<div class="section-card">'
        rm_html += '<div class="section-title">✅ Recognition</div>'
        rm_html += f'<p style="margin:4px 0;"><strong>Criteria:</strong> {r["recognition"].get("criteria","N/A")}</p>'
        rm_html += f'<p style="margin:4px 0;"><strong>Timing:</strong> {r["recognition"].get("timing","N/A")}</p>'
        if r['recognition'].get('conditions'):
            for cond in r['recognition']['conditions']:
                rm_html += f'<p style="margin:2px 0 2px 12px;font-size:0.9rem;">• {cond}</p>'
        if r['recognition'].get('industry_considerations') and r['recognition']['industry_considerations'] not in ["null", None]:
            rm_html += f'<p style="margin:6px 0;"><strong>Industry note:</strong> {r["recognition"]["industry_considerations"]}</p>'
        rm_html += '</div>'
    
    if r.get('measurement'):
        rm_html += '<div class="section-card">'
        rm_html += '<div class="section-title">📏 Measurement</div>'
        rm_html += f'<p style="margin:4px 0;"><strong>Initial:</strong> {r["measurement"].get("initial","N/A")}</p>'
        rm_html += f'<p style="margin:4px 0;"><strong>Subsequent:</strong> {r["measurement"].get("subsequent","N/A")}</p>'
        rm_html += f'<p style="margin:4px 0;"><strong>Method:</strong> {r["measurement"].get("method","N/A")}</p>'
        if r['measurement'].get('rates_assumptions'):
            rm_html += f'<p style="margin:4px 0;"><strong>Key assumptions:</strong> {r["measurement"]["rates_assumptions"]}</p>'
        rm_html += '</div>'
    
    rm_html += '</div>'
    st.markdown(rm_html, unsafe_allow_html=True)
    
    # Thin divider
    st.markdown('<hr class="blue-divider">', unsafe_allow_html=True)
    
    # Journal Entries - single HTML block
    if r.get("journal_entries"):
        je_html = '<div class="section-card"><div class="section-title">📝 Journal Entries</div>'
    for je in r["journal_entries"]:
        timing_label = f" ({je['timing']})" if je.get('timing') else ""
        je_html += f'<p style="margin:6px 0;font-weight:700;">{je["description"]}{timing_label}</p>'
        je_html += '<table class="journal-table"><tr><th>Account</th><th>Debit</th><th>Credit</th></tr>'
        for e in je["entries"]:
            je_html += f'<tr><td>{e["account"]}</td><td>{e.get("debit","")}</td><td>{e.get("credit","")}</td></tr>'
        je_html += '</table>'
    je_html += '</div>'
    st.markdown(je_html, unsafe_allow_html=True)
    
    # Thin divider
    st.markdown('<hr class="blue-divider">', unsafe_allow_html=True)
    
    # Disclosure Draft as single HTML block
    if r.get("disclosure_draft"):
        dd = r["disclosure_draft"]
        disc_html = '<div class="section-card"><div class="section-title">📋 Disclosure Draft</div>'
        if dd.get("accounting_policy"):
            disc_html += f'<div class="memo-section"><div class="memo-label">Accounting Policy Wording</div>{dd["accounting_policy"]}</div>'
        if dd.get("note_disclosures"):
            disc_html += '<p style="margin:8px 0 4px;font-weight:700;">Required Note Disclosures:</p>'
            for d in dd["note_disclosures"]:
                disc_html += f'<div class="disclosure-item">{d}</div>'
        if dd.get("quantitative_disclosures"):
            disc_html += '<p style="margin:8px 0 4px;font-weight:700;">Quantitative Schedules Required:</p>'
            for q in dd["quantitative_disclosures"]:
                disc_html += f'<p style="margin:2px 0 2px 12px;font-size:0.9rem;">• {q}</p>'
        disc_html += '</div>'
        st.markdown(disc_html, unsafe_allow_html=True)
    
    # Thin divider
    st.markdown('<hr class="blue-divider">', unsafe_allow_html=True)
    
    # Practical Notes & Judgments - rendered as single HTML to avoid Streamlit gaps
    pn_html = '<div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:4px;">'
    
    # Left column - Practical Notes
    pn_html += '<div class="section-card">'
    pn_html += '<div class="section-title">⚠️ Practical Notes</div>'
    for n in r.get("practical_notes", []):
        pn_html += f'<p style="margin:4px 0;font-size:0.9rem;">• {n}</p>'
    if r.get("common_errors"):
        pn_html += '<p style="margin:8px 0 4px;font-weight:700;">Common errors:</p>'
        for ce in r.get("common_errors", []):
            pn_html += f'<p style="margin:3px 0;font-size:0.9rem;">🔴 {ce}</p>'
    pn_html += '</div>'
    
    # Right column - Key Judgments
    pn_html += '<div class="section-card">'
    pn_html += '<div class="section-title">🔍 Key Judgments</div>'
    for kj in r.get("key_judgments", []):
        pn_html += f'<p style="margin:4px 0;font-size:0.9rem;">🔸 {kj}</p>'
    if r.get("jurisdiction_notes") and r.get("jurisdiction_notes") not in ["null", None]:
        pn_html += f'<p style="margin:8px 0 4px;font-weight:700;">Jurisdiction note:</p>'
        pn_html += f'<p style="margin:3px 0;font-size:0.9rem;">{r["jurisdiction_notes"]}</p>'
    pn_html += '</div></div>'
    
    st.markdown(pn_html, unsafe_allow_html=True)


def render_memo(result):
    r = result
    st.markdown(f'<div class="section-card"><div class="ifrs-tag">{r.get("memo_title", "Technical Accounting Memo")}</div>', unsafe_allow_html=True)
    st.markdown(f'*Prepared by: {r.get("prepared_by", "IFRS Copilot")} | {r.get("date", "")}*')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Issue
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1️⃣ Issue</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="memo-section"><div class="memo-label">Summary</div>{r["issue"]["summary"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="memo-section"><div class="memo-label">Background</div>{r["issue"]["background"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="memo-section"><div class="memo-label">Question</div>{r["issue"]["question"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Guidance
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2️⃣ Relevant IFRS Guidance</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ifrs-tag">{r["relevant_guidance"]["primary_standard"]}</div>', unsafe_allow_html=True)
    if r["relevant_guidance"].get("key_paragraphs"):
        for p in r["relevant_guidance"]["key_paragraphs"]:
            st.markdown(f'<div class="disclosure-item">{p}</div>', unsafe_allow_html=True)
    if r["relevant_guidance"].get("interpretations"):
        st.markdown("**Relevant interpretations:**")
        for interp in r["relevant_guidance"]["interpretations"]:
            st.markdown(f"- {interp}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3️⃣ Analysis</div>', unsafe_allow_html=True)
    st.markdown(f"**Approach:** {r['analysis']['approach']}")
    st.markdown(f'<div class="memo-section"><div class="memo-label">Application</div>{r["analysis"]["application"]}</div>', unsafe_allow_html=True)
    if r["analysis"].get("key_judgments"):
        for kj in r["analysis"]["key_judgments"]:
            st.markdown(f"**Judgment:** {kj['judgment']}")
            st.markdown(f"*Our position:* {kj['our_position']}")
            st.markdown(f"*Sensitivity:* {kj['sensitivity']}")
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Conclusion
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4️⃣ Conclusion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="memo-section"><div class="memo-label">Recommended Treatment</div>{r["conclusion"]["recommended_treatment"]}</div>', unsafe_allow_html=True)
    if r["conclusion"].get("journal_entries"):
        for je in r["conclusion"]["journal_entries"]:
            st.markdown(f"**{je['description']}**")
            tbl = '<table class="journal-table"><tr><th>Account</th><th>Debit</th><th>Credit</th></tr>'
            for e in je["entries"]:
                tbl += f'<tr><td>{e["account"]}</td><td>{e.get("debit","")}</td><td>{e.get("credit","")}</td></tr>'
            tbl += '</table>'
            st.markdown(tbl, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alternatives
    if r.get("alternative_views"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">5️⃣ Alternative Views</div>', unsafe_allow_html=True)
        for av in r["alternative_views"]:
            st.markdown(f'<div class="memo-section"><div class="memo-label">{av["alternative"]}</div>'
                       f'<strong>Rejected because:</strong> {av["why_rejected"]}<br>'
                       f'<strong>Risk if adopted:</strong> {av["risk_if_adopted"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Audit
    if r.get("audit_considerations"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">6️⃣ Audit Considerations</div>', unsafe_allow_html=True)
        ac = r["audit_considerations"]
        if ac.get("likely_auditor_questions") and ac.get("suggested_responses"):
            for q, a in zip(ac["likely_auditor_questions"], ac["suggested_responses"]):
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**A:** {a}")
                st.markdown("")
        if ac.get("supporting_evidence"):
            st.markdown("**Evidence to prepare:**")
            for ev in ac["supporting_evidence"]:
                st.markdown(f"📎 {ev}")
        st.markdown('</div>', unsafe_allow_html=True)


def render_compare(result):
    r = result
    st.markdown(f'<div class="section-card"><div class="section-title">⚖️ Transaction Summary</div>{r["transaction_summary"]}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    for col, treatment, header_class in [(c1, r["treatment_a"], "compare-header-a"), (c2, r["treatment_b"], "compare-header-b")]:
        with col:
            st.markdown(f'<div class="compare-col">', unsafe_allow_html=True)
            st.markdown(f'<div class="{header_class}">{treatment["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'*{treatment["standard"]}*')
            st.markdown(f'{treatment["description"]}')
            
            # JEs
            if treatment.get("journal_entries"):
                st.markdown("**Journal Entries:**")
                for je in treatment["journal_entries"]:
                    tbl = '<table class="journal-table"><tr><th>Account</th><th>Dr</th><th>Cr</th></tr>'
                    for e in je["entries"]:
                        tbl += f'<tr><td>{e["account"]}</td><td>{e.get("debit","")}</td><td>{e.get("credit","")}</td></tr>'
                    tbl += '</table>'
                    st.markdown(tbl, unsafe_allow_html=True)
            
            # P&L Impact
            st.markdown("**P&L Impact:**")
            for k, v in treatment.get("pnl_impact", {}).items():
                st.markdown(f"- {k.replace('_',' ').title()}: {v}")
            
            # BS Impact
            st.markdown("**Balance Sheet:**")
            for k, v in treatment.get("balance_sheet_impact", {}).items():
                st.markdown(f"- {k.title()}: {v}")
            
            # Ratios
            st.markdown("**Ratio Impact:**")
            for k, v in treatment.get("ratio_impact", {}).items():
                st.markdown(f"- {k.replace('_',' ').title()}: {v}")
            
            st.markdown("**✅ Pros:**")
            for p in treatment.get("pros", []):
                st.markdown(f"- {p}")
            st.markdown("**❌ Cons:**")
            for c_item in treatment.get("cons", []):
                st.markdown(f"- {c_item}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendation
    rec = r.get("recommendation", {})
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✅ Recommendation</div>', unsafe_allow_html=True)
    st.markdown(f"**Preferred:** {rec.get('preferred', '')}")
    st.markdown(f"**Reasoning:** {rec.get('reasoning', '')}")
    st.markdown(f"**Risk of wrong choice:** {rec.get('risk_of_wrong_choice', '')}")
    if r.get("auditor_perspective"):
        st.markdown(f"**Auditor perspective:** {r['auditor_perspective']}")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Analysis Execution ──
if analyze_btn and (transaction.strip() or (uploaded_file if 'uploaded_file' in dir() else False)):
    if not st.session_state.is_premium and st.session_state.usage_count >= MAX_FREE_ANALYSES:
        st.error("Free trial ended. DM Akshita on LinkedIn for the Premium access code to unlock unlimited analyses.")
    else:
        model = get_model()
        context_block = build_context_block()
        
        prompt_map = {
            "Quick Treatment": PROMPT_QUICK,
            "Audit Memo": PROMPT_MEMO,
            "Compare Treatments": PROMPT_COMPARE
        }
        
        # Build message parts
        message_parts = []
        if 'uploaded_file' in dir() and uploaded_file:
            file_bytes = uploaded_file.read()
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            message_parts.append({"mime_type": "application/pdf", "data": file_b64})
        
        full_prompt = prompt_map[clean_mode] + "\n\n" + context_block + "\n\nTransaction to analyze:\n" + transaction
        message_parts.append(full_prompt)
        
        # Loading states
        loading_msgs = {
            "Quick Treatment": ["🔍 Identifying applicable IFRS standard...", "📝 Generating journal entries...", "📋 Drafting disclosures...", "✅ Finalising analysis..."],
            "Audit Memo": ["📄 Structuring the memo...", "📖 Mapping IFRS guidance...", "⚖️ Evaluating alternative views...", "✅ Preparing audit considerations..."],
            "Compare Treatments": ["⚖️ Analysing Treatment A...", "⚖️ Analysing Treatment B...", "📊 Calculating financial impact...", "✅ Generating recommendation..."]
        }
        
        progress = st.progress(0)
        status = st.empty()
        msgs = loading_msgs.get(clean_mode, loading_msgs["Quick Treatment"])
        
        import time
        for i in range(2):
            status.markdown(f"*{msgs[i]}*")
            progress.progress((i + 1) * 25)
            time.sleep(0.4)
        
        # Retry logic — 2 attempts
        result = None
        raw = ""
        for attempt in range(2):
            try:
                status.markdown(f"*{msgs[2]}*")
                progress.progress(75)
                
                response = model.generate_content(
                    [{"role": "user", "parts": message_parts}],
                    generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=8192)
                )
                
                raw = response.text.strip()
                if raw.startswith("```"): raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"): raw = raw[:-3]
                if raw.startswith("json"): raw = raw[4:]
                raw = raw.strip()
                
                # Handle truncated JSON — try to fix common truncation issues
                try:
                    result = json.loads(raw)
                except json.JSONDecodeError:
                    # Try to close open strings, arrays, objects
                    fixed = raw.rstrip()
                    # Remove trailing incomplete string
                    if fixed.count('"') % 2 != 0:
                        last_quote = fixed.rfind('"')
                        fixed = fixed[:last_quote+1]
                    # Close open brackets
                    open_brackets = fixed.count('[') - fixed.count(']')
                    open_braces = fixed.count('{') - fixed.count('}')
                    # Trim to last complete value
                    while fixed and fixed[-1] not in ']}"\d':
                        fixed = fixed[:-1]
                    fixed = fixed.rstrip(',')
                    fixed += ']' * open_brackets + '}' * open_braces
                    result = json.loads(fixed)
                status.markdown(f"*{msgs[3]}*")
                progress.progress(100)
                time.sleep(0.3)
                break
                
            except json.JSONDecodeError:
                if attempt == 0:
                    status.markdown("*⚠️ Retrying analysis...*")
                    time.sleep(1)
                else:
                    progress.empty(); status.empty()
                    st.error("⚠️ Failed to parse response after 2 attempts. Please try again.")
                    with st.expander("Raw response (for debugging)"):
                        st.text(raw)
            except Exception as e:
                progress.empty(); status.empty()
                st.error(f"⚠️ Error: {str(e)}")
                break
        
        progress.empty(); status.empty()
        
        if result:
            # Only increment counter for free tier new analyses (not follow-ups)
            if not st.session_state.is_premium:
                st.session_state.usage_count += 1
                # Persist to file so it survives page refresh
                if "pw_hash" in st.session_state:
                    save_usage(st.session_state.pw_hash, st.session_state.usage_count)
            
            st.session_state.last_result = result
            st.session_state.last_transaction = transaction
            st.session_state.last_mode = clean_mode
            
            display_name = uploaded_file.name if ('uploaded_file' in dir() and uploaded_file) else transaction[:60]
            st.session_state.history.append({
                "transaction": transaction, "mode": clean_mode,
                "timestamp": datetime.now().strftime("%H:%M"), "display": display_name
            })
            if len(st.session_state.history) > 10:
                st.session_state.history = st.session_state.history[-10:]
            
            st.markdown("---")
            
            if 'uploaded_file' in dir() and uploaded_file:
                file_size = len(file_bytes) / 1024
                sz = f"{file_size:.0f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                st.markdown(f'<div class="context-bar">📄 <strong>Document analyzed:</strong> {uploaded_file.name} ({sz})</div>', unsafe_allow_html=True)
            
            if clean_mode == "Quick Treatment":
                render_quick(result)
            elif clean_mode == "Audit Memo":
                render_memo(result)
            elif clean_mode == "Compare Treatments":
                render_compare(result)
            
            st.markdown("""
            <div class="caveat-box">
                <strong>⚠️ Important Disclaimer:</strong> This is AI-generated indicative guidance based on IFRS standards as issued by the IASB.
                It is not a substitute for professional accounting advice. Actual treatment may vary based on specific facts, circumstances,
                and jurisdictional requirements. Always consult your auditor or technical accounting team before finalising treatment.
                Verify all IFRS paragraph references against the current standards via <a href="https://www.ifrs.org/issued-standards/" target="_blank">eIFRS</a> or the IFRS Red Book.
            </div>
            """, unsafe_allow_html=True)
            
            # Follow-up
            st.markdown("---")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💬 Ask a Follow-Up Question</div>', unsafe_allow_html=True)
            st.markdown("Refine or extend this analysis — e.g., *'What if the lease has a purchase option?'* or *'How does this change for an SME?'*")
            st.markdown('</div>', unsafe_allow_html=True)

# ── Follow-up section (always visible if last_result exists) ──
if st.session_state.last_result and not (analyze_btn and (transaction.strip() or (uploaded_file if 'uploaded_file' in dir() else False))):
    # Re-render last result when returning to page (e.g., after follow-up rerun)
    result = st.session_state.last_result
    clean_mode = st.session_state.last_mode
    transaction = st.session_state.last_transaction
    
    st.markdown("---")
    if clean_mode == "Quick Treatment":
        render_quick(result)
    elif clean_mode == "Audit Memo":
        render_memo(result)
    elif clean_mode == "Compare Treatments":
        render_compare(result)
    
    st.markdown("""
    <div class="caveat-box">
        <strong>⚠️ Important Disclaimer:</strong> This is AI-generated indicative guidance based on IFRS standards as issued by the IASB.
        It is not a substitute for professional accounting advice. Always consult your auditor or technical accounting team.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Ask a Follow-Up Question</div>', unsafe_allow_html=True)
    st.markdown("Refine or extend this analysis — follow-ups are unlimited and don't count toward your trial.")
    st.markdown('</div>', unsafe_allow_html=True)

# Follow-up input (always available if last_result exists)
if st.session_state.last_result:
    followup = st.text_input("Follow-up question:", placeholder="What if...", key="followup_input")
    if st.button("🔄 Ask Follow-Up", key="followup_btn") and followup.strip():
        model = get_model()
        context_block = build_context_block()
        followup_prompt = (
            f"Previous analysis context:\nTransaction: {st.session_state.last_transaction}\n"
            f"Mode: {st.session_state.last_mode}\n"
            f"Previous result (summary): {json.dumps(st.session_state.last_result, ensure_ascii=False)[:3000]}\n\n"
            f"{context_block}\n\nFollow-up question: {followup}\n\n"
            f"Provide a focused answer. Reference the previous analysis. "
            f"If the follow-up changes the treatment, state what changes and what stays the same. "
            f"Respond in plain text (not JSON). Be specific and practical."
        )
        lang_name = output_language.split(" (")[0] if " (" in output_language else output_language
        if lang_name != "English":
            followup_prompt += f"\n\nRespond in {lang_name}."
        
        with st.spinner("Analyzing follow-up..."):
            try:
                fu_resp = model.generate_content(
                    [{"role": "user", "parts": [followup_prompt]}],
                    generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=3000))
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">💬 Follow-Up Response</div>', unsafe_allow_html=True)
                st.markdown(fu_resp.text)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Follow-up error: {str(e)}")

elif analyze_btn:
    st.warning("Please describe a transaction or upload a document first.")

# ── Footer ──
st.markdown(
    '<div class="powered-by">IFRS Accounting Copilot — Part of the "Exploring AI in Finance" series by Akshita Gagrani</div>',
    unsafe_allow_html=True
)
