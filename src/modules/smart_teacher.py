import streamlit as st
import pandas as pd
from datetime import date
from src.translations import t
from src.db import (
    create_assignment_db,
    list_teacher_assignments,
    list_student_assignments,
    save_submission_db,
    list_teacher_submissions,
    list_student_submissions,
    save_grade_db,
    list_student_grades,
    get_user_by_email,
    get_conn,  # make sure this is exported from db.py
)


def _get_current_user():
    """
    Expect that after login/registration you stored:
    st.session_state['user_email']
    """
    email = st.session_state.get("user_email", "")
    if not email:
        return None
    return get_user_by_email(email)


def _find_child_user(parent_user):
    """
    Resolve child user by parent's stored child reg no + institution.
    Uses users table; can be optimized later.
    """
    child_reg = (parent_user.get("parent_child_reg_no") or "").strip()
    inst = (parent_user.get("institution_name") or "").strip()
    if not child_reg or not inst:
        return None

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_code, full_name, email, password_hash, role, phone,
                   student_id, institution_name, teacher_reg_no, student_reg_no,
                   parent_child_name, parent_child_reg_no, status
            FROM users
            WHERE role = 'Student'
              AND institution_name = ?
              AND student_reg_no = ?
            """,
            (inst, child_reg),
        )
        row = cur.fetchone()
        if not row:
            return None
        (
            id_,
            user_code,
            full_name,
            email,
            password_hash,
            role,
            phone,
            student_id,
            institution_name,
            teacher_reg_no,
            student_reg_no,
            parent_child_name,
            parent_child_reg_no,
            status,
        ) = row
        return {
            "id": id_,
            "user_code": user_code,
            "full_name": full_name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "phone": phone,
            "student_id": student_id,
            "institution_name": institution_name,
            "teacher_reg_no": teacher_reg_no,
            "student_reg_no": student_reg_no,
            "parent_child_name": parent_child_name,
            "parent_child_reg_no": parent_child_reg_no,
            "status": status,
        }
    finally:
        if conn is not None:
            conn.close()


def render(role: str):
    lang = st.session_state.get("lang", "en")

    st.header(t("smart_title", lang))
    st.write("Assignment management, grading, files, students, class messages, and AI tools.")

    # -------- Super Admin bypass + normal login --------
    app_role = st.session_state.get("current_role")
    if app_role == "Super Admin":
        current_user = {
            "id": -1,
            "full_name": "Super Admin",
            "email": "superadmin@local",
            "role": "Super Admin",
            "institution_name": st.session_state.get("profile_institution", ""),
            "parent_child_reg_no": "",
        }
    else:
        current_user = _get_current_user()

    if current_user is None:
        st.warning(
            "Please register and log in first (Institution, Teacher, Student, or Parent) "
            "so Smart Teacher can load your data."
        )
        return

    role = current_user["role"]
    st.info(f"Logged in as: **{current_user['full_name']}** ({role})")

    if "class_messages" not in st.session_state:
        st.session_state.class_messages = []

    tab_overview, tab_assign, tab_grades, tab_messages, tab_ai_tools = st.tabs(
        [
            t("overview_tab", lang),
            t("assign_tab", lang),
            t("grades_tab", lang),
            t("messages_tab", lang),
            t("ai_tab", lang),
        ]
    )

    # -------- Overview --------
    with tab_overview:
        st.subheader(t("overview_tab", lang))

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Current Smart Teacher role:** {role}")

            if role in ["Teacher", "Super Admin"]:
                teacher_assignments = list_teacher_assignments(current_user["id"]) if role != "Super Admin" else []
                st.write(f"**Assignments you created:** {len(teacher_assignments)}")
                teacher_subs = list_teacher_submissions(current_user["id"]) if role != "Super Admin" else []
                st.write(f"**Submissions for your assignments:** {len(teacher_subs)}")

            if role == "Student":
                student_assigns = list_student_assignments(current_user)
                st.write(f"**Assignments available to you:** {len(student_assigns)}")
                student_subs = list_student_submissions(current_user["id"])
                st.write(f"**Your submissions:** {len(student_subs)}")

            if role == "Parent":
                child_grades = _get_child_grades(current_user)
                st.write(f"**Recorded grades for your child:** {len(child_grades)}")

        with col2:
            st.write(
                "Smart Teacher uses your registered role and institution to control exactly what you can see.\n\n"
                "- Teachers: create assignments, see and grade submissions for their classes.\n"
                "- Students: see published assignments for their institution/class and only their own marks.\n"
                "- Parents: see only results of the child linked to their account.\n"
                "- Institutions / Super Admin: high-level admin and analytics views."
            )

        st.markdown("---")
        st.write("Use the tabs above to manage assignments, grades, messages, and AI tools.")

    # -------- Assignments --------
    with tab_assign:
        st.subheader(t("assign_tab", lang))

        if role in ["Teacher", "Super Admin"]:
            _teacher_assignments_and_submissions(current_user)
        elif role == "Student":
            _student_assignments_and_submissions(current_user)
        elif role == "Parent":
            st.info("Parents do not create or submit assignments. Use the Grades tab to see your child's marks.")
        elif role == "Institution":
            st.info("Institution accounts can review summary analytics here in future versions.")

    # -------- Grades --------
    with tab_grades:
        st.subheader(t("grades_tab", lang))

        if role in ["Teacher", "Super Admin"]:
            _teacher_grades_view(current_user)
        elif role == "Student":
            _student_grades_view(current_user)
        elif role == "Parent":
            _parent_grades_view(current_user)
        elif role == "Institution":
            st.info("Institution accounts will see aggregated performance analytics here later.")

    # -------- Messages --------
    with tab_messages:
        _messages_view(current_user)

    # -------- AI Tools --------
    with tab_ai_tools:
        _ai_tools_view(current_user)


# ================== TEACHER FLOW ==================

def _teacher_assignments_and_submissions(user):
    st.markdown("### Create Assignment (Teacher)")

    col_left, col_right = st.columns(2)

    with col_left:
        with st.form("assignment_form_db"):
            title = st.text_input("Assignment Title")
            subject = st.selectbox("Subject", ["Math", "Science", "History", "English", "Other"])
            class_name = st.text_input("Class / Group", value="Grade 10 A")
            due_date = st.date_input("Due Date", value=date.today())
            max_points = st.number_input("Max Points", min_value=1, max_value=100, value=10)
            status = st.selectbox("Status", ["Draft", "Published", "Closed"])
            description = st.text_area("Instructions / Description")

            submitted = st.form_submit_button("Create Assignment")
            if submitted:
                if not title.strip():
                    st.error("Please enter an Assignment Title before creating.")
                else:
                    teacher_id = user["id"] if user["id"] != -1 else 0  # Super Admin placeholder
                    create_assignment_db(
                        teacher_id=teacher_id,
                        title=title,
                        subject=subject,
                        class_name=class_name,
                        due_date=str(due_date),
                        max_points=int(max_points),
                        status=status,
                        description=description,
                    )
                    st.success(f"Assignment '{title}' ({status}) created for {subject} - {class_name}.")

    with col_right:
        st.markdown("### Your Assignments")
        if user["id"] == -1:
            st.info("As Super Admin, you can create assignments for demo, but no teacher is linked.")
            rows = []
        else:
            rows = list_teacher_assignments(user["id"])
        if not rows:
            st.write("No assignments found yet.")
        else:
            df_assign = pd.DataFrame(
                [
                    {
                        "ID": r[0],
                        "Title": r[1],
                        "Subject": r[2],
                        "Class": r[3],
                        "Due Date": r[4],
                        "Max Points": r[5],
                        "Status": r[6],
                    }
                    for r in rows
                ]
            )
            st.dataframe(df_assign, use_container_width=True)

    st.markdown("---")
    st.markdown("### Student Submissions for Your Assignments")

    if user["id"] == -1:
        st.info("Super Admin is not linked to a specific teacher; submissions list is empty for now.")
        subs = []
    else:
        subs = list_teacher_submissions(user["id"])

    if not subs:
        st.write("No submissions for your assignments yet.")
        return

    df_sub = pd.DataFrame(
        [
            {
                "Submission ID": s[0],
                "Assignment ID": s[1],
                "Student ID": s[2],
                "Filename": s[3],
                "Submitted At": s[4],
                "Assignment Title": s[5],
                "Class": s[6],
                "Student Name": s[7],
            }
            for s in subs
        ]
    )
    st.dataframe(df_sub, use_container_width=True)

    st.markdown("#### Manual Grading for Selected Submission")

    sub_labels = [f"{s[0]} – {s[7]} – {s[5]} ({s[3]})" for s in subs]
    selected = st.selectbox("Select submission to grade", sub_labels)
    if selected:
        submission_id = int(selected.split("–")[0].strip())
        score = st.number_input("Score", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
        max_points = st.number_input("Max Points", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
        if st.button("Save Grade for Selected Submission"):
            teacher_id = user["id"] if user["id"] != -1 else 0
            save_grade_db(
                submission_id=submission_id,
                teacher_id=teacher_id,
                score=score,
                max_points=max_points,
            )
            st.success(f"Saved grade {score}/{max_points} for submission ID {submission_id}.")


def _teacher_grades_view(user):
    st.markdown("### Gradebook (Teacher Overview)")
    if user["id"] == -1:
        st.info("Super Admin overview is not linked to specific teacher gradebook yet.")
        return
    subs = list_teacher_submissions(user["id"])
    if not subs:
        st.write("No submissions yet, so no grades to aggregate.")
        return
    st.info(
        "Each grade you save in the Assignments tab is stored per submission. "
        "Later this view can show full analytics per student/class."
    )


# ================== STUDENT FLOW ==================

def _student_assignments_and_submissions(user):
    st.markdown("### Assignments Available to You")

    assigns = list_student_assignments(user)
    if not assigns:
        st.write("No published assignments available for your institution/class yet.")
        return

    df_assign = pd.DataFrame(
        [
            {
                "Assignment ID": r[0],
                "Title": r[1],
                "Subject": r[2],
                "Class": r[3],
                "Due Date": r[4],
                "Max Points": r[5],
                "Status": r[6],
            }
            for r in assigns
        ]
    )
    st.dataframe(df_assign, use_container_width=True)

    st.markdown("### Submit Your Work")

    labels = [f"{r[0]} – {r[1]} ({r[2]})" for r in assigns]
    selected = st.selectbox("Assignment to submit", labels)
    if not selected:
        return

    assignment_id = int(selected.split("–")[0].strip())
    submission_pdf = st.file_uploader(
        "Upload your solution (PDF)",
        type=["pdf"],
        key="student_submission_uploader_db"
    )

    if st.button("Submit Assignment"):
        if submission_pdf is None:
            st.error("Please upload a PDF file.")
        else:
            save_submission_db(
                assignment_id=assignment_id,
                student_id=user["id"],
                filename=submission_pdf.name,
                file_bytes=submission_pdf.read(),
            )
            st.success("Submission uploaded successfully.")

    st.markdown("---")
    st.markdown("### Your Previous Submissions")

    subs = list_student_submissions(user["id"])
    if not subs:
        st.write("You have not submitted any assignments yet.")
    else:
        df_sub = pd.DataFrame(
            [
                {
                    "Submission ID": s[0],
                    "Assignment ID": s[1],
                    "Filename": s[2],
                    "Submitted At": s[3],
                    "Assignment Title": s[4],
                    "Subject": s[5],
                    "Class": s[6],
                }
                for s in subs
            ]
        )
        st.dataframe(df_sub, use_container_width=True)


def _student_grades_view(user):
    st.markdown("### Your Grades")

    grades = list_student_grades(user["id"])
    if not grades:
        st.write("No grades recorded for you yet.")
        return

    df = pd.DataFrame(
        [
            {
                "Grade ID": g[0],
                "Score": g[1],
                "Max Points": g[2],
                "Created At": g[3],
                "Assignment Title": g[4],
                "Subject": g[5],
                "Class": g[6],
                "Percent": (g[1] / g[2] * 100) if g[2] else 0,
            }
            for g in grades
        ]
    )
    st.dataframe(df, use_container_width=True)


# ================== PARENT FLOW ==================

def _get_child_grades(parent_user):
    child_user = _find_child_user(parent_user)
    if child_user is None:
        return []
    return list_student_grades(child_user["id"])


def _parent_grades_view(parent_user):
    st.markdown("### Your Child's Results")

    grades = _get_child_grades(parent_user)
    if not grades:
        st.write(
            "No grades found for your linked child. "
            "Check that the child's registration number and institution are correct in your account."
        )
        return

    df = pd.DataFrame(
        [
            {
                "Grade ID": g[0],
                "Score": g[1],
                "Max Points": g[2],
                "Created At": g[3],
                "Assignment Title": g[4],
                "Subject": g[5],
                "Class": g[6],
                "Percent": (g[1] / g[2] * 100) if g[2] else 0,
            }
            for g in grades
        ]
    )
    st.dataframe(df, use_container_width=True)


# ================== MESSAGES & AI ==================

def _messages_view(user):
    st.subheader(t("messages_tab", st.session_state.get("lang", "en")))
    role = user["role"]

    col_left, col_right = st.columns(2)

    with col_left:
        if role in ["Teacher", "Super Admin"]:
            st.markdown("### Send Message to Class")
            class_name = st.text_input("Target Class / Group", value="Grade 10 A")
            message_text = st.text_area("Message to this class")
            if st.button("Send Message"):
                msg = message_text.strip()
                if not msg:
                    st.error("Message cannot be empty.")
                else:
                    st.session_state.class_messages.append(
                        {
                            "Class": class_name.strip(),
                            "SenderRole": role,
                            "SenderName": user["full_name"],
                            "Message": msg,
                        }
                    )
                    st.success(f"Message sent to class: {class_name}")
        else:
            st.info("Only Teachers and Super Admin can send class messages.")

    with col_right:
        st.markdown("### View Messages")
        class_to_view = st.text_input("View messages for class", value="Grade 10 A")
        msgs = [m for m in st.session_state.class_messages if m["Class"] == class_to_view.strip()]
        if msgs:
            for m in msgs:
                st.write(f"**{m['SenderName']} ({m['SenderRole']}) → {m['Class']}:** {m['Message']}")
        else:
            st.write("No messages for this class yet.")


def _ai_tools_view(user):
    lang = st.session_state.get("lang", "en")
    st.subheader(t("ai_tab", lang))
    role = user["role"]

    if role in ["Teacher", "Super Admin"]:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### AI Lesson Planner (Placeholder)")
            topic = st.text_input("Topic", placeholder="e.g., Linear Equations")
            class_name = st.text_input("Class / Group for this plan", value="Grade 10 A", key="ai_plan_class")
            duration = st.number_input("Duration (minutes)", min_value=10, max_value=120, value=40)
            if st.button("Generate Plan (placeholder)"):
                st.info("In future this will call an AI planner. For now, use the outline below.")
            st.text_area("Lesson Outline (manual for now)")

            st.markdown("---")
            st.markdown("### Attendance Tracking (Placeholder)")
            st.text_area("Attendance notes (manual)")

        with col2:
            st.markdown("### AI Explanations for Students (Placeholder)")
            st.text_area("Common doubts / explanations (manual)")

            st.markdown("---")
            st.markdown("### Teacher Performance Analytics (Planned)")
            st.write("Later this tab will show per-teacher metrics and links to the Analytics module.")
    else:
        st.markdown("### Study Help & Explanations")
        st.write(
            "Here you will see important explanations and tips shared by your teachers. "
            "In future, this will include AI-powered explanations for your questions."
        )
        st.text_area("Your notes / questions (manual for now)")
