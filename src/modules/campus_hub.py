"""
SANZAD Campus Hub
=================

Future-ready digital campus environment integrated into SANZAD Core:

- Identity & Access (roles, institutions, users)
- Payments (SANZAD Pay: QR / Wallet / Cashless)
- Notifications & Messaging
- Analytics & Audit

This module is UI + orchestration only.
All critical business logic lives in SANZAD Core services.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any, List

import streamlit as st

# -------------------------------------------------------------------
# SANZAD CORE SERVICE CLIENTS (ASSUMED TO EXIST)
# -------------------------------------------------------------------
# These are *dependencies*, not re-implementations.
# In your real platform, point these imports to actual client modules.
try:
    from sanzad_core.identity import get_current_identity, require_role
    from sanzad_core.payments import (
        create_payment_request,
        get_payment_status,
        PaymentStatus,
    )
    from sanzad_core.notifications import send_notification, send_inbox_message
    from sanzad_core.analytics import log_event
except ImportError:
    # Light, no-op fallbacks so this module can still run in demo mode.
    class PaymentStatus:
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    def get_current_identity() -> Dict[str, Any]:
        # Demo identity for local testing
        return {
            "user_id": "demo-student-001",
            "full_name": "Demo Student",
            "role": "Student",
            "institution_id": "demo-inst-001",
        }

    def require_role(*_roles: str) -> bool:
        ident = get_current_identity()
        return ident.get("role") in _roles

    def create_payment_request(
        *,
        tenant_id: str,
        payer_id: str,
        amount: float,
        currency: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "payment_id": f"demo-pay-{int(datetime.utcnow().timestamp())}",
            "qr_url": "https://example.com/demo-qr",
            "amount": amount,
            "currency": currency,
            "description": description,
            "metadata": metadata or {},
        }

    def get_payment_status(payment_id: str) -> str:
        return PaymentStatus.SUCCESS

    def send_notification(
        *,
        tenant_id: str,
        user_ids: List[str],
        title: str,
        body: str,
        tags: Optional[List[str]] = None,
    ) -> None:
        pass

    def send_inbox_message(
        *,
        tenant_id: str,
        thread_key: str,
        sender_id: str,
        text: str,
    ) -> None:
        pass

    def log_event(
        *,
        tenant_id: str,
        actor_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass


# -------------------------------------------------------------------
# SIMPLE TYPES
# -------------------------------------------------------------------
@dataclass
class Identity:
    user_id: str
    full_name: str
    role: str
    institution_id: str


def _get_identity_from_core() -> Identity:
    raw = get_current_identity()
    return Identity(
        user_id=str(raw.get("user_id")),
        full_name=str(raw.get("full_name", "")),
        role=str(raw.get("role", "")),
        institution_id=str(raw.get("institution_id", "")),
    )


# -------------------------------------------------------------------
# SHARED UI HELPERS
# -------------------------------------------------------------------
def _role_badge(identity: Identity):
    st.markdown(
        f"<span style='padding:0.25rem 0.75rem; border-radius:999px; "
        f"background-color:#1f2937; color:#e5e7eb; font-size:0.8rem;'>"
        f"{identity.full_name} · {identity.role}</span>",
        unsafe_allow_html=True,
    )


def _section_card(title: str, description: str = ""):
    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.subheader(title)
    if description:
        st.caption(description)


def _info_pill(text: str):
    st.markdown(
        f"<span style='padding:0.1rem 0.6rem; border-radius:999px; "
        f"border:1px solid #4b5563; font-size:0.72rem; color:#e5e7eb;'>"
        f"{text}</span>",
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------
# MAIN ENTRY (CALLED BY SHELL)
# -------------------------------------------------------------------
def render(role: str, user: Dict[str, Any] | None = None):
    """
    Entry for SANZAD shell.

    `role` comes from shell (effective role).
    `user` can be the shell's user dict; identity is still resolved via SANZAD Identity.
    """
    identity = _get_identity_from_core()

    st.markdown("## 🎓 SANZAD Campus Hub")
    _role_badge(identity)
    st.caption(
        "Everything a student needs for learning, living, paying, and thriving — "
        "in one digital campus space."
    )

    # Multi-domain navigation
    main_tab = st.selectbox(
        "Choose a Campus Hub domain",
        [
            "1. Academic Life",
            "2. Campus Administration",
            "3. Campus Dining & Mess Hub",
            "4. Hostel & Accommodation Hub",
            "5. Campus Marketplace",
            "6. Work, Gigs & Attachments",
            "7. Wellbeing & Student Support",
            "8. Fees, Payments & Finance",
            "9. Digital ID & Access",
            "10. Communication & Community",
            "11. Analytics & Transparency",
        ],
        key="campushub_main_tab",
    )

    if main_tab == "1. Academic Life":
        ui_academic_life(identity)
    elif main_tab == "2. Campus Administration":
        ui_campus_admin(identity)
    elif main_tab == "3. Campus Dining & Mess Hub":
        ui_mess_hub(identity)
    elif main_tab == "4. Hostel & Accommodation Hub":
        ui_hostel_hub(identity)
    elif main_tab == "5. Campus Marketplace":
        ui_marketplace(identity)
    elif main_tab == "6. Work, Gigs & Attachments":
        ui_work_gigs(identity)
    elif main_tab == "7. Wellbeing & Student Support":
        ui_wellbeing(identity)
    elif main_tab == "8. Fees, Payments & Finance":
        ui_finance(identity)
    elif main_tab == "9. Digital ID & Access":
        ui_digital_id(identity)
    elif main_tab == "10. Communication & Community":
        ui_communication(identity)
    elif main_tab == "11. Analytics & Transparency":
        ui_analytics(identity)


# -------------------------------------------------------------------
# 1. ACADEMIC LIFE
# -------------------------------------------------------------------
def ui_academic_life(identity: Identity):
    _section_card(
        "Academic Life",
        "Courses, timetables, learning resources, attendance, grades, and lecturer announcements.",
    )

    tab = st.tabs(
        [
            "📚 Courses & Units",
            "🗓️ Timetables & Calendars",
            "📁 Learning Resources",
            "✅ Attendance",
            "📊 Grades & Transcripts",
            "📢 Announcements",
        ]
    )

    # 1. Courses & Units
    with tab[0]:
        st.markdown("### Course & Unit Enrollment")
        _info_pill("Backed by SANZAD Identity & Institution APIs")
        st.write("Demo: list courses pulled from SANZAD Core (placeholder).")
        st.text_input("Search course / unit", key="acad_search_course")
        st.button("Request enrollment (demo)", key="acad_enroll_btn")
        log_event(
            tenant_id=identity.institution_id,
            actor_id=identity.user_id,
            event_type="campus_hub.academic.view_courses",
            payload={},
        )

    # 2. Timetables & Calendars
    with tab[1]:
        st.markdown("### Timetables & Academic Calendars")
        st.date_input("Filter by date", key="acad_tt_date", value=date.today())
        st.info("Timetables are generated by SANZAD Academic core (placeholder).")

    # 3. Learning Resources
    with tab[2]:
        st.markdown("### Learning Resources")
        if identity.role in ("Lecturer", "Staff", "Institution Admin"):
            st.file_uploader(
                "Upload teaching resources (delegated to SANZAD Storage)",
                key="acad_res_upload",
            )
            st.button("Publish resource (demo)", key="acad_res_publish")
        st.info("Students see institution-scoped resources here (placeholder).")

    # 4. Attendance
    with tab[3]:
        st.markdown("### Smart Attendance")
        _info_pill("Linked with Digital ID & QR check-in")
        if identity.role in ("Lecturer", "Staff"):
            st.button("Generate attendance session QR (demo)", key="att_gen_qr")
        if identity.role == "Student":
            st.text_input("Enter/scan attendance token", key="att_token")
            st.button("Mark my attendance (demo)", key="att_mark_btn")

    # 5. Grades & Transcripts
    with tab[4]:
        st.markdown("### Grades & Transcripts")
        if identity.role == "Student":
            st.info("Transcript is fetched from SANZAD Academic core (placeholder).")
        elif identity.role in ("Lecturer", "Institution Admin"):
            st.text_input("Student ID / reg no", key="grades_stud_id")
            st.button("View / approve grades (demo)", key="grades_view_btn")

    # 6. Lecturer Announcements
    with tab[5]:
        st.markdown("### Lecturer Announcements")
        if identity.role in ("Lecturer", "Staff"):
            title = st.text_input("Announcement title", key="ann_title")
            body = st.text_area("Announcement body", key="ann_body")
            if st.button("Publish announcement (demo)", key="ann_publish_btn"):
                send_notification(
                    tenant_id=identity.institution_id,
                    user_ids=[],  # would be course participants
                    title=title,
                    body=body,
                    tags=["academic", "announcement"],
                )
                st.success("Announcement sent (demo).")
        else:
            st.info("Course announcements appear here (placeholder).")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 2. CAMPUS ADMINISTRATION
# -------------------------------------------------------------------
def ui_campus_admin(identity: Identity):
    _section_card(
        "Campus Administration",
        "Institution configuration, multi-campus support, policies, and notices.",
    )

    if identity.role not in ("Institution Admin", "SANZAD Super Admin"):
        st.info("Campus Administration is only visible to institution admins.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    tab = st.tabs(
        [
            "🏫 Institution Setup",
            "🌍 Multi-campus",
            "📅 Academic Calendars",
            "👥 Staff Roles",
            "📜 Policies & Notices",
        ]
    )

    with tab[0]:
        st.markdown("### Institution Configuration")
        st.text_input("Institution display name", key="admin_inst_name")
        st.text_input("Default country", key="admin_inst_country")
        st.button("Save institution config (demo)", key="admin_inst_save")

    with tab[1]:
        st.markdown("### Multi-campus Support")
        st.text_input("New campus name", key="admin_new_campus_name")
        st.text_input("City / location", key="admin_new_campus_city")
        st.button("Add campus (demo)", key="admin_add_campus")

    with tab[2]:
        st.markdown("### Academic Calendars")
        st.date_input("Semester start", key="admin_sem_start")
        st.date_input("Semester end", key="admin_sem_end")
        st.button("Save academic calendar (demo)", key="admin_sem_save")

    with tab[3]:
        st.markdown("### Staff approvals & roles")
        st.text_input("Staff email or ID", key="admin_staff_identifier")
        role = st.selectbox(
            "Assign role",
            ["Lecturer", "Staff", "Institution Admin"],
            key="admin_staff_role",
        )
        st.button("Approve / update staff role (demo)", key="admin_staff_save")

    with tab[4]:
        st.markdown("### Policies & digital notices")
        policy_title = st.text_input("Policy / notice title", key="admin_policy_title")
        policy_body = st.text_area("Policy body / notice content", key="admin_policy_body")
        st.button("Publish notice (demo)", key="admin_policy_publish")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 3. CAMPUS DINING & MESS HUB
# -------------------------------------------------------------------
def ui_mess_hub(identity: Identity):
    _section_card(
        "Campus Dining & Mess Hub",
        "Menus, subscriptions, cashless payments, and feedback.",
    )

    tab = st.tabs(
        [
            "🍽️ Student View",
            "📋 Vendor Menu & Pricing",
            "📊 Vendor Dashboard",
        ]
    )

    # Student view
    with tab[0]:
        st.markdown("### Daily / Weekly Menus")
        st.date_input("Select date", key="mess_date", value=date.today())
        st.info("Menus are loaded from vendor configs in SANZAD Core (demo).")
        st.markdown("#### Select meal")
        meal = st.selectbox(
            "Meal",
            ["Breakfast", "Lunch", "Supper"],
            key="mess_meal_select",
        )
        st.text("Price: shown from SANZAD (demo)")

        if st.button("Pay via SANZAD Pay (demo)", key="mess_pay_btn"):
            payment = create_payment_request(
                tenant_id=identity.institution_id,
                payer_id=identity.user_id,
                amount=150.0,
                currency="KES",
                description=f"{meal} mess meal",
                metadata={"domain": "mess", "meal_type": meal},
            )
            st.success(
                f"Payment request created (demo). Scan QR at: {payment['qr_url']}"
            )
            log_event(
                tenant_id=identity.institution_id,
                actor_id=identity.user_id,
                event_type="campus_hub.mess.payment_requested",
                payload={"amount": 150.0, "meal": meal},
            )

    # Vendor menu & pricing
    with tab[1]:
        st.markdown("### Vendor Menu Management")
        if identity.role not in ("Vendor / Service Provider", "Institution Admin"):
            st.info("Only mess vendors or institution admins can manage menus.")
        else:
            day = st.selectbox(
                "Day", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key="mess_day"
            )
            meal_type = st.selectbox(
                "Meal type", ["Breakfast", "Lunch", "Supper"], key="mess_meal_type"
            )
            item_name = st.text_input("Meal item", key="mess_item_name")
            price = st.number_input(
                "Price", min_value=0.0, step=1.0, key="mess_price"
            )
            tags = st.multiselect(
                "Nutrition tags",
                ["Vegan", "Vegetarian", "Halal", "Gluten-free", "High protein"],
                key="mess_tags",
            )
            st.button("Save / update item (demo)", key="mess_item_save")

    # Vendor dashboard
    with tab[2]:
        st.markdown("### Vendor Dashboard")
        if identity.role not in ("Vendor / Service Provider", "Institution Admin"):
            st.info("Only mess vendors or institution admins can see this dashboard.")
        else:
            st.write("Revenue charts, meal popularity, and feedback appear here.")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 4. HOSTEL & ACCOMMODATION HUB
# -------------------------------------------------------------------
def ui_hostel_hub(identity: Identity):
    _section_card(
        "Hostel & Accommodation Hub",
        "Listings, applications, digital rent, and maintenance.",
    )

    tab = st.tabs(
        [
            "🏠 Student View",
            "📝 Applications & Tenancy",
            "🛠️ Maintenance",
        ]
    )

    with tab[0]:
        st.markdown("### Hostel Listings")
        st.info("Listings are fetched from SANZAD Accommodation service (demo).")
        st.text_input("Filter by area / hostel name", key="hostel_filter")

    with tab[1]:
        st.markdown("### Applications & Tenancy")
        if identity.role == "Student":
            st.text_input("Preferred hostel / room type", key="hostel_pref")
            if st.button("Apply for hostel (demo)", key="hostel_apply_btn"):
                st.success("Hostel application submitted (demo).")
        if identity.role in ("Institution Admin", "Vendor / Service Provider"):
            st.text_input("Student ID / reg no", key="hostel_student_id")
            st.selectbox(
                "Decision",
                ["Pending", "Approved", "Rejected"],
                key="hostel_decision",
            )
            st.button("Update application (demo)", key="hostel_update_app")

    with tab[2]:
        st.markdown("### Maintenance Requests")
        desc = st.text_area("Describe maintenance issue", key="hostel_maint_desc")
        if st.button("Submit request (demo)", key="hostel_maint_submit"):
            st.success("Maintenance request submitted (demo).")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 5. CAMPUS MARKETPLACE
# -------------------------------------------------------------------
def ui_marketplace(identity: Identity):
    _section_card(
        "Campus Marketplace",
        "Buy/sell items, services, and manage cashless transactions.",
    )

    tab = st.tabs(
        [
            "🛒 Browse & Buy",
            "📦 Sell / List Item",
            "⚖️ Disputes & Ratings",
        ]
    )

    with tab[0]:
        st.markdown("### Browse items")
        st.text_input("Search items", key="mkt_search")
        st.info(
            "Items and vendors come from SANZAD Marketplace service (demo). "
            "Only verified campus accounts appear."
        )

    with tab[1]:
        st.markdown("### Sell / List Item")
        if not require_role("Student", "Vendor / Service Provider"):
            st.info("Only students and verified vendors can list items.")
        else:
            st.text_input("Item title", key="mkt_item_title")
            st.text_area("Description", key="mkt_item_desc")
            st.number_input("Price", min_value=0.0, step=10.0, key="mkt_item_price")
            st.button("Publish listing (demo)", key="mkt_item_publish")

    with tab[2]:
        st.markdown("### Disputes & Ratings")
        st.info(
            "Ratings and dispute logs are stored by SANZAD Marketplace + Audit "
            "Engines (demo)."
        )

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 6. WORK, GIGS & ATTACHMENTS
# -------------------------------------------------------------------
def ui_work_gigs(identity: Identity):
    _section_card(
        "Work, Gigs & Attachments",
        "Campus jobs, gigs, industrial attachments, and verified records.",
    )

    tab = st.tabs(
        [
            "💼 Job & gig board",
            "📘 Attachments & internships",
            "📄 Work logs & approvals",
        ]
    )

    with tab[0]:
        st.markdown("### Job & Gig Board")
        st.info("Opportunities are sourced from SANZAD Work service (demo).")
        st.text_input("Filter by skill / keyword", key="work_filter")

    with tab[1]:
        st.markdown("### Attachments & Internships")
        if identity.role == "Student":
            st.text_input("Preferred industry / company", key="att_pref")
            st.button("Submit interest (demo)", key="att_submit")

    with tab[2]:
        st.markdown("### Work logs & approvals")
        if identity.role in ("Student", "Lecturer", "Staff"):
            st.text_area("Log today's work / activities", key="work_log_text")
            st.button("Save log (demo)", key="work_log_save")
        if identity.role in ("Lecturer", "Staff", "Institution Admin"):
            st.text_input("Student ID", key="work_log_student_id")
            st.button("Review logs (demo)", key="work_log_review")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 7. WELLBEING & STUDENT SUPPORT
# -------------------------------------------------------------------
def ui_wellbeing(identity: Identity):
    _section_card(
        "Wellbeing & Student Support",
        "Mental health, counseling, emergency support, and anonymous reports.",
    )

    tab = st.tabs(
        [
            "🧠 Check-ins",
            "📞 Counseling",
            "🚨 Emergency & anonymous reports",
        ]
    )

    with tab[0]:
        st.markdown("### Mental health check-ins")
        mood = st.slider("How are you feeling today?", 0, 10, 5, key="wb_mood")
        st.text_area("Anything you want to share?", key="wb_notes")
        if st.button("Save check-in (demo)", key="wb_save_checkin"):
            st.success("Check-in saved (demo).")
            log_event(
                tenant_id=identity.institution_id,
                actor_id=identity.user_id,
                event_type="campus_hub.wellbeing.checkin",
                payload={"mood": mood},
            )

    with tab[1]:
        st.markdown("### Counseling booking")
        st.selectbox(
            "Preferred mode", ["In-person", "Online"], key="wb_counsel_mode"
        )
        st.date_input("Preferred date", key="wb_counsel_date")
        st.button("Request session (demo)", key="wb_counsel_request")

    with tab[2]:
        st.markdown("### Emergency & anonymous reports")
        st.text_area("Describe the situation", key="wb_emergency_desc")
        anonymous = st.checkbox("Submit anonymously", key="wb_emergency_anon")
        if st.button("Send emergency report (demo)", key="wb_emergency_send"):
            st.error("Emergency report sent (demo). Campus security will respond.")
            log_event(
                tenant_id=identity.institution_id,
                actor_id=identity.user_id if not anonymous else "anonymous",
                event_type="campus_hub.wellbeing.emergency_report",
                payload={"anonymous": anonymous},
            )

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 8. FEES, PAYMENTS & FINANCE
# -------------------------------------------------------------------
def ui_finance(identity: Identity):
    _section_card(
        "Fees, Payments & Finance",
        "Tuition, rent, mess, tickets, fines, and digital receipts.",
    )

    tab = st.tabs(
        [
            "💳 My payments",
            "🏫 Institution billing",
        ]
    )

    with tab[0]:
        st.markdown("### My payments")
        st.info("Pulled from SANZAD Pay & Finance core (demo).")
        payment_type = st.selectbox(
            "What do you want to pay?",
            ["Tuition", "Hostel rent", "Mess", "Event ticket", "Fine"],
            key="fin_pay_type",
        )
        amount = st.number_input(
            "Amount", min_value=0.0, step=100.0, key="fin_pay_amount"
        )
        if st.button("Pay via SANZAD Pay (demo)", key="fin_pay_btn"):
            payment = create_payment_request(
                tenant_id=identity.institution_id,
                payer_id=identity.user_id,
                amount=amount,
                currency="KES",
                description=payment_type,
                metadata={"domain": "finance", "type": payment_type},
            )
            st.success(
                f"Payment created (demo). Scan QR:\n{payment['qr_url']}"
            )

    with tab[1]:
        st.markdown("### Institution billing")
        if identity.role not in ("Institution Admin", "SANZAD Super Admin"):
            st.info("Only institution admins can view campus-level billing.")
        else:
            st.write("Total revenue, breakdown by category, and pending balances.")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 9. DIGITAL ID & ACCESS
# -------------------------------------------------------------------
def ui_digital_id(identity: Identity):
    _section_card(
        "Digital ID & Access",
        "Futuristic campus digital ID and QR access.",
    )

    st.markdown("### Your Campus ID")
    st.write(f"User: **{identity.full_name}**")
    st.write(f"Role: **{identity.role}**")
    st.write(f"Institution: **{identity.institution_id}**")
    st.info("QR code generated by SANZAD Identity service (demo).")

    st.markdown("### Access endpoints")
    st.write("Library, events, hostels, attendance & verification are all QR-based.")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 10. COMMUNICATION & COMMUNITY
# -------------------------------------------------------------------
def ui_communication(identity: Identity):
    _section_card(
        "Communication & Community",
        "Groups, announcements, broadcasts, polls, and clubs.",
    )

    tab = st.tabs(
        [
            "👥 Groups & channels",
            "📢 Announcements & events",
            "📊 Polls & surveys",
            "🎭 Clubs & societies",
        ]
    )

    with tab[0]:
        st.markdown("### Groups & channels")
        st.info("Backed by SANZAD Messaging core (demo).")
        st.text_input("Create or join group by code", key="comm_group_code")

    with tab[1]:
        st.markdown("### Institution announcements & event broadcasts")
        if identity.role in ("Institution Admin", "Lecturer", "Staff"):
            title = st.text_input("Announcement title", key="comm_announcement_title")
            body = st.text_area("Message", key="comm_announcement_body")
            if st.button("Broadcast announcement (demo)", key="comm_announcement_send"):
                send_notification(
                    tenant_id=identity.institution_id,
                    user_ids=[],
                    title=title,
                    body=body,
                    tags=["announcement"],
                )
                st.success("Announcement broadcasted (demo).")

    with tab[2]:
        st.markdown("### Polls & surveys")
        if identity.role in ("Institution Admin", "SANZAD Super Admin"):
            question = st.text_input("Question", key="comm_poll_question")
            options = st.text_area("Options (one per line)", key="comm_poll_options")
            st.button("Create poll (demo)", key="comm_poll_create")
        else:
            st.info("You can vote on active polls (demo placeholder).")

    with tab[3]:
        st.markdown("### Clubs & societies")
        st.text_input("Search clubs / societies", key="comm_club_search")
        if identity.role == "Student":
            st.button("Start a new club (demo)", key="comm_club_start")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 11. ANALYTICS & TRANSPARENCY
# -------------------------------------------------------------------
def ui_analytics(identity: Identity):
    _section_card(
        "Analytics & Transparency",
        "Performance, attendance, revenue, and accountability views.",
    )

    tab = st.tabs(
        [
            "📊 Student & academic",
            "📈 Revenue & services",
            "🔍 Accountability views",
        ]
    )

    with tab[0]:
        st.markdown("### Student performance & attendance")
        st.info("Charts powered by SANZAD Analytics Engine (demo).")

    with tab[1]:
        st.markdown("### Revenue & service usage")
        if identity.role not in ("Institution Admin", "SANZAD Super Admin"):
            st.info("Only admins see revenue dashboards.")
        else:
            st.write("Per-service revenue and usage stats appear here.")

    with tab[2]:
        st.markdown("### Accountability views")
        st.info(
            "Public or student-facing summaries (e.g. how fees are allocated) "
            "are derived from institution-approved data (demo)."
        )

    st.markdown("</div>", unsafe_allow_html=True)
