# src/modules/home.py

import streamlit as st
import pandas as pd
from translations import t
from db import (
    list_institutions,
    add_institution_application,
    approve_institution_db,
    delete_institution_application,
)


def init_ecosystem_state():
    """Ensure ecosystem wrapper exists and load institutions from DB."""
    if "ecosystem" not in st.session_state:
        st.session_state.ecosystem = {"institutions": {}}

    # Pending users still in memory for now
    if "pending_users" not in st.session_state:
        st.session_state.pending_users = []

    # Load institutions from DB into memory structure
    ecosystem = st.session_state.ecosystem
    ecosystem["institutions"] = {}
    rows = list_institutions()
    for _, name, code, status, country, city, details in rows:
        ecosystem["institutions"][name] = {
            "code": code or "",
            "status": status or "pending",
            "location": f"{city or ''}, {country or ''} {details or ''}".strip(", "),
            "departments": set(),
            "students": [],
            "teachers": [],
            "parents": [],
            "timetables": [],
            "announcements": [],
        }


def render(role: str):
    lang = st.session_state.get("lang", "en")
    init_ecosystem_state()
    ecosystem = st.session_state.ecosystem

    st.header(t("home_title", lang))
    st.write("Role-based overview for the Sanzad Global Ecosystem.")

    user_name = st.session_state.get("user_name", "").strip()
    if user_name:
        st.write(f"Welcome, **{user_name}**.")

    st.markdown("---")

    # -----------------------------
    # Institution banner
    # -----------------------------
    inst_names = sorted(ecosystem["institutions"].keys())
    inst_data_for_banner = None

    if role == "Super Admin":
        if inst_names:
            inst_col1, inst_col2 = st.columns([2, 3])
            with inst_col1:
                selected_inst = st.selectbox(
                    "Select institution to view",
                    inst_names,
                    key="home_inst_select_admin",
                )
            inst_data_for_banner = ecosystem["institutions"][selected_inst]
            with inst_col2:
                st.markdown(f"**Institution:** {selected_inst}")
                code = inst_data_for_banner.get("code", "")
                if code:
                    st.write(f"Code: {code}")
                st.write(f"Status: {inst_data_for_banner.get('status', 'pending')}")
        else:
            st.info("No institutions in database yet.")
    else:
        selected_inst_name = st.session_state.get("user_institution", "").strip()
        if selected_inst_name and selected_inst_name in ecosystem["institutions"]:
            inst_data_for_banner = ecosystem["institutions"][selected_inst_name]
            st.markdown(f"**Institution:** {selected_inst_name}")
            st.write(f"Code: {inst_data_for_banner.get('code', 'N/A')}")
            st.write(f"Status: {inst_data_for_banner.get('status', 'pending')}")
        elif selected_inst_name:
            st.warning(
                f"Your institution '{selected_inst_name}' is not yet approved in the database. "
                f"Some features will be limited until approval."
            )
        else:
            st.info(
                "No institution linked yet. Use the registration/apply sections below if needed."
            )

    st.markdown("---")

    # -----------------------------
    # Role-specific sections
    # -----------------------------
    if role == "Super Admin":
        render_super_admin_sections(ecosystem)
    elif role == "Institution":
        render_institution_role_sections(ecosystem)
    elif role == "Student":
        render_student_apply_section()
    elif role == "Teacher":
        render_teacher_apply_section()
    elif role == "Parent":
        render_parent_apply_section()
    else:
        render_admin_view(ecosystem)

    # -----------------------------
    # Emergency alerts panel (still session-based)
    # -----------------------------
    if role in ["Super Admin", "Institution"]:
        st.markdown("---")
        st.subheader("Emergency Alerts (from Panic Button)")

        emergencies = st.session_state.get("emergencies", [])
        if not emergencies:
            st.write("No emergency alerts recorded in this session yet.")
        else:
            df_em = pd.DataFrame(emergencies)
            st.dataframe(df_em)


# =========================
# Super Admin sections
# =========================


def render_super_admin_sections(ecosystem):
    st.subheader("Super Admin Panel")

    tab_inst, tab_users, tab_overview = st.tabs(
        ["Institution Applications", "User Requests (in memory)", "Ecosystem Overview"]
    )

    with tab_inst:
        render_institution_requests_admin()

    with tab_users:
        render_user_requests_admin()

    with tab_overview:
        render_admin_view(ecosystem)


def render_institution_requests_admin():
    st.markdown("### Institution Applications from DB")

    all_rows = list_institutions()
    pending = [r for r in all_rows if r[3] == "pending"]
    approved = [r for r in all_rows if r[3] == "approved"]

    if pending:
        df_pending = pd.DataFrame(
            [
                {
                    "Name": r[1],
                    "Country": r[4],
                    "City": r[5],
                    "Details": r[6],
                    "Code": r[2] or "",
                }
                for r in pending
            ]
        )
        st.write("Pending institution applications:")
        st.dataframe(df_pending)

        names = [r[1] for r in pending]
        selected_name = st.selectbox("Select an institution to review", names)
        new_code = st.text_input(
            "Set / update institution code (optional)", key="inst_code_input"
        )

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("Approve selected institution"):
                approve_institution_db(selected_name, new_code.strip() or None)
                st.success(f"Institution '{selected_name}' has been approved.")
        with action_col2:
            if st.button("Reject selected institution"):
                delete_institution_application(selected_name)
                st.warning(f"Institution '{selected_name}' application removed.")
    else:
        st.write("No pending institution applications in database.")

    st.markdown("---")
    st.markdown("### Approved Institutions")
    if approved:
        df_inst = pd.DataFrame(
            [
                {
                    "Name": r[1],
                    "Code": r[2] or "",
                    "Country": r[4] or "",
                    "City": r[5] or "",
                    "Details": r[6] or "",
                }
                for r in approved
            ]
        )
        st.dataframe(df_inst)
    else:
        st.write("No institutions approved yet.")


def render_user_requests_admin():
    st.markdown("### User Registration Requests (still in memory)")

    pending = st.session_state.get("pending_users", [])
    if not pending:
        st.write("No pending user registration requests in this session.")
        return

    df_users = pd.DataFrame(pending)
    st.dataframe(df_users)
    st.info(
        "Next step: move these user requests to the SQLite users table, similar to institutions."
    )


# =========================
# Institution role sections
# =========================


def render_institution_role_sections(ecosystem):
    st.subheader("Institution Panel")

    # Guard: ensure only Institution role uses this
    role_override = st.session_state.get("role_override", "")
    if role_override != "Institution":
        st.info("Institution tools are visible only to the Institution role.")
        return

    inst_name = st.session_state.get("user_institution", "").strip()
    if not inst_name:
        st.info(
            "Set your institution name in your profile so the system can link you to it."
        )
        return

    institutions = ecosystem["institutions"]
    if inst_name not in institutions:
        st.markdown("### Apply to register your institution")
        with st.form("institution_apply_form_db"):
            country = st.text_input("Country")
            city = st.text_input("City / Town")
            details = st.text_input("Location details (optional)")
            submitted = st.form_submit_button("Submit institution application")

            if submitted:
                if not country.strip() or not city.strip():
                    st.error("Country and city are required.")
                else:
                    add_institution_application(
                        name=inst_name,
                        country=country.strip(),
                        city=city.strip(),
                        details=details.strip(),
                    )
                    st.success(
                        "Institution application stored in database and waiting for Super Admin approval."
                    )
                    return
    else:
        inst_data = institutions[inst_name]
        st.markdown("### Institution View")
        st.write(f"Status: {inst_data.get('status', 'approved')}")
        st.write(f"Code: {inst_data.get('code', 'N/A')}")
        st.write(
            f"Departments: {', '.join(sorted(inst_data['departments'])) if inst_data.get('departments') else 'None'}"
        )
        st.write(f"Students: {len(inst_data['students'])}")
        st.write(f"Teachers: {len(inst_data['teachers'])}")
        st.write(f"Parents linked: {len(inst_data['parents'])}")

        if inst_data.get("status") == "approved":
            render_institution_department_manager(ecosystem)
            render_institution_resources(ecosystem)
        else:
            st.info(
                "Institution not fully approved. Department management and resources will unlock after approval."
            )


def render_institution_department_manager(ecosystem):
    st.subheader("Manage Departments (Institution)")

    inst_name = st.session_state.get("user_institution", "").strip()
    if not inst_name or inst_name not in ecosystem["institutions"]:
        st.info("Link this profile to an approved institution first.")
        return

    inst_data = ecosystem["institutions"][inst_name]
    inst_data.setdefault("departments", set())

    col_add, col_remove = st.columns(2)

    with col_add:
        st.markdown("**Add Department**")
        new_dept = st.text_input("New department name", key="inst_new_dept")
        if st.button("Add department"):
            d = new_dept.strip()
            if not d:
                st.error("Department name cannot be empty.")
            elif d in inst_data["departments"]:
                st.warning("Department already exists.")
            else:
                inst_data["departments"].add(d)
                st.success(f"Department '{d}' added.")

    with col_remove:
        st.markdown("**Remove Department**")
        existing_departments = sorted(inst_data["departments"])
        if existing_departments:
            dept_to_remove = st.selectbox(
                "Select department to remove",
                existing_departments,
                key="inst_remove_dept",
            )
            if st.button("Remove department"):
                inst_data["departments"].discard(dept_to_remove)
                st.success(f"Department '{dept_to_remove}' removed.")
        else:
            st.write("No departments to remove yet.")


def render_institution_resources(ecosystem):
    st.subheader("Post Timetables & Announcements (Institution)")

    inst_name = st.session_state.get("user_institution", "").strip()
    if not inst_name or inst_name not in ecosystem["institutions"]:
        st.info("Link this profile to an approved institution first.")
        return

    inst_data = ecosystem["institutions"][inst_name]
    inst_data.setdefault("timetables", [])
    inst_data.setdefault("announcements", [])

    st.markdown("### Timetables (PDF Upload)")
    with st.form("inst_timetable_form"):
        tt_title = st.text_input("Timetable title")
        tt_file = st.file_uploader(
            "Upload timetable PDF", type=["pdf"], key="inst_tt_upload"
        )
        tt_submit = st.form_submit_button("Post timetable")
        if tt_submit:
            if not tt_title.strip() or tt_file is None:
                st.error("Title and PDF are required.")
            else:
                inst_data["timetables"].append(
                    {
                        "title": tt_title.strip(),
                        "filename": tt_file.name,
                        "data": tt_file.read(),
                    }
                )
                st.success("Timetable posted.")

    st.markdown("### Announcements (Text)")
    with st.form("inst_announcement_form"):
        a_title = st.text_input("Announcement title")
        a_body = st.text_area("Announcement details")
        a_submit = st.form_submit_button("Post announcement")
        if a_submit:
            if not a_title.strip() or not a_body.strip():
                st.error("Title and details are required.")
            else:
                inst_data["announcements"].append(
                    {
                        "title": a_title.strip(),
                        "body": a_body.strip(),
                    }
                )
                st.success("Announcement posted.")


# =========================
# User self-registration (still in memory)
# =========================


def render_student_apply_section():
    st.subheader("Student Registration Request")

    with st.form("student_request_form"):
        name = st.text_input("Your full name")
        inst = st.text_input(
            "Institution name (exact as in DB)",
            value=st.session_state.get("user_institution", ""),
        )
        reg_no = st.text_input("Registration number")
        dept = st.text_input("Department")
        submitted = st.form_submit_button("Submit registration request")

        if submitted:
            if (
                not name.strip()
                or not inst.strip()
                or not reg_no.strip()
                or not dept.strip()
            ):
                st.error("All fields are required.")
            else:
                st.session_state.pending_users.append(
                    {
                        "role": "Student",
                        "name": name.strip(),
                        "institution": inst.strip(),
                        "extra": {
                            "reg_no": reg_no.strip(),
                            "department": dept.strip(),
                        },
                    }
                )
                st.session_state["user_institution"] = inst.strip()
                st.success(
                    "Student registration request stored in memory (next step: move to DB)."
                )


def render_teacher_apply_section():
    st.subheader("Teacher Registration Request")

    with st.form("teacher_request_form"):
        name = st.text_input("Your full name")
        inst = st.text_input(
            "Institution name (exact as in DB)",
            value=st.session_state.get("user_institution", ""),
        )
        dept = st.text_input("Department")
        submitted = st.form_submit_button("Submit registration request")

        if submitted:
            if not name.strip() or not inst.strip() or not dept.strip():
                st.error("All fields are required.")
            else:
                st.session_state.pending_users.append(
                    {
                        "role": "Teacher",
                        "name": name.strip(),
                        "institution": inst.strip(),
                        "extra": {"department": dept.strip()},
                    }
                )
                st.session_state["user_institution"] = inst.strip()
                st.success(
                    "Teacher registration request stored in memory (next step: move to DB)."
                )


def render_parent_apply_section():
    st.subheader("Parent / Guardian Registration Request")

    with st.form("parent_request_form"):
        name = st.text_input("Your full name")
        inst = st.text_input(
            "Institution of your child (exact as in DB)",
            value=st.session_state.get("user_institution", ""),
        )
        child_name = st.text_input("Child's name")
        child_reg = st.text_input("Child's registration number")
        submitted = st.form_submit_button("Submit registration request")

        if submitted:
            if (
                not name.strip()
                or not inst.strip()
                or not child_name.strip()
                or not child_reg.strip()
            ):
                st.error("All fields are required.")
            else:
                st.session_state.pending_users.append(
                    {
                        "role": "Parent",
                        "name": name.strip(),
                        "institution": inst.strip(),
                        "extra": {
                            "child_name": child_name.strip(),
                            "child_reg_no": child_reg.strip(),
                        },
                    }
                )
                st.session_state["user_institution"] = inst.strip()
                st.success(
                    "Parent registration request stored in memory (next step: move to DB)."
                )


# =========================
# Ecosystem overview
# =========================


def render_admin_view(ecosystem):
    st.subheader("Ecosystem Overview (from DB + memory)")

    institutions = ecosystem["institutions"]
    if not institutions:
        st.write("No institutions loaded from database yet.")
        return

    rows = []
    for inst_name, data in institutions.items():
        rows.append(
            {
                "Institution": inst_name,
                "Code": data.get("code", "N/A"),
                "Status": data.get("status", "pending"),
                "Departments": len(data.get("departments", [])),
                "Students": len(data["students"]),
                "Teachers": len(data["teachers"]),
                "Parents linked": len(data["parents"]),
                "Timetables": len(data.get("timetables", [])),
                "Announcements": len(data.get("announcements", [])),
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df)
