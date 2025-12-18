# src/app.py
"""
SANZAD 1.0 main shell (dark‑blue, Profile-driven, Register + Login + Super Admin + Institution Management).

- Global layout, navigation, theming, and role/session handling.
- "Profile" on Home exposes both registration and login (4 roles).
- No module is usable until someone is logged in.
- Personalized top welcome: WELCOME <first-name>!.
- "About SANZAD" button at top opens About dialog.
- Super Admin: only Super Admin dashboard (no Wings).
- Institution: only Institution Management dashboard (no Wings, only management).
- Student / Teacher / Parent: full Wings navigation and modules.
"""

import importlib
from typing import List, Dict

import streamlit as st
import pandas as pd

from translations import t
from db import (
    init_db,
    create_user,
    add_institution_application,
    list_institutions,
    approve_institution_db,
    delete_institution_application,
    list_users,
    set_user_status,
    verify_login,
)

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="SANZAD 1.0 – Global Education OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAIN_LOGO_PATH = None
ICON_LOGO_PATH = None

if MAIN_LOGO_PATH or ICON_LOGO_PATH:
    st.logo(MAIN_LOGO_PATH or ICON_LOGO_PATH, icon_image=ICON_LOGO_PATH or MAIN_LOGO_PATH)

# -------------------------------------------------------------------
# GLOBAL CSS
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    body, .stApp {
        background:
            radial-gradient(circle at top left, #0f172a 0, #020617 35%, #020617 70%, #000000 100%),
            radial-gradient(circle at bottom right, rgba(16,185,129,0.12) 0, rgba(16,185,129,0.0) 55%);
        background-color: #020617;
        color: #e5e7eb;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
    }

    section[data-testid="stMain"] > div.block-container {
        padding-top: 4.6rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    header[data-testid="stHeader"] {
        background-color: transparent;
    }

    .szt-top-nav {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 100;
        backdrop-filter: blur(18px);
        background: linear-gradient(90deg,
                    rgba(15,23,42,0.98) 0%,
                    rgba(17,24,39,0.98) 40%,
                    rgba(30,64,175,0.98) 80%,
                    rgba(21,128,61,0.98) 100%);
        border-bottom: 1px solid rgba(59,130,246,0.9);
        padding: 0.6rem 1.8rem 0.7rem 1.8rem;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 14px 36px rgba(15,23,42,0.95);
    }
    .szt-top-left { display: flex; align-items: center; gap: 0.9rem; }
    .szt-logo-mark { display: flex; align-items: center; gap: 0.6rem; }
    .szt-logo-circle {
        height: 38px; width: 38px; border-radius: 999px;
        background: radial-gradient(circle at 25% 0, #38bdf8, #22c55e 45%, #0ea5e9 100%);
        display: flex; align-items: center; justify-content: center;
        color: #020617; font-size: 1.06rem; font-weight: 800;
        box-shadow: 0 16px 34px rgba(56,189,248,0.9);
    }
    .szt-logo-text-main {
        font-size: 1.05rem; font-weight: 720; letter-spacing: 0.16em;
        text-transform: uppercase; color: #e5e7eb;
    }
    .szt-logo-text-sub {
        font-size: 0.8rem; color: #bfdbfe; margin-top: -0.1rem;
    }

    .szt-top-center { display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; }
    .szt-top-pill {
        padding: 0.18rem 0.8rem; border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.85);
        color: #e5e7eb; font-size: 0.8rem; background: rgba(15,23,42,0.7);
    }
    .szt-top-tag-primary {
        border-color: rgba(56,189,248,0.95);
        color: #e0f2fe;
        background: linear-gradient(135deg, rgba(59,130,246,0.65), rgba(34,197,94,0.5));
    }
    .szt-top-right { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: #e5e7eb; }
    .szt-top-right span strong { color: #bfdbfe; }

    [data-testid="stSidebar"] {
        background: radial-gradient(circle at top, #020617 0, #020617 45%, #020617 100%);
        border-right: 1px solid #020617;
    }
    .szt-sidebar-section {
        padding: 0.4rem 0.6rem 0.9rem 0.6rem;
        border-radius: 0.9rem;
        background: rgba(15,23,42,0.96);
        border: 1px solid rgba(30,64,175,0.9);
        margin-bottom: 0.9rem;
        box-shadow: 0 14px 32px rgba(15,23,42,1);
    }
    .szt-sidebar-title {
        font-size: 0.78rem; text-transform: uppercase;
        letter-spacing: 0.16em; color: #93c5fd; margin-bottom: 0.35rem;
    }

    .szt-card {
        padding: 1.2rem 1.6rem;
        border-radius: 1rem;
        background: radial-gradient(circle at top left, #020617 0, #020617 55%, #020617 100%);
        border: 1px solid rgba(30,64,175,0.95);
        box-shadow: 0 20px 44px rgba(15,23,42,1);
        margin-bottom: 1.0rem;
        transition: transform 140ms ease-out, box-shadow 140ms ease-out,
                    border-color 140ms ease-out, background 140ms ease-out;
    }
    .szt-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 26px 64px rgba(15,23,42,1);
        border-color: rgba(56,189,248,0.95);
        background: radial-gradient(circle at top left, #020617 0, #020617 40%, #020617 100%);
    }

    h1, h2, h3, h4 {
        font-weight: 620; letter-spacing: 0.03em; color: #e5e7eb;
    }

    .stButton>button {
        border-radius: 999px; border: 1px solid #22c55e;
        background: linear-gradient(135deg, #22c55e, #38bdf8);
        color: #020617; padding: 0.4rem 1.35rem;
        font-weight: 600; font-size: 0.9rem;
        box-shadow: 0 12px 32px rgba(34,197,94,0.75);
        transition: transform 80ms ease-out, box-shadow 80ms ease-out,
                    background 80ms ease-out, border-color 80ms ease-out;
    }
    .stButton>button:hover {
        border-color: #4ade80;
        background: linear-gradient(135deg, #4ade80, #60a5fa);
        transform: translateY(-1px);
        box-shadow: 0 18px 48px rgba(37,99,235,1);
    }
    .stButton>button:active {
        transform: translateY(0px) scale(0.99);
        box-shadow: 0 10px 26px rgba(15,23,42,1);
    }

    .szt-footer {
        margin-top: 2rem; padding-top: 1rem;
        border-top: 1px solid #1f2937;
        text-align: center; font-size: 0.85rem; color: #9ca3af;
    }

    @media (max-width: 768px) {
        .szt-top-nav {
            padding: 0.5rem 1.0rem 0.65rem 1.0rem;
            flex-direction: column; align-items: flex-start; gap: 0.25rem;
        }
        .szt-logo-text-main { font-size: 0.98rem; }
        section[data-testid="stMain"] > div.block-container {
            padding-top: 4.9rem; padding-left: 0.75rem; padding-right: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# LANGUAGE OPTIONS
# -------------------------------------------------------------------
LANG_OPTIONS = {
    "English": "en",
    "Français": "fr",
    "Kiswahili": "sw",
}

# -------------------------------------------------------------------
# AUTH / ROLE HELPERS
# -------------------------------------------------------------------
def get_effective_role() -> str:
    if "current_user" in st.session_state and st.session_state["current_user"]:
        return st.session_state["current_user"].get("role", "Student")
    role = st.session_state.get("current_role", "Student")
    if st.session_state.get("is_super_admin"):
        return "Super Admin"
    return role


def is_authenticated() -> bool:
    return bool(st.session_state.get("current_user"))


def login_user_with_email(email: str, password: str):
    user = verify_login(email, password)
    if user is None:
        return None
    return {
        "id": user["id"],
        "user_code": user["user_code"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
        "institution_name": user.get("institution_name", ""),
        "status": user["status"],
    }

# -------------------------------------------------------------------
# TOP NAV + ABOUT
# -------------------------------------------------------------------
def show_top_nav():
    lang = st.session_state.get("lang", "en")
    lang_display = {"en": "English", "fr": "Français", "sw": "Kiswahili"}.get(lang, "English")

    st.markdown(
        f"""
        <div class="szt-top-nav">
          <div class="szt-top-left">
            <div class="szt-logo-mark">
              <div class="szt-logo-circle">SZ</div>
              <div>
                <div class="szt-logo-text-main">SANZAD&nbsp;1.0</div>
                <div class="szt-logo-text-sub">Smart Global Education OS</div>
              </div>
            </div>
          </div>
          <div class="szt-top-center">
            <span class="szt-top-pill szt-top-tag-primary">Live • Beta</span>
            <span class="szt-top-pill">Global • Multi‑Campus</span>
            <span class="szt-top-pill">AI‑ready</span>
          </div>
          <div class="szt-top-right">
            <span>Language: <strong>{lang_display}</strong></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("About SANZAD 1.0", width="medium")
def show_about_dialog():
    st.markdown(
        """
**Sanzad 1.0** is the first release in the Sanzad series, developed by **Zaddock Kipchirchir**.

This platform is designed to make life simpler and more efficient, offering tools and services
for students, professionals, and everyday users.

As part of the Sanzad series, this is just the beginning. Future releases—**Sanzad 1.5, 2.0,
and beyond**—will introduce upgraded features, new services, and expanded functionality,
including access to government and public services, making Sanzad a comprehensive digital
ecosystem for everyone.

Sanzad is not just an app; it is a growing platform that evolves with its users, aiming to make
daily tasks, learning, and civic engagement smarter, faster, and more connected.
        """
    )


def show_language_switcher():
    lang = st.session_state.get("lang", "en")
    with st.expander(t("language_button", lang)):
        choice = st.selectbox(
            "Select language",
            list(LANG_OPTIONS.keys()),
            index=list(LANG_OPTIONS.values()).index(lang)
            if lang in LANG_OPTIONS.values()
            else 0,
            key="lang_select",
        )
        new_lang = LANG_OPTIONS[choice]
        if new_lang != st.session_state["lang"]:
            st.session_state["lang"] = new_lang
            st.rerun()

# -------------------------------------------------------------------
# SUPER ADMIN DASHBOARD
# -------------------------------------------------------------------
def show_super_admin_dashboard():
    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.markdown("## Super Admin • SANZAD Control Center")
    st.caption(
        "Manage institutions, platform users, and high-level controls. "
        "Super Admin does not use student/teacher features here."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    tab_inst, tab_users = st.tabs(["🏫 Institutions", "👥 Platform users"])

    # ---------- Institutions ----------
    with tab_inst:
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)
        st.subheader("Institutions")

        status_filter = st.selectbox(
            "Filter by status",
            ["All", "pending", "approved"],
            index=0,
            key="sa_inst_status_filter",
        )
        search_text = st.text_input(
            "Search by name, country, or city",
            key="sa_inst_search",
        )

        raw_rows = list_institutions(
            status=None if status_filter == "All" else status_filter
        )

        cols = ["id", "name", "code", "status", "country", "city", "details"]
        df = pd.DataFrame(raw_rows, columns=cols)

        if search_text.strip():
            s = search_text.strip().lower()
            mask = (
                df["name"].str.lower().str.contains(s)
                | df["country"].fillna("").str.lower().str.contains(s)
                | df["city"].fillna("").str.lower().str.contains(s)
            )
            df = df[mask]

        st.dataframe(df, use_container_width=True)

        st.markdown("### Actions")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            inst_name_approve = st.text_input(
                "Institution name to approve / assign code", key="sa_inst_name_approve"
            )
            inst_code = st.text_input("Code (optional, leave blank to keep existing)", key="sa_inst_code")
            if st.button("Approve / update code", key="sa_btn_approve_inst"):
                if inst_name_approve.strip():
                    code_val = inst_code.strip() or None
                    approve_institution_db(inst_name_approve.strip(), code_val)
                    st.success("Institution updated.")
                    st.rerun()
                else:
                    st.error("Enter institution name.")
        with col_b:
            inst_name_delete = st.text_input(
                "Pending institution name to delete", key="sa_inst_name_delete"
            )
            if st.button("Delete pending application", key="sa_btn_delete_inst"):
                if inst_name_delete.strip():
                    delete_institution_application(inst_name_delete.strip())
                    st.success("Pending application deleted (if found).")
                    st.rerun()
                else:
                    st.error("Enter institution name.")
        with col_c:
            st.info(
                "To block all users of an institution, use the **Platform users** tab "
                "and filter by institution name, then block them."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Users ----------
    with tab_users:
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)
        st.subheader("All platform users")

        users: List[Dict] = list_users()
        df_users = pd.DataFrame(users)

        role_filter = st.multiselect(
            "Filter by role",
            options=sorted(df_users["role"].unique()),
            default=list(sorted(df_users["role"].unique())),
            key="sa_user_role_filter",
        )
        status_filter = st.multiselect(
            "Filter by status",
            options=sorted(df_users["status"].unique()),
            default=list(sorted(df_users["status"].unique())),
            key="sa_user_status_filter",
        )
        search_users = st.text_input(
            "Search by name, email, institution, or user code",
            key="sa_user_search",
        )

        if role_filter:
            df_users = df_users[df_users["role"].isin(role_filter)]
        if status_filter:
            df_users = df_users[df_users["status"].isin(status_filter)]

        if search_users.strip():
            s = search_users.strip().lower()
            mask = (
                df_users["full_name"].str.lower().str.contains(s)
                | df_users["email"].str.lower().str.contains(s)
                | df_users["institution_name"].fillna("").str.lower().str.contains(s)
                | df_users["user_code"].fillna("").str.lower().str.contains(s)
            )
            df_users = df_users[mask]

        st.dataframe(df_users, use_container_width=True)

        st.markdown("### Block / unblock user")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            user_id_block = st.number_input(
                "User ID to block",
                min_value=1,
                step=1,
                key="sa_user_id_block",
            )
            if st.button("Block user", key="sa_btn_block_user"):
                set_user_status(int(user_id_block), "blocked")
                st.success(f"User {int(user_id_block)} blocked.")
                st.rerun()
        with col_u2:
            user_id_unblock = st.number_input(
                "User ID to unblock",
                min_value=1,
                step=1,
                key="sa_user_id_unblock",
            )
            if st.button("Unblock user", key="sa_btn_unblock_user"):
                set_user_status(int(user_id_unblock), "active")
                st.success(f"User {int(user_id_unblock)} unblocked.")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# INSTITUTION MANAGEMENT DASHBOARD
# -------------------------------------------------------------------
def show_institution_dashboard():
    user = st.session_state.get("current_user") or {}
    institution_name = user.get("institution_name", "")

    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.markdown(f"## Institution Management • {institution_name or 'Unknown Institution'}")
    st.caption(
        "Manage departments, teachers, students, fees, and teacher debts for your institution. "
        "Teaching features like assignments are hidden for institution accounts."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Load all users then keep only this institution
    all_users = list_users()
    df = pd.DataFrame(all_users)
    df = df[df["institution_name"] == institution_name]

    # Treat student_id as a department label for now
    if "student_id" in df.columns:
        df["department"] = df["student_id"].fillna("").replace("", "No department")
    else:
        df["department"] = "No department"

    # Build department list
    depts = sorted(set(df["department"].tolist())) if not df.empty else []

    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.subheader("Departments Management")

    st.write(
        "Departments are currently derived from the **department / student_id** field of users. "
        "When you register teachers and students, use the same text label to group them into a department."
    )

    new_dept = st.text_input(
        "Add new department label (use this text when registering users)",
        key="inst_new_dept",
    )
    if st.button("Save department label (concept only)", key="inst_add_dept_btn"):
        if new_dept.strip():
            st.success(
                "Department label noted. Use this exact text in the department/student_id field "
                "when creating teachers and students."
            )
        else:
            st.error("Enter a department name.")

    dept_filter = st.selectbox(
        "Select department to manage",
        ["All departments"] + depts if depts else ["All departments"],
        key="inst_dept_filter",
    )

    search_text = st.text_input(
        "Search by teacher name, student name, or email",
        key="inst_search",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Filter by department
    df_filtered = df.copy()
    if dept_filter != "All departments":
        df_filtered = df_filtered[df_filtered["department"] == dept_filter]

    # Search filter
    if search_text.strip():
        s = search_text.strip().lower()
        mask = (
            df_filtered["full_name"].str.lower().str.contains(s)
            | df_filtered["email"].str.lower().str.contains(s)
        )
        df_filtered = df_filtered[mask]

    # Split into teachers and students
    df_teachers = df_filtered[df_filtered["role"] == "Teacher"].copy()
    df_students = df_filtered[df_filtered["role"] == "Student"].copy()

    # Placeholder columns for money + dates (until you add real tables)
    if "teacher_debt" not in df_teachers.columns:
        df_teachers["teacher_debt"] = 0.0
    if "fee_balance" not in df_students.columns:
        df_students["fee_balance"] = 0.0
    if "last_payment_date" not in df_students.columns:
        df_students["last_payment_date"] = ""

    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.subheader(
        f"Teachers and students — {dept_filter if dept_filter != 'All departments' else 'All departments'}"
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Teachers in department")
        if df_teachers.empty:
            st.info("No teachers found for this selection.")
        else:
            st.dataframe(
                df_teachers[
                    ["id", "full_name", "email", "role", "department", "teacher_debt"]
                ],
                use_container_width=True,
            )

    with col_right:
        st.markdown("### Students in department")
        if df_students.empty:
            st.info("No students found for this selection.")
        else:
            st.dataframe(
                df_students[
                    ["id", "full_name", "email", "student_id", "department", "fee_balance", "last_payment_date"]
                ],
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # Management tabs
    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.subheader("Management actions")

    tab_people, tab_fees, tab_debts = st.tabs(
        ["Teachers & Students", "Fee Management", "Teacher Debts"]
    )

    # --- Teachers & Students (add / remove / edit placeholders) ---
    with tab_people:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Remove user (placeholder)")
            user_id_remove = st.number_input(
                "User ID",
                min_value=1,
                step=1,
                key="inst_remove_user_id",
            )
            if st.button("Remove user", key="inst_remove_user_btn"):
                st.warning(
                    "Implement a delete_user(user_id) helper in db.py to actually remove users. "
                    "This button is a placeholder."
                )
        with c2:
            st.markdown("#### Edit user (placeholder)")
            st.info(
                "Later you can add an edit form that loads a user by ID and updates fields with UPDATE in db.py."
            )

    # --- Fee Management (per student, placeholder for real fee tables) ---
    with tab_fees:
        st.markdown("#### Fee balances and history (placeholder)")
        fee_student_id = st.number_input(
            "Student user ID",
            min_value=1,
            step=1,
            key="inst_fee_student_id",
        )
        new_balance = st.number_input(
            "New fee balance",
            min_value=0.0,
            step=10.0,
            key="inst_fee_new_balance",
        )
        if st.button("Save fee balance", key="inst_fee_update_btn"):
            st.warning(
                "Add real fee tables in db.py (e.g. student_fees, fee_payments) and update them here. "
                "This UI is already wired for that future logic."
            )

    # --- Teacher Debts (placeholder for real debts table) ---
    with tab_debts:
        st.markdown("#### Teacher debts (placeholder)")
        debt_teacher_id = st.number_input(
            "Teacher user ID",
            min_value=1,
            step=1,
            key="inst_debt_teacher_id",
        )
        new_debt = st.number_input(
            "Debt amount",
            min_value=0.0,
            step=10.0,
            key="inst_debt_amount",
        )
        if st.button("Save / mark debt", key="inst_debt_save_btn"):
            st.warning(
                "Create a teacher_debts table in db.py and update it here to store real amounts and statuses."
            )

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# HOME: PROFILE + PERSONALIZED WELCOME
# -------------------------------------------------------------------
def show_home(role: str, effective_role: str, lang: str):
    with st.container():
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)

        user = st.session_state.get("current_user")
        if user:
            raw_name = user.get("full_name", "").strip() or "Friend"
            first_name = raw_name.split()[0]
            st.markdown(
                f"""
                <div style="
                    font-size: 2.4rem;
                    font-weight: 800;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    color: #e5e7eb;
                    text-align: left;
                ">
                    WELCOME {first_name}!
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Your SANZAD 1.0 experience is now fully personalized.")
        else:
            st.title(t("app_title", lang))
            st.write(
                "SANZAD 1.0 is a unified operating system for students, teachers, "
                "institutions, and parents — built for smart campuses worldwide."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)
        top_col1, top_col2, top_col3 = st.columns([1, 1, 3])

        with top_col1:
            if st.button("Profile", key="profile_toggle"):
                st.session_state["show_profile_panel"] = not st.session_state["show_profile_panel"]

        with top_col2:
            mode = st.session_state["profile_mode"]
            new_mode = st.segmented_control(
                "Profile mode",
                options=["register", "login"],
                format_func=lambda x: "Register" if x == "register" else "Login",
                key="profile_mode",
            )
            if new_mode != mode:
                st.session_state["profile_reg_choice"] = None
                st.session_state["profile_login_choice"] = None

        with top_col3:
            if is_authenticated():
                u = st.session_state["current_user"]
                st.markdown(
                    f"**Profile:** {u.get('full_name','Sanzad User')} · Role: {u.get('role','Unknown')}"
                )
            else:
                st.markdown("Use **Register** or **Login** under Profile to access SANZAD services.")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["show_profile_panel"]:
        if st.session_state["profile_mode"] == "register":
            show_register_panel()
        else:
            show_login_panel()

# -------------------------------------------------------------------
# REGISTER PANEL
# -------------------------------------------------------------------
def show_register_panel():
    with st.container():
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)
        st.subheader("Create your SANZAD profile")

        col_a, col_b, col_c, col_d = st.columns(4)
        reg_choice = None
        with col_a:
            if st.button("Student", key="btn_reg_student"):
                reg_choice = "Student"
        with col_b:
            if st.button("Teacher", key="btn_reg_teacher"):
                reg_choice = "Teacher"
        with col_c:
            if st.button("Parent", key="btn_reg_parent"):
                reg_choice = "Parent"
        with col_d:
            if st.button("Institution", key="btn_reg_institution"):
                reg_choice = "Institution"

        if reg_choice:
            st.session_state["profile_reg_choice"] = reg_choice
        choice = st.session_state.get("profile_reg_choice")

        # ---------- Student ----------
        if choice == "Student":
            with st.form("student_reg_form"):
                st.subheader("Student registration")
                full_name = st.text_input("Full name")
                institution_name = st.text_input("Institution name (exact)")
                student_reg_no = st.text_input("Student registration / admission number")
                email = st.text_input("Email")
                phone = st.text_input("Phone (optional)")
                country = st.text_input("Country")
                city = st.text_input("City / Town")
                _ = st.text_input("Location details (optional, e.g. estate, building, room)")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Register as Student")

            if submitted:
                if not full_name.strip() or not email.strip() or not password:
                    st.error("Full name, email, and password are required.")
                else:
                    created = create_user(
                        full_name=full_name,
                        email=email,
                        raw_password=password,
                        role="Student",
                        phone=phone,
                        student_id="",  # can later hold department
                        institution_name=institution_name,
                        teacher_reg_no="",
                        student_reg_no=student_reg_no,
                    )
                    if created is None:
                        st.error("An account with this email already exists or could not be created.")
                    else:
                        st.session_state["current_user"] = {
                            "id": created["id"],
                            "user_code": created["user_code"],
                            "full_name": created["full_name"],
                            "email": created["email"],
                            "role": created["role"],
                            "institution_name": created["institution_name"],
                            "status": created["status"],
                        }
                        st.success("Student profile created and signed in.")
                        st.rerun()

        # ---------- Teacher ----------
        elif choice == "Teacher":
            with st.form("teacher_reg_form"):
                st.subheader("Teacher registration")
                full_name = st.text_input("Full name")
                institution_name = st.text_input("Institution name (exact)")
                teacher_reg_no = st.text_input("Teacher registration / staff number")
                email = st.text_input("Email")
                phone = st.text_input("Phone (optional)")
                country = st.text_input("Country")
                city = st.text_input("City / Town")
                _ = st.text_input("Location details (optional, e.g. estate, building, room)")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Register as Teacher")

            if submitted:
                if not full_name.strip() or not email.strip() or not password:
                    st.error("Full name, email, and password are required.")
                else:
                    created = create_user(
                        full_name=full_name,
                        email=email,
                        raw_password=password,
                        role="Teacher",
                        phone=phone,
                        student_id="",  # can later hold department
                        institution_name=institution_name,
                        teacher_reg_no=teacher_reg_no,
                        student_reg_no="",
                    )
                    if created is None:
                        st.error("An account with this email already exists or could not be created.")
                    else:
                        st.session_state["current_user"] = {
                            "id": created["id"],
                            "user_code": created["user_code"],
                            "full_name": created["full_name"],
                            "email": created["email"],
                            "role": created["role"],
                            "institution_name": created["institution_name"],
                            "status": created["status"],
                        }
                        st.success("Teacher profile created and signed in.")
                        st.rerun()

        # ---------- Parent ----------
        elif choice == "Parent":
            with st.form("parent_reg_form"):
                st.subheader("Parent / Guardian registration")
                full_name = st.text_input("Full name")
                institution_name = st.text_input("Child's institution name (exact)")
                child_name = st.text_input("Child's full name")
                child_reg_no = st.text_input("Child's registration / admission number")
                email = st.text_input("Email")
                phone = st.text_input("Phone (optional)")
                country = st.text_input("Country")
                city = st.text_input("City / Town")
                _ = st.text_input("Location details (optional, e.g. estate, building, room)")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Register as Parent")

            if submitted:
                if not full_name.strip() or not email.strip() or not password:
                    st.error("Full name, email, and password are required.")
                else:
                    created = create_user(
                        full_name=full_name,
                        email=email,
                        raw_password=password,
                        role="Parent",
                        phone=phone,
                        student_id="",
                        institution_name=institution_name,
                        teacher_reg_no="",
                        student_reg_no="",
                        parent_child_name=child_name,
                        parent_child_reg_no=child_reg_no,
                    )
                    if created is None:
                        st.error("An account with this email already exists or could not be created.")
                    else:
                        st.session_state["current_user"] = {
                            "id": created["id"],
                            "user_code": created["user_code"],
                            "full_name": created["full_name"],
                            "email": created["email"],
                            "role": created["role"],
                            "institution_name": created["institution_name"],
                            "status": created["status"],
                        }
                        st.success("Parent profile created and signed in.")
                        st.rerun()

        # ---------- Institution ----------
        elif choice == "Institution":
            with st.form("institution_reg_form"):
                st.subheader("Institution registration (application to Super Admin)")
                inst_name = st.text_input("Institution / organization name (exact)")
                country = st.text_input("Country")
                city = st.text_input("City / Town")
                details = st.text_area("Institution details (type, levels, notes)")
                contact_name = st.text_input("Contact person name")
                contact_email = st.text_input("Contact email")
                contact_phone = st.text_input("Contact phone")
                password = st.text_input("Password for institution account", type="password")
                submitted = st.form_submit_button("Submit institution application")

            if submitted:
                if not inst_name.strip() or not contact_email.strip() or not password:
                    st.error("Institution name, contact email, and password are required.")
                else:
                    add_institution_application(
                        name=inst_name.strip(),
                        country=country.strip(),
                        city=city.strip(),
                        details=f"{details}\nContact: {contact_name}, {contact_email}, {contact_phone}",
                    )
                    created = create_user(
                        full_name=inst_name.strip(),
                        email=contact_email,
                        raw_password=password,
                        role="Institution",
                        phone=contact_phone,
                        student_id="",
                        institution_name=inst_name.strip(),
                        teacher_reg_no="",
                        student_reg_no="",
                    )
                    if created is None:
                        st.error(
                            "Institution application saved, but the institution user account "
                            "could not be created (email may already exist)."
                        )
                    else:
                        st.session_state["current_user"] = {
                            "id": created["id"],
                            "user_code": created["user_code"],
                            "full_name": created["full_name"],
                            "email": created["email"],
                            "role": created["role"],
                            "institution_name": created["institution_name"],
                            "status": created["status"],
                        }
                        st.success(
                            "Institution application submitted and profile set. "
                            "Super Admin will review and approve it."
                        )
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# LOGIN PANEL
# -------------------------------------------------------------------
def show_login_panel():
    with st.container():
        st.markdown('<div class="szt-card">', unsafe_allow_html=True)
        st.subheader("Log into your SANZAD profile")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

        if submitted:
            user = login_user_with_email(email, password)
            if not user:
                st.error("Login failed. Check your email/password or account status.")
            else:
                st.session_state["current_user"] = user
                if user["role"] == "Super Admin":
                    st.session_state["is_super_admin"] = True
                st.success(f"Logged in as {user['full_name']} ({user['role']}).")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
def main():
    init_db()

    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    if "current_role" not in st.session_state:
        st.session_state["current_role"] = "Student"
    if "is_super_admin" not in st.session_state:
        st.session_state["is_super_admin"] = False
    if "current_module" not in st.session_state:
        st.session_state["current_module"] = "Home"
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None
    if "show_profile_panel" not in st.session_state:
        st.session_state["show_profile_panel"] = False
    if "profile_mode" not in st.session_state:
        st.session_state["profile_mode"] = "register"
    if "profile_reg_choice" not in st.session_state:
        st.session_state["profile_reg_choice"] = None
    if "profile_login_choice" not in st.session_state:
        st.session_state["profile_login_choice"] = None

    lang = st.session_state["lang"]

    show_top_nav()

    # About button row
    with st.container():
        col_about, _ = st.columns([1, 6])
        with col_about:
            if st.button("About SANZAD", key="about_sanzad_top"):
                show_about_dialog()

    show_language_switcher()

    # 1) Super Admin: ONLY Super Admin dashboard (no Wings)
    if st.session_state.get("is_super_admin"):
        show_super_admin_dashboard()
        st.markdown(
            '<div class="szt-footer">Sanzad 1.0 — Super Admin Console.</div>',
            unsafe_allow_html=True,
        )
        return

    # 2) Institution: ONLY Institution Management dashboard (no Wings)
    current_user = st.session_state.get("current_user")
    if current_user and current_user.get("role") == "Institution":
        show_institution_dashboard()
        st.markdown(
            '<div class="szt-footer">Sanzad 1.0 — Institution Management Console.</div>',
            unsafe_allow_html=True,
        )
        return

    # 3) Student / Teacher / Parent: normal sidebar + Wings
    with st.sidebar:
        st.markdown('<div class="szt-sidebar-section">', unsafe_allow_html=True)
        st.markdown("<div class='szt-sidebar-title'>Identity (view as)</div>", unsafe_allow_html=True)
        st.radio(
            "I am using SANZAD as:",
            ["Student", "Teacher", "Parent", "Institution"],
            key="current_role",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Super Admin unlock
        st.markdown('<div class="szt-sidebar-section">', unsafe_allow_html=True)
        st.markdown("<div class='szt-sidebar-title'>Super Admin</div>", unsafe_allow_html=True)
        with st.expander("Super Admin control (passcode)"):
            if not st.session_state["is_super_admin"]:
                admin_code = st.text_input("Enter Super Admin passcode", type="password")
                if st.button("Unlock Super Admin"):
                    if admin_code == "Sanzad2025!":
                        st.session_state["is_super_admin"] = True
                        st.success("Super Admin mode activated.")
                        st.rerun()
                    else:
                        st.error("Incorrect passcode.")
            else:
                st.success("Super Admin mode is ON.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Wings
        st.markdown('<div class="szt-sidebar-section">', unsafe_allow_html=True)
        st.markdown("<div class='szt-sidebar-title'>SANZAD Wings</div>", unsafe_allow_html=True)

        module_list = [
            "Home",
            "Sanzad Campus Hub",
            "Knowledge Hub",
            "Community Hub",
            "Gamification",
            "Analytics",
            "Career",
            "Innovation Lab",
            "Finance",
            "Wellbeing",
            "EnviroTech",
        ]

        icon_map = {
            "Home": "🏠",
            "Sanzad Campus Hub": "🎓",
            "Knowledge Hub": "📚",
            "Community Hub": "🌐",
            "Gamification": "🎯",
            "Analytics": "📊",
            "Career": "💼",
            "Innovation Lab": "🧪",
            "Finance": "💰",
            "Wellbeing": "🩺",
            "EnviroTech": "♻️",
        }

        label_to_module = {f"{icon_map[m]}  {m}": m for m in module_list}
        current_label = f"{icon_map[st.session_state['current_module']]}  {st.session_state['current_module']}"
        module_label = st.selectbox(
            "Navigation",
            list(label_to_module.keys()),
            index=list(label_to_module.keys()).index(current_label),
        )
        module = label_to_module[module_label]
        st.session_state["current_module"] = module

        st.markdown("</div>", unsafe_allow_html=True)

        # Session summary
        st.markdown('<div class="szt-sidebar-section">', unsafe_allow_html=True)
        st.markdown("<div class='szt-sidebar-title'>Session</div>", unsafe_allow_html=True)
        effective_role = get_effective_role()
        if is_authenticated():
            u = st.session_state["current_user"]
            st.write(f"Signed in as **{u.get('full_name','Sanzad User')}** ({effective_role})")
            if st.button("Sign out", key="btn_sign_out_sidebar"):
                st.session_state["current_user"] = None
                st.session_state["is_super_admin"] = False
                st.success("Signed out.")
                st.rerun()
        else:
            st.write(f"Not signed in • Viewing as **{effective_role}**")
            st.caption("Register or log in under Home → Profile before using services.")
        st.markdown("</div>", unsafe_allow_html=True)

    # MAIN body for Student / Teacher / Parent
    role = st.session_state["current_role"]
    effective_role = get_effective_role()

    module = st.session_state["current_module"]

    if module == "Home":
        show_home(role, effective_role, lang)
    else:
        if not is_authenticated():
            with st.container():
                st.markdown('<div class="szt-card">', unsafe_allow_html=True)
                st.markdown(f"#### {module}")
                st.warning(
                    "You must create or log into a SANZAD profile before accessing this service. "
                    "Go to **Home → Profile**, register or log in, and then return here."
                )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown('<div class="szt-card">', unsafe_allow_html=True)
                st.markdown(f"#### {module}")
                st.caption("Loaded as part of SANZAD 1.0 global platform shell.")
                st.markdown("</div>", unsafe_allow_html=True)

            module_map = {
                "Home": "modules.home",
                "Sanzad Campus Hub": "modules.campus_hub",
                "Knowledge Hub": "modules.knowledge_hub",
                "Community Hub": "modules.community_hub",
                "Gamification": "modules.gamification",
                "Analytics": "modules.analytics",
                "Career": "modules.career",
                "Innovation Lab": "modules.innovation_lab",
                "Finance": "modules.finance",
                "Wellbeing": "modules.wellbeing",
                "EnviroTech": "modules.envirotech",
            }

            if module in module_map:
                module_path = module_map[module]
                try:
                    imported_module = importlib.import_module(module_path)
                    if hasattr(imported_module, "render"):
                        imported_module.render(effective_role)
                    else:
                        st.warning(f"Module {module} loaded but has no render(role) function.")
                except ModuleNotFoundError:
                    st.warning(f"Module file for {module} not found yet.")
            else:
                st.info("Select a module from the sidebar.")

    st.markdown(
        '<div class="szt-footer">Sanzad 1.0 — The Future Begins Here.</div>',
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
