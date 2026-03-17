# app.py
# Gujarat Domestic Worker Registration System — v4.1
# Sidebar ALWAYS shows all 3 role options
# Login appears inline in main area when Admin/Employer selected while not logged in
# Worker portal: never requires login

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from PIL import Image
import io

st.set_page_config(
    page_title="Gujarat Domestic Worker System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS + JS — sidebar always open
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Sidebar always open ── */
[data-testid="stSidebar"] {
    display:block !important; visibility:visible !important;
    opacity:1 !important; width:18rem !important;
    min-width:18rem !important; transform:translateX(0) !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    display:block !important; width:18rem !important;
    min-width:18rem !important; transform:translateX(0) !important;
}
section[data-testid="stSidebarContent"] {
    display:block !important; visibility:visible !important;
}
button[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stSidebar"] > div:first-child {
    background:linear-gradient(180deg,#003366 0%,#004488 100%) !important;
    border-right:3px solid #FF6600 !important;
}
[data-testid="stSidebar"] * { color:white !important; }
[data-testid="stSidebar"] .stSelectbox label {
    color:#B8C8D8 !important; font-size:0.78rem !important;
    text-transform:uppercase !important; letter-spacing:0.05em !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background:rgba(255,255,255,0.12) !important;
    border:1px solid rgba(255,255,255,0.25) !important;
}
[data-testid="stSidebar"] .stSelectbox svg { fill:white !important; }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.2) !important; }

/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{ font-family:'Inter','Noto Sans Gujarati',sans-serif; }
.block-container{ padding-top:1.5rem; padding-bottom:2rem; max-width:1100px; }

/* ── Header ── */
.guj-header {
    background:linear-gradient(135deg,#003366 0%,#004499 50%,#003366 100%);
    border-bottom:4px solid #FF6600; padding:1rem 1.5rem;
    border-radius:10px; margin-bottom:1.5rem;
    display:flex; align-items:center; gap:1rem;
}
.guj-header h1 { color:white !important; font-size:1.3rem !important; font-weight:700 !important; margin:0 !important; }
.guj-header p  { color:#B8C8D8 !important; font-size:0.8rem; margin:0.2rem 0 0; }

/* ── Login card ── */
.login-card {
    max-width:460px; margin:2rem auto;
    background:white; border:1px solid #DDE3EA;
    border-radius:16px; padding:2rem 2rem 1.5rem;
    box-shadow:0 4px 24px rgba(0,51,102,0.08);
}
.login-card h2 { color:#003366; font-size:1.25rem; font-weight:700; margin:0 0 0.25rem; }
.login-card p  { color:#64748B; font-size:0.83rem; margin:0 0 1.3rem; }
.otp-box {
    background:#F0F4FF; border:1px solid #C7D2FE;
    border-radius:10px; padding:1rem; margin:0.8rem 0;
    text-align:center;
}
.otp-box .otp-label { font-size:0.72rem; color:#4338CA; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.3rem; }
.otp-box .otp-code  { font-size:2rem; font-weight:800; color:#003366; letter-spacing:0.3em; font-family:monospace; }
.otp-box .otp-sub   { font-size:0.7rem; color:#6366F1; margin-top:0.15rem; }
.demo-accounts {
    background:#F8FAFC; border:1px solid #E2E8F0;
    border-radius:8px; padding:0.7rem 0.9rem;
    font-size:0.78rem; line-height:2; margin-bottom:1rem;
}
.user-badge {
    background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2);
    border-radius:10px; padding:0.6rem 0.8rem; margin-bottom:0.6rem;
}
.ub-name  { font-size:0.86rem; font-weight:600; color:white; }
.ub-phone { font-size:0.7rem;  color:#90A8C0; }
.ub-role  { font-size:0.68rem; color:#FFB347; text-transform:uppercase; letter-spacing:0.05em; margin-top:0.1rem; }
.lock-banner {
    background:#FEF3C7; border:1px solid #FCD34D;
    border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:1.5rem;
    text-align:center;
}
.lock-banner .lb-icon  { font-size:2rem; margin-bottom:0.3rem; }
.lock-banner .lb-title { font-weight:700; color:#92400E; font-size:1rem; }
.lock-banner .lb-sub   { font-size:0.82rem; color:#78350F; margin-top:0.2rem; }

/* ── Metric cards ── */
.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.5rem; }
.metric-card { background:white; border:1px solid #DDE3EA; border-radius:10px; padding:1.1rem; text-align:center; }
.metric-card .metric-value { font-size:2rem; font-weight:700; line-height:1; margin-bottom:0.3rem; }
.metric-card .metric-label { font-size:0.73rem; color:#64748B; text-transform:uppercase; letter-spacing:0.04em; }
.metric-blue{color:#003366;} .metric-orange{color:#FF6600;} .metric-green{color:#16A34A;} .metric-red{color:#DC2626;}

/* ── General ── */
.section-card { background:white; border:1px solid #DDE3EA; border-radius:12px; padding:1.4rem; margin-bottom:1rem; }
.section-card h3 { color:#003366; font-size:0.93rem; font-weight:600; margin:0 0 1rem;
    padding-bottom:0.5rem; border-bottom:2px solid #FF6600; display:inline-block; }
.worker-profile { background:linear-gradient(135deg,#F8FAFC 0%,#EFF6FF 100%);
    border:1px solid #BFDBFE; border-radius:12px; padding:1.2rem; margin-bottom:1rem; }
.worker-name { font-size:1.15rem; font-weight:700; color:#003366; }
.worker-id   { font-size:0.76rem; color:#64748B; font-family:monospace; }
.verified-banner { background:#DCFCE7; border:2px solid #22C55E; border-radius:10px; padding:0.65rem 1rem; margin:0.65rem 0; }
.verified-banner .v-text { font-weight:700; color:#15803D; font-size:0.88rem; }
.verified-banner .v-sub  { font-size:0.71rem; color:#16A34A; }
.risk-high { background:#FFF7ED; border-left:4px solid #F97316; border-radius:0 8px 8px 0; padding:0.65rem 0.9rem; margin:0.4rem 0; }
.risk-high p { margin:0; color:#9A3412; font-size:0.81rem; }
.info-box { background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:0.65rem 0.9rem; font-size:0.8rem; color:#1E40AF; }
.agent-step { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:0.85rem; }
.compliance-panel { background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px; padding:0.9rem 1rem; margin:0.7rem 0; }
.compliance-row { display:flex; justify-content:space-between; align-items:center; padding:0.28rem 0; border-bottom:1px solid #DCFCE7; font-size:0.78rem; }
.compliance-row:last-of-type { border-bottom:none; }
.c-pass{color:#16A34A;font-weight:700;} .c-fail{color:#DC2626;font-weight:700;}
.clearance-clear{background:#DCFCE7;color:#15803D;} .clearance-review{background:#FEF3C7;color:#92400E;} .clearance-block{background:#FEE2E2;color:#991B1B;}
.notify-panel { background:#F0F4FF; border:1px solid #C7D2FE; border-radius:8px; padding:0.7rem 0.9rem; margin:0.5rem 0; font-size:0.8rem; color:#3730A3; }
.notify-panel strong { display:block; margin-bottom:0.2rem; font-size:0.73rem; color:#6366F1; text-transform:uppercase; letter-spacing:0.04em; }
.prompt-decision { background:#EFF6FF; border-left:3px solid #3B82F6; padding:0.4rem 0.65rem; border-radius:0 6px 6px 0; font-size:0.77rem; color:#1E40AF; margin:0.22rem 0; }
.compliance-footer { background:#F8FAFC; border:1px solid #DDE3EA; border-radius:8px; padding:0.65rem 1rem; margin-top:1.5rem; font-size:0.68rem; color:#64748B; text-align:center; }
.stButton>button[kind="primary"]{background:#003366 !important;border:none !important;border-radius:8px !important;font-weight:600 !important;}
.approve-btn>button{background:#16A34A !important;color:white !important;border:none !important;border-radius:6px !important;}
.reject-btn>button{background:#DC2626 !important;color:white !important;border:none !important;border-radius:6px !important;}
#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
</style>

<script>
(function forceSidebarOpen(){
    function expand(){
        try{
            var doc=window.parent.document;
            var sb=doc.querySelector('[data-testid="stSidebar"]');
            if(sb){
                sb.style.display='block'; sb.style.visibility='visible';
                sb.style.transform='none'; sb.style.width='18rem';
                sb.style.minWidth='18rem'; sb.setAttribute('aria-expanded','true');
            }
            var btn=doc.querySelector('button[data-testid="collapsedControl"]');
            if(btn) btn.style.display='none';
        }catch(e){}
    }
    expand(); setInterval(expand,400);
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import database as db
import ai_agent as ai
import auth
from translations import t
from agent_compliance   import run_compliance_check, format_compliance_for_display
from agent_notify       import (notify_registration, notify_approved, notify_rejected,
                                 notify_leave, notify_employer_leave,
                                 notify_extra_hours, notify_high_risk)
from agent_orchestrator import (LeaveRequestOrchestrator, ExtraHoursOrchestrator)

db.init_db()
auth.init_auth_tables()

_leave_orch = LeaveRequestOrchestrator()
_eh_orch    = ExtraHoursOrchestrator()

# ─────────────────────────────────────────────
# SESSION DEFAULTS
# ─────────────────────────────────────────────
_DEFAULTS = {
    "logged_in":       False,
    "current_user":    None,
    "login_step":      "phone",   # phone | otp | done
    "login_phone":     "",
    "demo_otp":        "",
    "signup_success":  False,
    "extraction_done": False,
    "aadhaar_data":    None,
    "last_audit":      {},
    "last_routing":    "",
    "last_compliance": {},
    "pt_result":       None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# SIDEBAR — always shows all 3 roles
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:0.9rem 0 1rem;">
            <div style="font-size:2.1rem;">🏛️</div>
            <div style="font-size:0.93rem;font-weight:700;color:white;margin-top:0.3rem;">Gujarat Sarkar</div>
            <div style="font-size:0.7rem;color:#90A8C0;margin-top:0.12rem;">Shram &amp; Rojgar Vibhag</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        lang = st.selectbox("🌐 ભાષા / Language",
                            ["Gujarati","Hindi","English"], key="language", index=0)
        st.divider()

        # ── ALWAYS show all 3 role options ──
        role_options = {
            t("worker_portal",   lang): "worker",
            t("admin_portal",    lang): "admin",
            t("employer_portal", lang): "employer",
        }
        selected_label = st.selectbox(
            t("select_role", lang),
            list(role_options.keys()),
            key="role_label"
        )
        role = role_options[selected_label]

        st.divider()

        # ── Show logged-in user badge OR login hint ──
        if st.session_state["logged_in"] and st.session_state["current_user"]:
            user       = st.session_state["current_user"]
            role_label = "Government Officer" if user["role"] == "admin" else "Employer"
            st.markdown(f"""
            <div class="user-badge">
                <div class="ub-name">👤 {user['name']}</div>
                <div class="ub-phone">📱 +91 {user['phone']}</div>
                <div class="ub-role">✓ {role_label} — Logged in</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Logout", key="logout_btn"):
                for k in ["logged_in","current_user","login_step","login_phone","demo_otp"]:
                    st.session_state[k] = _DEFAULTS[k]
                st.rerun()
        else:
            if role in ("admin", "employer"):
                role_name = "Government Officer" if role == "admin" else "Employer"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);
                     border-radius:8px;padding:0.55rem 0.7rem;font-size:0.72rem;color:#B8C8D8;">
                    🔐 {role_name} portal requires login.<br>
                    Enter your phone below to continue.
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        <div style="font-size:0.67rem;color:#90A8C0;line-height:2;margin-bottom:0.5rem;">
            <div style="color:#FFB347;font-weight:600;margin-bottom:0.15rem;">Multi-Agent System</div>
            <div>&#9312; Orchestrator agent</div>
            <div>&#9313; Compliance agent</div>
            <div>&#9314; Notification agent</div>
            <div style="margin-top:0.2rem;color:#7FBA00;">&#10003; All agents active</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        st.markdown("""
        <div style="font-size:0.67rem;color:#90A8C0;line-height:1.9;">
            <div>&#128274; DPDP Act 2023</div>
            <div>&#128203; UIDAI Guidelines</div>
            <div>&#9878;&#65039; Labour Code 2020</div>
            <div>&#128737;&#65039; IT Act Section 43A</div>
        </div>
        """, unsafe_allow_html=True)

    return lang, role


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

def render_header(lang: str):
    st.markdown(f"""
    <div class="guj-header">
        <div style="font-size:2.1rem;">🏛️</div>
        <div>
            <h1>{t("app_title", lang)}</h1>
            <p>Gujarat Sarkar · Shram &amp; Rojgar Vibhag · Ahmedabad</p>
        </div>
        <div style="margin-left:auto;text-align:right;">
            <div style="color:#90A8C0;font-size:0.7rem;">v4.1 · OTP Auth</div>
            <div style="color:#FF9944;font-size:0.7rem;margin-top:0.15rem;">
                {datetime.now().strftime("%d %b %Y")}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOGIN SCREEN — shown inline in main area
# ─────────────────────────────────────────────

def render_login_screen(role: str, lang: str):
    """
    Shown in the MAIN AREA when Admin or Employer is selected but not logged in.
    Two tabs: Login (OTP) and Sign Up.
    """
    role_name = "Government Officer (Admin)" if role == "admin" else "Employer"
    role_icon = "🏛️" if role == "admin" else "🏢"

    st.markdown(f"""
    <div class="lock-banner">
        <div class="lb-icon">{role_icon} 🔐</div>
        <div class="lb-title">{role_name} Portal — Login Required</div>
        <div class="lb-sub">Enter your registered phone number to receive an OTP</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login with OTP", "📝 Sign Up"])

    # ── LOGIN TAB ──
    with tab_login:
        col_center, _, _ = st.columns([1.2, 0.4, 0.4])
        with col_center:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h2>Login</h2><p>Phone OTP — no password needed</p>", unsafe_allow_html=True)

            # Demo accounts hint
            st.markdown("""
            <div class="demo-accounts">
                <strong style="color:#003366;">Demo accounts:</strong><br>
                <span style="color:#1D4ED8;">Admin:</span> 9000000001 &nbsp;|&nbsp; 9000000002<br>
                <span style="color:#92400E;">Employer:</span> 9000000003 &nbsp;|&nbsp; 9000000004
            </div>
            """, unsafe_allow_html=True)

            if st.session_state["login_step"] == "phone":
                phone = st.text_input("📱 Mobile Number", placeholder="10-digit number",
                                       max_chars=10, key="login_phone_input")
                if st.button("Send OTP →", type="primary", key="send_otp_btn", use_container_width=True):
                    if not phone or len(phone) != 10 or not phone.isdigit():
                        st.error("Please enter a valid 10-digit number.")
                    else:
                        otp, is_registered = auth.generate_otp(phone)
                        if not is_registered:
                            st.error("Phone not registered. Use Sign Up tab to create an account.")
                        else:
                            user = auth.get_user_by_phone(phone)
                            if user and user["role"] != role:
                                st.error(f"This number is registered as {user['role']}, not {role}. Use the correct portal.")
                            else:
                                auth.send_otp_sms(phone, otp)
                                st.session_state["login_phone"] = phone
                                st.session_state["demo_otp"]    = otp
                                st.session_state["login_step"]  = "otp"
                                st.rerun()

            elif st.session_state["login_step"] == "otp":
                phone   = st.session_state["login_phone"]
                demo_otp = st.session_state.get("demo_otp", "")
                st.markdown(f"OTP sent to **+91 {phone}**")

                if demo_otp:
                    st.markdown(f"""
                    <div class="otp-box">
                        <div class="otp-label">Your OTP (demo — shown on screen)</div>
                        <div class="otp-code">{demo_otp}</div>
                        <div class="otp-sub">Valid 10 min · Max 3 attempts</div>
                    </div>
                    """, unsafe_allow_html=True)

                otp_input = st.text_input("Enter 6-digit OTP", max_chars=6,
                                           placeholder="------", key="otp_field")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Verify OTP", type="primary", key="verify_btn", use_container_width=True):
                        if not otp_input or len(otp_input) != 6:
                            st.error("Enter the 6-digit OTP.")
                        else:
                            result = auth.verify_otp(phone, otp_input)
                            if result["success"]:
                                st.session_state["logged_in"]    = True
                                st.session_state["current_user"] = result["user"]
                                st.session_state["login_step"]   = "phone"
                                st.session_state["demo_otp"]     = ""
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])
                with c2:
                    if st.button("← Change Number", key="back_btn", use_container_width=True):
                        st.session_state["login_step"] = "phone"
                        st.session_state["demo_otp"]   = ""
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # ── SIGN UP TAB ──
    with tab_signup:
        col_center, _, _ = st.columns([1.2, 0.4, 0.4])
        with col_center:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h2>Create Account</h2><p>Register as Officer or Employer</p>",
                        unsafe_allow_html=True)

            su_name  = st.text_input("Full Name", placeholder="Your full name", key="su_name")
            su_phone = st.text_input("Mobile Number", placeholder="10-digit number",
                                      max_chars=10, key="su_phone")
            su_role  = st.selectbox("Role",
                                     ["admin", "employer"],
                                     format_func=lambda x: "Government Officer (Admin)" if x == "admin"
                                                 else "Employer / Business Owner",
                                     index=0 if role == "admin" else 1,
                                     key="su_role")

            if su_role == "admin":
                st.markdown("""
                <div style="background:#FEF3C7;border:1px solid #FCD34D;border-radius:8px;
                     padding:0.55rem 0.75rem;font-size:0.76rem;color:#92400E;margin:0.5rem 0;">
                    ⚠️ Admin accounts are for licensed Government Officers only.
                </div>
                """, unsafe_allow_html=True)

            if st.button("Create Account →", type="primary", key="signup_btn", use_container_width=True):
                result = auth.register_user(su_phone, su_name, su_role)
                if result["success"]:
                    st.success(result["message"] + " → Go to Login tab.")
                else:
                    st.error(result["message"])

            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AGENT HELPERS
# ─────────────────────────────────────────────

def render_agent_chain_cards(aadhaar_data, checks):
    st.markdown("""
    <div style="background:#F0F4FF;border:1px solid #C7D2FE;border-radius:10px;
         padding:0.65rem 0.9rem;margin:0.7rem 0;">
        <div style="font-weight:700;color:#3730A3;font-size:0.85rem;margin-bottom:0.15rem;">
            &#128279; 3-Step AI Agent Chain
        </div>
        <div style="font-size:0.74rem;color:#4338CA;">
            Step 1 Extract &rarr; Step 2 Audit &rarr; Step 3 Route
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.markdown("""
        <div class="agent-step">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.45rem;">
                <span style="font-weight:600;font-size:0.83rem;">&#9312; Extract</span>
                <span style="background:#DCFCE7;color:#15803D;font-size:0.66rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:600;">DONE</span>
            </div>
            <div style="font-size:0.71rem;color:#64748B;line-height:2;">
                <div>Gemini 2.0 Flash Vision</div>
                <div>Strict JSON output</div>
                <div>Pydantic validation</div>
                <div>DPDP: image deleted</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        with st.spinner("Auditing..."):
            audit = ai.run_confidence_audit(aadhaar_data)
        score    = audit.get("overall_score", 0)
        concerns = audit.get("concerns", "None detected")
        fscores  = audit.get("field_scores", {})
        bar_col  = "#16A34A" if score >= 80 else "#D97706" if score >= 60 else "#DC2626"
        fpills   = "".join([
            f'<div style="background:#F1F5F9;padding:0.22rem 0.45rem;border-radius:4px;font-size:0.68rem;color:#334155;">'
            f'{k.replace("_"," ").title()}: <b>{v}</b></div>'
            for k, v in fscores.items()
        ])
        st.markdown(f"""
        <div class="agent-step">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <span style="font-weight:600;font-size:0.83rem;">&#9313; Audit</span>
                <span style="font-size:1.2rem;font-weight:800;color:{bar_col};">{score}/100</span>
            </div>
            <div style="background:#E2E8F0;border-radius:4px;height:5px;margin-bottom:0.45rem;">
                <div style="width:{score}%;background:{bar_col};height:5px;border-radius:4px;"></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.25rem;margin-bottom:0.4rem;">{fpills}</div>
            <div style="font-size:0.68rem;color:#64748B;">&#9888; {concerns}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        rec  = audit.get("recommendation", "MANUAL_REVIEW_REQUIRED")
        risk = checks.get("risk_score", "Low")
        if rec == "AUTO_APPROVE" and risk == "Low":
            bg, fg, rl, rd = "#DCFCE7","#15803D","AUTO APPROVE","Score≥80, no flags"
        elif rec == "REJECT" or risk == "High":
            bg, fg, rl, rd = "#FEE2E2","#991B1B","FLAG FOR REVIEW","Risk flags detected"
        else:
            bg, fg, rl, rd = "#FEF3C7","#92400E","MANUAL REVIEW","Score<80 or anomaly"
        st.markdown(f"""
        <div class="agent-step">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <span style="font-weight:600;font-size:0.83rem;">&#9314; Route</span>
                <span style="background:#E0E7FF;color:#3730A3;font-size:0.66rem;padding:0.15rem 0.4rem;border-radius:4px;font-weight:600;">DECIDED</span>
            </div>
            <div style="margin:0.45rem 0;">
                <span style="background:{bg};color:{fg};padding:0.22rem 0.55rem;border-radius:6px;font-size:0.7rem;font-weight:600;">{rl}</span>
            </div>
            <div style="font-size:0.68rem;color:#64748B;line-height:1.7;"><div>{rd}</div><div>Risk: <strong>{risk}</strong></div></div>
            <div style="font-size:0.66rem;color:#94A3B8;margin-top:0.35rem;border-top:1px solid #F1F5F9;padding-top:0.28rem;">
                Officer makes final decision
            </div>
        </div>
        """, unsafe_allow_html=True)

    return audit, rec


def render_compliance_panel(worker_dict: dict):
    with st.spinner("Compliance agent checking 4 laws..."):
        result = run_compliance_check(worker_dict)
    rows      = format_compliance_for_display(result)
    clearance = result.get("overall_clearance", "REVIEW")
    summary   = result.get("summary", "—")
    cl_css    = {"CLEAR":"clearance-clear","REVIEW":"clearance-review","BLOCK":"clearance-block"}.get(clearance,"clearance-review")
    row_html  = "".join([
        f'<div class="compliance-row"><span>{r["law"]}</span>'
        f'<span class="{"c-pass" if r["status"]=="PASS" else "c-fail"}">{r["status"]}</span></div>'
        for r in rows
    ])
    st.markdown(f"""
    <div class="compliance-panel">
        <div style="font-weight:700;font-size:0.82rem;color:#15803D;margin-bottom:0.5rem;">
            &#9878;&#65039; Compliance Agent — Legal Check
        </div>
        {row_html}
        <div style="margin-top:0.5rem;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.75rem;color:#374151;">{summary}</span>
            <span style="padding:0.2rem 0.6rem;border-radius:6px;font-size:0.72rem;font-weight:700;" class="{cl_css}">{clearance}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return result


def render_notify_panel(message: str, label: str = "Notification Agent"):
    st.markdown(f"""
    <div class="notify-panel">
        <strong>&#128276; {label}</strong>{message}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 1: WORKER PORTAL — no login needed
# ─────────────────────────────────────────────

def render_worker_portal(lang: str):
    st.markdown(f"### {t('worker_title', lang)}")
    st.markdown(f"<p style='color:#64748B;margin-top:-0.8rem;'>{t('worker_subtitle', lang)}</p>",
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"📝 {t('worker_title', lang)}", f"🗓️ {t('holiday_title', lang)}"])

    with tab1:
        col1, col2 = st.columns([1,1], gap="large")

        with col1:
            st.markdown(f'<div class="section-card"><h3>📄 {t("upload_aadhaar", lang)}</h3>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(t("upload_aadhaar", lang), type=["jpg","jpeg","png"],
                                              key="aadhaar_upload", label_visibility="collapsed")
            st.caption(t("upload_hint", lang))
            if uploaded_file:
                st.image(Image.open(uploaded_file), caption="Uploaded Aadhaar Card", use_column_width=True)
                if st.button(f"🔍 {t('extracting', lang)}", type="primary", key="extract_btn"):
                    with st.spinner(t("extracting", lang)):
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()
                        aadhaar_data, msg = ai.extract_aadhaar_data(image_bytes)
                        del image_bytes
                        if aadhaar_data:
                            st.session_state["aadhaar_data"]    = aadhaar_data
                            st.session_state["extraction_done"] = True
                            st.success(msg)
                        else:
                            st.error(msg)
                            st.session_state["extraction_done"] = False
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card"><h3>📋 Registration Details</h3>', unsafe_allow_html=True)

            if st.session_state.get("extraction_done") and st.session_state.get("aadhaar_data"):
                aadhaar = st.session_state["aadhaar_data"]
                st.markdown(f"<div class='info-box'>✅ {t('verify_details', lang)}</div>", unsafe_allow_html=True)
                st.markdown("")
                ca, cb = st.columns(2)
                with ca:
                    st.metric(t("extracted_name",    lang), aadhaar.full_name or "—")
                    st.metric(t("extracted_dob",     lang), aadhaar.date_of_birth or "—")
                with cb:
                    st.metric(t("extracted_aadhaar", lang), db.mask_aadhaar(aadhaar.aadhaar_number) if aadhaar.aadhaar_number else "—")
                    st.metric(t("extracted_gender",  lang), aadhaar.gender or "—")

                checks = ai.run_deterministic_checks(aadhaar)
                if checks["risk_score"] == "High":
                    st.markdown(f'<div class="risk-high"><p>🚨 <b>High Risk:</b> {checks["notes"]}</p></div>', unsafe_allow_html=True)
                elif checks["risk_score"] == "Medium":
                    st.warning(f"⚠️ {checks['notes']}")

                st.divider()
                audit, routing = render_agent_chain_cards(aadhaar, checks)
                st.session_state["last_audit"]   = audit
                st.session_state["last_routing"] = routing
                st.divider()

                mock_w = {"full_name": aadhaar.full_name, "date_of_birth": aadhaar.date_of_birth,
                          "consent_given": 1, "status": "Pending"}
                compliance_result = render_compliance_panel(mock_w)
                st.session_state["last_compliance"] = compliance_result
                st.divider()

                phone   = st.text_input(t("phone_number", lang), placeholder=t("phone_hint", lang), max_chars=10)
                address = st.text_area(t("address", lang), placeholder=t("address_hint", lang), height=70)
                consent = st.checkbox(t("consent_checkbox", lang), key="consent")
                if not consent:
                    st.caption(t("consent_required", lang))

                if st.button(f"📤 {t('submit', lang)}", type="primary", key="submit_reg", disabled=not consent):
                    if not phone or len(phone) != 10 or not phone.isdigit():
                        st.error("Please enter a valid 10-digit mobile number.")
                    elif not address:
                        st.error("Please enter your current address.")
                    else:
                        score     = st.session_state.get("last_audit",{}).get("overall_score","N/A")
                        clearance = st.session_state.get("last_compliance",{}).get("overall_clearance","REVIEW")
                        notes     = f"{checks['notes']} | Confidence:{score}/100 | Routing:{routing} | Legal:{clearance}"
                        with st.spinner("Submitting..."):
                            ref_id = db.add_worker(
                                full_name=aadhaar.full_name, date_of_birth=aadhaar.date_of_birth,
                                gender=aadhaar.gender or "Not specified",
                                aadhaar_number=aadhaar.aadhaar_number,
                                phone=phone, address=address, language=lang,
                                ai_risk_score=checks["risk_score"], ai_notes=notes,
                            )
                        worker_obj = {"full_name": aadhaar.full_name, "ref_id": ref_id}
                        render_notify_panel(notify_registration(worker_obj, lang), "Registration Notification")
                        if checks["risk_score"] == "High":
                            render_notify_panel(notify_high_risk(worker_obj, checks.get("notes","")[:60], lang), "High Risk Alert")
                        st.success(t("registration_success", lang, ref_id=ref_id))
                        st.info(t("registration_pending", lang))
                        st.session_state["extraction_done"] = False
                        st.session_state["aadhaar_data"]    = None
                        st.markdown(f"""
                        <div style="background:#F0FDF4;border:2px solid #22C55E;border-radius:10px;
                             padding:1rem;text-align:center;margin-top:0.8rem;">
                            <div style="font-size:0.76rem;color:#16A34A;">Registration Reference</div>
                            <div style="font-size:1.5rem;font-weight:800;color:#15803D;
                                 font-family:monospace;letter-spacing:0.1em;">{ref_id}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:2.5rem 1rem;color:#94A3B8;">
                    <div style="font-size:2.8rem;">📋</div>
                    <div style="margin-top:0.4rem;font-size:0.86rem;">
                        Upload your Aadhaar card — AI agents extract, audit, and check compliance automatically
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card"><h3>🗓️ Log Leave or Absence</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1,1], gap="large")
        with c1:
            ref_input    = st.text_input("Your Registration Reference ID", placeholder="e.g., GJ-2025-DEMO001")
            leave_date   = st.date_input(t("holiday_date", lang), value=date.today()+timedelta(days=1), min_value=date.today())
            leave_reason = st.text_input(t("holiday_reason", lang), placeholder="Festival, doctor appointment...")
            notify_emp   = st.checkbox(t("notify_employer", lang), value=True)
            if st.button(f"📅 {t('submit', lang)}", type="primary", key="log_leave_btn"):
                if not ref_input:
                    st.error("Please enter your Registration ID")
                elif not leave_reason:
                    st.error("Please enter a reason for leave")
                else:
                    worker = db.get_worker_by_ref(ref_input.strip())
                    if not worker:
                        st.error("Registration ID not found.")
                    else:
                        leave_result = _leave_orch.run_leave_pipeline(
                            worker=worker, leave_date=leave_date.strftime("%Y-%m-%d"),
                            reason=leave_reason, notify_employer=notify_emp, language=lang)
                        db.log_leave(ref_input.strip(), leave_date.strftime("%Y-%m-%d"), leave_reason, notify_emp)
                        st.success(t("holiday_logged", lang))
                        render_notify_panel(leave_result["worker_msg"], "Worker Notification")
                        if leave_result.get("employer_msg"):
                            render_notify_panel(leave_result["employer_msg"], "Employer Notification")
        with c2:
            if ref_input:
                worker = db.get_worker_by_ref(ref_input.strip())
                if worker:
                    st.markdown(f"**{t('worker_holidays', lang)} — {worker['full_name']}**")
                    for lv in db.get_leaves_for_worker(ref_input.strip())[:5]:
                        st.markdown(f"""
                        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;
                             padding:0.55rem 0.8rem;margin:0.3rem 0;font-size:0.8rem;">
                            <b>{lv['leave_date']}</b> — {lv['reason']}
                            {'<span style="color:#16A34A;font-size:0.7rem;"> ✓ Notified</span>' if lv["employer_notified"] else ""}
                        </div>
                        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MODULE 2: ADMIN PORTAL
# ─────────────────────────────────────────────

def render_admin_portal(lang: str):
    officer_id   = st.session_state["current_user"]["phone"]
    officer_name = st.session_state["current_user"]["name"]

    st.markdown(f"### {t('admin_title', lang)}")
    st.markdown(f"<p style='color:#64748B;margin-top:-0.8rem;'>"
                f"Logged in as <strong>{officer_name}</strong> · Officer ID: <code>{officer_id}</code></p>",
                unsafe_allow_html=True)
    st.divider()

    stats = db.get_dashboard_stats()
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="metric-value metric-blue">{stats['total']}</div><div class="metric-label">{t('total_registered', lang)}</div></div>
        <div class="metric-card"><div class="metric-value metric-orange">{stats['pending']}</div><div class="metric-label">{t('pending_verification', lang)}</div></div>
        <div class="metric-card"><div class="metric-value metric-green">{stats['approved']}</div><div class="metric-label">{t('approved', lang)}</div></div>
        <div class="metric-card"><div class="metric-value metric-red">{stats['rejected']}</div><div class="metric-label">{t('rejected', lang)}</div></div>
    </div>
    """, unsafe_allow_html=True)

    tab_p, tab_a, tab_log, tab_users, tab_pm = st.tabs([
        f"⏳ Pending ({stats['pending']})", "📋 All Workers",
        "📝 Audit Log", "👥 Users", "🔧 Prompts"
    ])

    with tab_p:
        pending = db.get_all_workers(status_filter="Pending")
        if not pending:
            st.success(t("no_pending", lang))
        else:
            for w in pending:
                risk_bg = "#FEF3C7" if w["ai_risk_score"]=="High" else "#DBEAFE"
                risk_fg = "#92400E" if w["ai_risk_score"]=="High" else "#1D4ED8"
                st.markdown(f"""
                <div class="worker-profile">
                    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.4rem;">
                        <div><div class="worker-name">{w['full_name']}</div>
                            <div class="worker-id">Ref: {w['ref_id']} · {w['submitted_at'][:10]}</div></div>
                        <span style="background:{risk_bg};color:{risk_fg};padding:0.18rem 0.55rem;border-radius:999px;font-size:0.71rem;font-weight:600;">
                            AI Risk: {w['ai_risk_score']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                dc, ac = st.columns([2,1], gap="large")
                with dc:
                    ca, cb, cc = st.columns(3)
                    with ca: st.metric("DOB",    w["date_of_birth"] or "—")
                    with cb: st.metric("Gender", w["gender"]        or "—")
                    with cc: st.metric("Aadhaar",w["aadhaar_masked"] or "—")
                    st.markdown(f"📞 {w['phone'] or '—'} &nbsp; 📍 {w['address'] or '—'}")
                    if w.get("ai_notes"):
                        css = "risk-high" if w["ai_risk_score"]=="High" else "info-box"
                        p1  = "<p>" if css=="risk-high" else ""
                        p2  = "</p>" if css=="risk-high" else ""
                        st.markdown(f'<div class="{css}">{p1}🤖 <b>AI Notes:</b> {w["ai_notes"]}{p2}</div>', unsafe_allow_html=True)
                    with st.expander("⚖️ Run Compliance Check"):
                        render_compliance_panel({"full_name":w["full_name"],"date_of_birth":w["date_of_birth"],
                                                  "consent_given":w.get("consent_given",1),"status":w["status"]})
                with ac:
                    st.markdown("**Actions**")
                    st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                    if st.button(t("approve_btn", lang), key=f"apr_{w['ref_id']}"):
                        if db.approve_worker(w["ref_id"], officer_id):
                            amsg = notify_approved({"full_name":w["full_name"],"ref_id":w["ref_id"]}, w.get("language",lang))
                            st.success(t("approved_msg", lang, name=w["full_name"]))
                            render_notify_panel(amsg, "Approval Notification")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                    if st.button(t("reject_btn", lang), key=f"rej_{w['ref_id']}"):
                        st.session_state[f"rf_{w['ref_id']}"] = True

                    if st.session_state.get(f"rf_{w['ref_id']}"):
                        rreason = st.text_area(t("rejection_reason", lang), key=f"rr_{w['ref_id']}", height=70)
                        if rreason and st.button("🤖 Generate Notice", key=f"gn_{w['ref_id']}"):
                            with st.spinner("Drafting..."):
                                notice = ai.generate_rejection_notice(w["full_name"],w["ref_id"],rreason,w.get("language","Gujarati"))
                            st.text_area("📄 Notice", value=notice, height=120, key=f"nt_{w['ref_id']}")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
                            if st.button(t("confirm_rejection", lang), key=f"cr_{w['ref_id']}"):
                                rsn = st.session_state.get(f"rr_{w['ref_id']}", "")
                                if not rsn:
                                    st.error("Enter a rejection reason.")
                                elif db.reject_worker(w["ref_id"], officer_id, rsn):
                                    rmsg = notify_rejected({"full_name":w["full_name"],"ref_id":w["ref_id"]}, rsn, w.get("language",lang))
                                    st.warning(t("rejected_msg", lang, name=w["full_name"]))
                                    render_notify_panel(rmsg, "Rejection Notification")
                                    st.session_state[f"rf_{w['ref_id']}"] = False
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with cc2:
                            if st.button(t("cancel", lang), key=f"cn_{w['ref_id']}"):
                                st.session_state[f"rf_{w['ref_id']}"] = False
                                st.rerun()
                st.divider()

    with tab_a:
        sf = st.selectbox("Filter", ["All","Pending","Verified","Rejected"], key="admin_sf")
        all_w = db.get_all_workers(status_filter=None if sf=="All" else sf)
        if all_w:
            rows = []
            for w in all_w:
                si = {"Verified":"✅","Pending":"⏳","Rejected":"❌"}.get(w["status"],"—")
                ri = {"Low":"🟢","Medium":"🟡","High":"🔴"}.get(w["ai_risk_score"],"—")
                rows.append({"Ref ID":w["ref_id"],"Name":w["full_name"],"DOB":w["date_of_birth"] or "—",
                              "Aadhaar":w["aadhaar_masked"],"Status":f"{si} {w['status']}",
                              "Risk":f"{ri} {w['ai_risk_score']}","Submitted":w["submitted_at"][:10] if w["submitted_at"] else "—","Officer":w["officer_id"] or "—"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption(f"{len(all_w)} records")

    with tab_log:
        icons = {"APPROVE":"✅","REJECT":"❌","REGISTER":"📝","LEAVE_LOG":"🗓️"}
        for e in db.get_recent_audit_log(limit=20):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0.7rem;
                 border-bottom:1px solid #F1F5F9;font-size:0.81rem;">
                <span>{icons.get(e['action'],'📌')}</span>
                <div><b>{e['action']}</b>
                    <span style="color:#64748B;margin-left:0.35rem;">{e.get('worker_ref_id','—')}</span>
                    <span style="color:#94A3B8;font-size:0.7rem;margin-left:0.35rem;">by {e.get('performed_by','—')}</span>
                </div>
                <div style="margin-left:auto;color:#94A3B8;font-size:0.7rem;">
                    {e['performed_at'][:16] if e.get('performed_at') else '—'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_users:
        st.markdown("### Registered System Users")
        users = auth.get_all_users()
        if users:
            rows = [{"Name":u["name"],"Phone":u["phone"],
                     "Role":"🏛️ Admin" if u["role"]=="admin" else "🏢 Employer",
                     "Active":"✅" if u["is_active"] else "❌","Created":u["created_at"][:10]}
                    for u in users]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.divider()
        st.markdown("### Add New User")
        au_name  = st.text_input("Full Name", key="au_name")
        au_phone = st.text_input("Mobile Number", max_chars=10, key="au_phone")
        au_role  = st.selectbox("Role", ["admin","employer"],
                                 format_func=lambda x: "Government Officer" if x=="admin" else "Employer",
                                 key="au_role")
        if st.button("➕ Add User", type="primary", key="add_user_btn"):
            result = auth.register_user(au_phone, au_name, au_role)
            if result["success"]:
                st.success(result["message"]); st.rerun()
            else:
                st.error(result["message"])

    with tab_pm:
        st.markdown("### Prompt Engineering — Design Decisions")
        for title, prompt_text, decisions in [
            ("📄 Prompt 1 — Vision extraction", ai.EXTRACT_PROMPT,
             [("`ONLY valid JSON`","Prevents markdown wrapping"),("`null` for missing","Stops hallucination"),("Explicit example","Models follow examples better")]),
            ("🔍 Prompt 2 — Confidence auditor", ai.CONFIDENCE_PROMPT,
             [("Separate call","Honest evaluator mode"),("Per-field scores","Pinpoints weak fields"),("3-option enum","Forces single clear decision")]),
        ]:
            with st.expander(title):
                p1, p2 = st.columns([1,1], gap="large")
                with p1:
                    for d, r in decisions:
                        st.markdown(f'<div class="prompt-decision"><b>{d}</b> — {r}</div>', unsafe_allow_html=True)
                with p2:
                    st.code(prompt_text, language="text")


# ─────────────────────────────────────────────
# MODULE 3: EMPLOYER PORTAL
# ─────────────────────────────────────────────

def render_employer_portal(lang: str):
    emp_user = st.session_state["current_user"]
    st.markdown(f"### {t('employer_title', lang)}")
    st.markdown(f"<p style='color:#64748B;margin-top:-0.8rem;'>Logged in as <strong>{emp_user['name']}</strong></p>", unsafe_allow_html=True)

    employers      = db.get_all_employers()
    employer_names = {e["business_name"]: e for e in employers}
    if not employer_names:
        st.info("No employer businesses found.")
        return

    sel_emp = employer_names[st.selectbox("Select Your Business", list(employer_names.keys()), key="emp_sel")]
    st.divider()

    workers = db.get_workers_for_employer(sel_emp["id"])
    if not workers:
        st.info("No workers mapped to this employer yet.")
        return

    worker_names = {w["full_name"]: w for w in workers}
    sel_w = worker_names[st.selectbox(t("view_worker", lang), list(worker_names.keys()), key="emp_w_sel")]

    c1, c2 = st.columns([1,1], gap="large")
    with c1:
        st.markdown(f"""
        <div class="worker-profile">
            <div class="worker-name">{sel_w['full_name']}</div>
            <div class="worker-id">Ref: {sel_w['ref_id']}</div>
            <table style="width:100%;font-size:0.81rem;border-collapse:collapse;margin-top:0.65rem;">
                <tr><td style="color:#64748B;padding:0.22rem 0;">DOB</td><td style="font-weight:500;">{sel_w['date_of_birth'] or '—'}</td></tr>
                <tr><td style="color:#64748B;padding:0.22rem 0;">Aadhaar</td><td style="font-weight:500;font-family:monospace;">{sel_w['aadhaar_masked']}</td></tr>
                <tr><td style="color:#64748B;padding:0.22rem 0;">Phone</td><td style="font-weight:500;">{sel_w['phone'] or '—'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        if sel_w["status"] == "Verified":
            st.markdown(f"""
            <div class="verified-banner">
                <div class="v-text">✅ {t('verified_badge', lang)}</div>
                <div class="v-sub">Verified {sel_w.get('verified_at','—')[:10]} · Officer {sel_w.get('officer_id','—')}</div>
            </div>
            """, unsafe_allow_html=True)
        elif sel_w["status"] == "Pending":
            st.warning(t("not_verified", lang))
        else:
            st.error("❌ Registration Rejected")

        st.markdown(f"**{t('worker_holidays', lang)}**")
        upcoming = [lv for lv in db.get_leaves_for_worker(sel_w["ref_id"]) if lv["leave_date"] >= date.today().strftime("%Y-%m-%d")]
        for lv in upcoming[:3]:
            st.markdown(f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:6px;padding:0.42rem 0.65rem;margin:0.22rem 0;font-size:0.78rem;">📅 <b>{lv["leave_date"]}</b> — {lv["reason"]}</div>', unsafe_allow_html=True)
        if not upcoming:
            st.caption(t("no_holidays", lang))

    with c2:
        st.markdown(f'<div class="section-card"><h3>⏰ {t("request_extra_hours", lang)}</h3>', unsafe_allow_html=True)
        if sel_w["status"] != "Verified":
            st.warning("Worker must be verified before requesting extra hours.")
        else:
            nl = st.text_area("Natural language request:",
                              placeholder=f"Ask {sel_w['full_name'].split()[0]} to stay 2 hours late tomorrow for a party",
                              height=85, key="nl_req")
            if nl and st.button("🤖 Parse Request", key="parse_nl"):
                with st.spinner("Parsing..."):
                    eh_result = _eh_orch.run_extra_hours_pipeline(natural_language=nl, worker=sel_w, employer=sel_emp, language=lang)
                if not eh_result["allowed"]:
                    st.error(eh_result["message"])
                else:
                    st.success(eh_result["message"])
                    render_notify_panel(eh_result["notification"], "Extra Hours Notification")

            st.markdown("**Or enter manually:**")
            rdate = st.date_input(t("request_date",lang), value=date.today()+timedelta(days=1), min_value=date.today(), key="req_date")
            ehrs  = st.slider(t("extra_hours",lang), 1, 4, 2, key="extra_hrs")
            rrson = st.text_input(t("extra_hours_reason",lang), placeholder="House party...", key="req_rsn")
            total  = 8 + ehrs
            colour = "#16A34A" if total <= 9 else "#DC2626"
            st.markdown(f"""
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:0.55rem 0.85rem;font-size:0.78rem;margin:0.35rem 0;">
                ⚖️ <b>Labour Code 2020:</b> 8h + {ehrs}h = <span style="color:{colour};font-weight:700;">{total}h</span>
                {"✅ OK" if total<=9 else "❌ Exceeds 9h limit"}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"📤 {t('send_request',lang)}", type="primary", key="send_req", disabled=total>9):
                res = db.add_work_request(worker_ref_id=sel_w["ref_id"], employer_id=sel_emp["id"],
                                          request_date=rdate.strftime("%Y-%m-%d"),
                                          extra_hours=float(ehrs), reason=rrson or "Extra work")
                if res["allowed"]:
                    eh_n = notify_extra_hours({"full_name":sel_w["full_name"],"ref_id":sel_w["ref_id"]},
                                              sel_emp["business_name"],ehrs,rdate.strftime("%Y-%m-%d"),rrson or "Extra work",lang)
                    st.success(t("request_sent", lang))
                    render_notify_panel(eh_n, "Request Sent (Notify Agent)")
                else:
                    st.error(res["message"])
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

def render_footer():
    st.markdown("""
    <div class="compliance-footer">
        🔒 <b>Auth:</b> OTP Phone Login · Sessions in-memory &nbsp;|&nbsp;
        🤖 <b>Agents:</b> Orchestrator · Compliance · Notification &nbsp;|&nbsp;
        ⚖️ <b>Human-in-Loop:</b> Officer approval required &nbsp;|&nbsp;
        Gemini 2.0 Flash · Gujarat Sarkar v4.1
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN — fixed routing logic
# ─────────────────────────────────────────────

def main():
    lang, role = render_sidebar()
    render_header(lang)

    logged_in = st.session_state["logged_in"]
    user      = st.session_state.get("current_user")

    if role == "worker":
        # Worker portal — never requires login
        render_worker_portal(lang)

    elif role == "admin":
        if logged_in and user and user["role"] == "admin":
            # Logged in as admin — show admin portal
            render_admin_portal(lang)
        elif logged_in and user and user["role"] != "admin":
            # Logged in as wrong role
            st.warning(f"You are logged in as **{user['role']}**. Please logout and login with an admin account.")
        else:
            # Not logged in — show login screen
            render_login_screen("admin", lang)

    elif role == "employer":
        if logged_in and user and user["role"] == "employer":
            # Logged in as employer — show employer portal
            render_employer_portal(lang)
        elif logged_in and user and user["role"] != "employer":
            # Logged in as wrong role
            st.warning(f"You are logged in as **{user['role']}**. Please logout and login with an employer account.")
        else:
            # Not logged in — show login screen
            render_login_screen("employer", lang)

    render_footer()


if __name__ == "__main__":
    main()