import streamlit as st
import pandas as pd  # keep if used elsewhere
import base64
import io

from streamlit_drawable_canvas import st_canvas
from PIL import Image


def _init_overlay_state():
    """Ensure overlay marks list exists in session state."""
    if "overlay_marks" not in st.session_state:
        st.session_state.overlay_marks = []  # list of symbol placements


def _demo_chat_ui(chat_key: str, other_party_label: str):
    """Simple in-platform chat box to be backed by a DB table later."""
    st.markdown(f"##### Chat with {other_party_label}")
    chat_history = st.session_state.get(chat_key, [])
    for sender, msg in chat_history:
        st.write(f"**{sender}:** {msg}")

    new_msg = st.text_input("Type a message", key=f"{chat_key}_input")
    if st.button("Send", key=f"{chat_key}_send"):
        if new_msg.strip():
            chat_history.append(("You", new_msg.strip()))
            st.session_state[chat_key] = chat_history
            st.experimental_rerun()



# -------------------------------------------------------------------
# SHARED HELPERS
# -------------------------------------------------------------------
def _role_badge(role: str):
    st.markdown(
        f"<span style='padding:0.25rem 0.75rem; border-radius:999px; "
        f"background-color:#1f2937; color:#e5e7eb; font-size:0.8rem;'>"
        f"Role: {role}</span>",
        unsafe_allow_html=True,
    )


def _section_card(title: str, description: str = ""):
    st.markdown('<div class="szt-card">', unsafe_allow_html=True)
    st.subheader(title)
    if description:
        st.caption(description)


# -------------------------------------------------------------------
# MAIN ENTRY FOR SANZAD CAMPUS HUB
# -------------------------------------------------------------------
def render(role: str):
    """
    Main entry for Sanzad Campus Hub.
    Role is one of: "Super Admin", "Institution", "Teacher",
                    "Student", "Parent", "Security".
    """
    st.markdown("## Sanzad Campus Hub")
    _role_badge(role)
    st.markdown(
        "A unified hub for academic life, student services, marketplace, "
        "security, community, EnviroTech, and finance."
    )

    st.markdown("---")

    wing = st.selectbox(
        "Choose a Wing",
        [
            "1. Academic Wing",
            "2. Student Services Wing",
            "3. Marketplace Wing",
            "4. Security & Safety Wing",
            "5. Social & Community Wing",
            "6. EnviroTech Wing",
            "7. Finance & Payments Wing",
        ],
        key="campus_hub_wing",
    )

    if wing.startswith("1."):
        academic_wing(role)
    elif wing.startswith("2."):
        student_services_wing(role)
    elif wing.startswith("3."):
        marketplace_wing(role)
    elif wing.startswith("4."):
        security_safety_wing(role)
    elif wing.startswith("5."):
        social_community_wing(role)
    elif wing.startswith("6."):
        envirotech_wing(role)
    elif wing.startswith("7."):
        finance_payments_wing(role)
    else:
        st.info("Select a wing to begin.")


# -------------------------------------------------------------------
# 1. ACADEMIC WING
# -------------------------------------------------------------------
def academic_wing(role: str):
    st.markdown("### 1. Academic Wing")

    sub = st.selectbox(
        "Choose an Academic module",
        [
            "Courses & Lecturers",
            "Assignments & Submissions",
            "Exams & Timetables",
            "Grades & Analytics",
            "Attendance Tracker",
            "Parent Portal",
            "Loan / Scholarship Tracker",
            "Academic Calendar",
        ],
        key="academic_sub",
    )

    if sub == "Courses & Lecturers":
        academic_courses_lecturers(role)
    elif sub == "Assignments & Submissions":
        academic_assignments_submissions(role)
    elif sub == "Exams & Timetables":
        academic_exams_timetables(role)
    elif sub == "Grades & Analytics":
        academic_grades_analytics(role)
    elif sub == "Attendance Tracker":
        academic_attendance_tracker(role)
    elif sub == "Parent Portal":
        academic_parent_portal(role)
    elif sub == "Loan / Scholarship Tracker":
        academic_loan_scholarship_tracker(role)
    elif sub == "Academic Calendar":
        academic_calendar(role)


def academic_courses_lecturers(role: str):
    _section_card(
        "Courses & Lecturers",
        "Manage courses, lecturers, materials, and schedules.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Course materials")
        if role in ("Teacher", "Institution", "Super Admin"):
            st.write("Upload notes, PDFs, slides, and videos.")
            st.file_uploader(
                "Upload course material",
                type=["pdf", "ppt", "pptx", "docx", "mp4"],
                key="course_material_uploader",
            )
            # TODO: save metadata & file reference in DB
        else:
            st.info("Only teachers/institution staff can upload materials.")

    with col2:
        st.markdown("#### AI-assisted lesson planning")
        if role in ("Teacher", "Institution", "Super Admin"):
            st.write("Draft lesson plans from topics, objectives, and duration.")
            topic = st.text_input("Topic / unit")
            objectives = st.text_area("Learning objectives")
            duration = st.selectbox(
                "Lesson duration",
                ["30 minutes", "45 minutes", "60 minutes", "90 minutes"],
            )
            if st.button("Generate AI lesson plan"):
                # TODO: call your AI backend here
                st.info("AI lesson planner output will appear here (placeholder).")
        else:
            st.info("Lesson planning is available to teachers only.")

    st.markdown("#### Lecture schedules")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Define and view lecture schedules for each course.")
        st.text_input("Course code / name", key="course_schedule_course")
        st.date_input("Lecture date", key="course_schedule_date")
        st.time_input("Start time", key="course_schedule_time")
        # TODO: write schedule to DB and show table of schedules
    else:
        st.write("View-only timetables will be shown in the Exams & Timetables module.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- NEW: marking helpers ----------
def _init_marking_state():
    """Ensure marking session state is initialised."""
    if "mark_counts" not in st.session_state:
        st.session_state.mark_counts = {
            "green_ticks": 0,
            "red_crosses": 0,
            "stars": 0,
            "red_circles": 0,
        }
    if "marking_log" not in st.session_state:
        st.session_state.marking_log = []
    if "marks_df" not in st.session_state:
        demo_students = [
            {"name": "Student A", "reg_no": "REG001", "score": 0, "comment": ""},
            {"name": "Student B", "reg_no": "REG002", "score": 0, "comment": ""},
            {"name": "Student C", "reg_no": "REG003", "score": 0, "comment": ""},
        ]
        st.session_state.marks_df = pd.DataFrame(demo_students)


def _increment_symbol(symbol_key: str, label: str):
    st.session_state.mark_counts[symbol_key] += 1
    st.session_state.marking_log.append(label)


def _get_feedback_template(score_percent: float) -> str:
    if score_percent < 10:
        return "Your performance in this assessment is very low. Please meet your teacher for guidance and create a recovery plan."
    elif score_percent < 20:
        return "You have scored below 20%. Extra effort and practice are needed. Focus on understanding core concepts first."
    elif score_percent < 30:
        return "You are still far below the pass mark. Revisit the notes, redo past questions, and ask for help where needed."
    elif score_percent < 40:
        return "You are improving but still below average. Keep practicing, attend revision sessions, and ask questions in class."
    elif score_percent < 50:
        return "You are close to the pass range, but more consistency is required. Revise regularly and avoid last‑minute reading."
    elif score_percent < 60:
        return "Fair performance. You passed, but there is big room for improvement. Aim for clearer understanding, not just memorising."
    elif score_percent < 70:
        return "Good work. You are above average. Strengthen weak areas and maintain disciplined study to move to the top tier."
    elif score_percent < 80:
        return "Very good performance. Keep up the effort and continue practising higher‑order questions to polish your skills."
    elif score_percent < 90:
        return "Excellent score. You are performing at a high level. Keep challenging yourself with advanced problems."
    else:
        return "Outstanding performance. Congratulations on your hard work and discipline. Keep maintaining this standard."

def _pdf_viewer(pdf_bytes: bytes, height: int = 600):
    """Simple iframe PDF viewer, no pdf2image/poppler needed."""
    if not pdf_bytes:
        st.info("No PDF loaded.")
        return

    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_html = f"""
        <iframe src="data:application/pdf;base64,{b64}"
                width="100%" height="{height}" style="border:none;">
        </iframe>
    """
    st.markdown(pdf_html, unsafe_allow_html=True)

def academic_assignments_submissions(role: str):
    _section_card(
        "Assignments & Submissions",
        "Create assignments, accept submissions, and manage grading.",
    )

    st.markdown("#### Upload & download submissions")
    st.write("Teachers create assignments; students upload submissions.")

    # ------------------------------------------------------------------
    # TEACHER VIEW
    # ------------------------------------------------------------------
    if role == "Teacher":
        # Assignment creation (existing behaviour)
        st.text_input("Assignment title", key="assign_title")
        st.text_area("Assignment instructions", key="assign_instructions")
        st.date_input("Due date", key="assign_due")
        st.number_input("Max points", min_value=1, value=100, step=1, key="assign_mp")
        st.selectbox("Status", ["Draft", "Published"], key="assign_status")
        if st.button("Publish assignment"):
            # TODO: call create_assignment_db(...) here with teacher_id
            st.success("Assignment published (placeholder).")

        st.markdown("---")
        st.markdown("### Whiteboard-style marking workspace")

        uploaded_pdf = st.file_uploader(
            "Load a student's PDF script (demo)",
            type=["pdf"],
            key="teacher_mark_pdf",
        )

        if uploaded_pdf is None:
            st.info("Upload a PDF script to view and annotate it here.")
        else:
            # ---- Render first page of real script as background image ----
            pdf_bytes = uploaded_pdf.read()
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                page = doc.load_page(0)  # first page only
                zoom = 2.0  # increase for higher resolution if needed
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                from PIL import Image
                import io as _io

                bg_image = Image.open(_io.BytesIO(img_bytes))
                canvas_width, canvas_height = bg_image.size
            except Exception as e:
                st.error(f"Could not render PDF page: {e}")
                bg_image = None
                canvas_width, canvas_height = 800, 600

            st.markdown("#### Student script (PDF view)")
            if bg_image is not None:
                st.image(bg_image, use_container_width=True)
            else:
                st.info(
                    "PDF uploaded, but preview failed. You can still mark on a blank canvas."
                )

            st.markdown("#### Marking canvas on real script")

            # ---- Init symbol state ----
            if "overlay_marks" not in st.session_state:
                st.session_state.overlay_marks = []  # list of {symbol, x, y}
            if "click_cycle" not in st.session_state:
                st.session_state.click_cycle = 0  # 0→tick,1→cross,2→circle

            st.caption(
                "Click directly on the script page to place symbols: "
                "1st click = green tick, 2nd = red cross, 3rd = red circle (then repeats)."
            )

            # Current background: real script page if available, else plain white
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",
                stroke_width=2,
                stroke_color="#00FF00",
                background_color="#FFFFFF" if bg_image is None else None,
                background_image=bg_image if bg_image is not None else None,
                update_streamlit=True,
                height=canvas_height,
                width=canvas_width,
                drawing_mode="point",  # each click = one point
                key="pdf_mark_canvas",
            )

            # ---- Detect new click and assign symbol automatically ----
            if canvas_result.json_data is not None:
                objects = canvas_result.json_data.get("objects", [])
                # We only care when a new point is added
                if len(objects) > len(st.session_state.overlay_marks):
                    last_obj = objects[-1]
                    cx = last_obj.get("left", 0)
                    cy = last_obj.get("top", 0)

                    # Decide symbol based on click cycle
                    cycle = st.session_state.click_cycle % 3
                    if cycle == 0:
                        symbol = "small_green_tick"
                    elif cycle == 1:
                        symbol = "small_red_cross"
                    else:
                        symbol = "red_circle"
                    st.session_state.click_cycle = cycle + 1

                    st.session_state.overlay_marks.append(
                        {
                            "symbol": symbol,
                            "page": 1,
                            "x": cx,
                            "y": cy,
                        }
                    )
                    st.success(f"Placed {symbol} at ({cx:.1f}, {cy:.1f}) on page 1.")

            if st.session_state.overlay_marks:
                st.markdown("#### Recorded marks (this session)")
                for i, m in enumerate(st.session_state.overlay_marks, start=1):
                    st.write(
                        f"{i}. {m['symbol']} – page {m['page']} at "
                        f"({m['x']:.1f}, {m['y']:.1f})"
                    )
                if st.button("Clear marks for this script"):
                    st.session_state.overlay_marks = []
                    st.session_state.click_cycle = 0
                    st.experimental_rerun()

    # ------------------------------------------------------------------
    # STUDENT VIEW
    # ------------------------------------------------------------------
    elif role == "Student":
        st.file_uploader(
            "Upload your submission", type=["pdf", "docx", "zip"], key="sub_upload"
        )
        if st.button("Submit assignment"):
            # TODO: call save_submission_db(...) here with current user id
            st.success("Submission received (placeholder).")

        st.markdown("#### My results and marked scripts")
        st.info(
            "Here you will see your score, feedback, and a PDF viewer with "
            "the teacher's symbols overlaid (to be implemented using saved marks)."
        )

    else:
        st.info("Assignments are managed between teachers and students only.")

    # ------------------------------------------------------------------
    # Keep existing auto-grading & feedback
    # ------------------------------------------------------------------
    st.markdown("#### Auto grading / AI scoring")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Objective questions and quizzes can be auto-graded with AI.")
        if st.button("Run auto-grading (demo)"):
            # TODO: integrate auto-grading logic
            st.info("Auto-grading engine output will appear here (placeholder).")
    else:
        st.info("Auto-grading controls are for academic staff.")

    st.markdown("#### Teacher feedback & results")
    if role == "Teacher":
        st.write("Teachers enter feedback; students view their results.")
        st.text_area("Feedback (teacher view demo)", key="feedback_demo")
    elif role == "Student":
        st.write("You will see your feedback and marks here.")
    else:
        st.info("Feedback tools are primarily for teachers and their students.")

    st.markdown("</div>", unsafe_allow_html=True)










def academic_exams_timetables(role: str):
    _section_card(
        "Exams & Timetables",
        "Plan exam schedules, host quizzes/tests, and publish results.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Exam schedules")
        if role in ("Teacher", "Institution", "Super Admin"):
            st.write("Create exam timetable entries.")
            st.text_input("Exam name", key="exam_name")
            st.date_input("Exam date", key="exam_date")
            st.time_input("Exam time", key="exam_time")
            # TODO: save exam schedule to DB
        else:
            st.write("You can view exam timetables assigned to you.")
            # TODO: show read-only timetables

    with col2:
        st.markdown("#### Online quizzes / tests")
        if role in ("Teacher", "Institution"):
            st.write("Host small MCQ/online tests inside Sanzad Campus Hub.")
            st.text_input("Quiz title", key="quiz_title")
            if st.button("Start sample quiz"):
                # TODO: build quiz UI and scoring
                st.info("Quiz UI will appear here (placeholder).")
        elif role == "Student":
            st.write("Join quizzes created for your courses.")
            # TODO: list active quizzes for this student
        else:
            st.info("Quizzes are mainly for teachers and students.")

    st.markdown("#### Exam results / transcripts")
    if role in ("Institution", "Super Admin", "Teacher"):
        st.write("Search and view exam results and transcripts.")
        st.text_input("Student registration number", key="transcript_reg")
        if st.button("View transcript (demo)"):
            # TODO: fetch grades and generate transcript
            st.info("Transcript viewer will display here (placeholder).")
    elif role == "Student":
        st.write("View your own transcript here.")
        # TODO: automatically fetch student's results
    elif role == "Parent":
        st.write("View your child's transcript (linked to child reg).")
        # TODO: fetch child transcript
    else:
        st.info("Transcript access is limited to academic roles and parents.")

    st.markdown("</div>", unsafe_allow_html=True)


def academic_grades_analytics(role: str):
    _section_card(
        "Grades & Analytics",
        "Gradebook, GPA, and performance dashboards.",
    )

    st.markdown("#### Gradebook")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Tabular view of assignments, exams, and scores per course.")
        # TODO: list grades for class/department
    elif role == "Student":
        st.write("View your personal gradebook.")
        # TODO: list only this student's grades
    elif role == "Parent":
        st.write("View your child's gradebook.")
        # TODO: list child's grades
    else:
        st.info("Gradebook access is limited to academic roles and parents.")

    st.markdown("#### GPA calculation")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Compute GPA for a student per semester and cumulative.")
        st.text_input("Student registration number", key="gpa_reg")
        if st.button("Calculate GPA"):
            # TODO: implement GPA logic using grades table
            st.info("GPA calculation logic will run here (placeholder).")
    elif role == "Student":
        st.write("Your GPA summary will appear here.")
        if st.button("Calculate my GPA"):
            # TODO: use logged-in student id
            st.info("Personal GPA calc will run here (placeholder).")
    else:
        st.info("GPA tools are available for academic roles and students.")

    st.markdown("#### Student performance analytics")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Charts and trends for performance over time and by course.")
        st.info("Analytics charts will be added here later (placeholder).")
    elif role == "Student":
        st.write("Visualize your performance in different courses.")
        st.info("Personal analytics will appear here (placeholder).")
    else:
        st.info("Performance analytics are targeted to academic users.")

    st.markdown("</div>", unsafe_allow_html=True)


def academic_attendance_tracker(role: str):
    _section_card(
        "Attendance Tracker",
        "Smart attendance with QR check-in and analytics.",
    )

    st.markdown("#### QR check-in / smart class attendance")
    st.write("Teachers generate QR; students scan to mark attendance.")
    if role == "Teacher":
        if st.button("Generate attendance QR (demo)"):
            # TODO: generate real QR with session token
            st.info("QR code would be displayed here (placeholder).")
    elif role == "Student":
        st.text_input("Scan/enter QR token (demo)", key="qr_token")
        if st.button("Mark attendance (demo)"):
            # TODO: validate token and mark attendance in DB
            st.success("Attendance marked (placeholder).")
    else:
        st.info("Attendance controls are for teachers and students.")

    st.markdown("#### Attendance analytics")
    if role in ("Teacher", "Institution", "Super Admin"):
        st.write("Monthly attendance summaries and alerts for classes.")
        st.info("Attendance charts and alerts will be shown here (placeholder).")
    elif role == "Student":
        st.write("Check your own attendance record.")
        # TODO: show student's attendance
    elif role == "Parent":
        st.write("View your child's attendance record.")
        # TODO: show child's attendance
    else:
        st.info("Attendance analytics are limited to academic and parent roles.")

    st.markdown("</div>", unsafe_allow_html=True)


def academic_parent_portal(role: str):
    _section_card(
        "Parent Portal",
        "Parents/guardians monitor student progress and communicate.",
    )

    if role == "Parent":
        st.markdown("#### View student progress")
        st.text_input("Child's registration number", key="parent_child_reg_view")
        if st.button("View progress (demo)"):
            # TODO: fetch child's grades and attendance
            st.info("Progress dashboard will appear here (placeholder).")

        st.markdown("#### Communicate with lecturers")
        st.text_area("Message to lecturer", key="parent_message")
        if st.button("Send message to lecturer (demo)"):
            # TODO: send message to a messaging table
            st.success("Message sent (placeholder).")

        st.markdown("#### Access announcements")
        st.write("View key announcements related to your child.")
        st.info("Announcements feed will appear here (placeholder).")
    else:
        st.info("Parent Portal is primarily for Parent accounts.")

    st.markdown("</div>", unsafe_allow_html=True)


def academic_loan_scholarship_tracker(role: str):
    _section_card(
        "Loan / Scholarship Tracker",
        "Track HELB and other loans/scholarships.",
    )

    st.markdown("#### HELB or external loan info")
    if role in ("Student", "Parent", "Institution", "Super Admin"):
        st.text_input("Loan account / reference number", key="loan_ref")
        if st.button("Fetch loan status (demo)"):
            # TODO: integrate external APIs or local tracking
            st.info("Loan status integration will show here (placeholder).")
    else:
        st.info("Loan information is available to students, parents, and admins.")

    st.markdown("#### Application & status updates")
    if role in ("Student", "Parent"):
        st.write("Record applications and follow status updates.")
        st.text_area("New application notes (demo)", key="loan_application_notes")
        # TODO: save records in a loans table
    else:
        st.write("Applications are typically created by students or on their behalf.")

    st.markdown("#### Scholarship opportunities")
    st.write("List scholarships filtered by course, country, or academic level.")
    st.info("Scholarship listings will be displayed here (placeholder).")

    st.markdown("</div>", unsafe_allow_html=True)


def academic_calendar(role: str):
    _section_card(
        "Academic Calendar",
        "Semester dates, holidays, and exam periods.",
    )

    st.markdown("#### Semester dates")
    if role in ("Institution", "Super Admin"):
        st.date_input("Semester start", key="sem_start")
        st.date_input("Semester end", key="sem_end")
        # TODO: write semester info to DB
    else:
        st.write("View only: semester dates will be shown here.")
        # TODO: show read-only dates

    st.markdown("#### Holidays & events")
    if role in ("Institution", "Super Admin"):
        st.text_input("Holiday / event name", key="holiday_name")
        st.date_input("Holiday / event date", key="holiday_date")
        # TODO: append to calendar table and show list
    else:
        st.write("Institution-defined holidays will appear here.")

    st.markdown("#### Exam periods")
    if role in ("Institution", "Super Admin"):
        st.date_input("Exam period start", key="exam_period_start")
        st.date_input("Exam period end", key="exam_period_end")
        # TODO: connect with exam schedules for full calendar view
    else:
        st.write("Exam periods will be visible here as read-only.")

    st.info("A full calendar view will be integrated here later (placeholder).")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 2. STUDENT SERVICES WING
# -------------------------------------------------------------------
def student_services_wing(role: str):
    st.markdown("### 2. Student Services Wing")

    sub = st.selectbox(
        "Choose a Student Services module",
        [
            "Lost & Found",
            "Housing & Hostels",
            "Transport & Routes",
            "Health & Wellbeing",
            "Campus Map",
            "Institutional Services",
        ],
        key="student_services_sub",
    )

    if sub == "Lost & Found":
        services_lost_found(role)
    elif sub == "Housing & Hostels":
        services_housing_hostels(role)
    elif sub == "Transport & Routes":
        services_transport_routes(role)
    elif sub == "Health & Wellbeing":
        services_health_wellbeing(role)
    elif sub == "Campus Map":
        services_campus_map(role)
    elif sub == "Institutional Services":
        services_institutional(role)


def services_lost_found(role: str):
    _section_card(
        "Lost & Found",
        "Report lost/found items and manage claims.",
    )

    st.markdown("#### Report lost/found item")
    if role in ("Student", "Teacher", "Parent", "Institution", "Security", "Super Admin"):
        st.text_input("Item name", key="lf_item_name")
        st.selectbox("Type", ["Lost", "Found"], key="lf_type")
        st.text_area("Description", key="lf_description")
        st.file_uploader("Upload photo", type=["png", "jpg", "jpeg"], key="lf_photo")
        if st.button("Submit lost/found report"):
            # TODO: insert into lost_found table with user_id
            st.success("Report submitted (placeholder).")
    else:
        st.info("Lost & Found is for campus users only.")

    st.markdown("#### Claim verification")
    if role in ("Institution", "Security", "Super Admin"):
        st.write("Admins/security verify claims and mark items as resolved.")
        # TODO: show list of open items for admins / security
    else:
        st.write("Verification is handled by institution/security teams.")

    st.markdown("</div>", unsafe_allow_html=True)


def services_housing_hostels(role: str):
    _section_card(
        "Housing & Hostels",
        "On-campus rooms, off-campus rentals, and maintenance.",
    )

    st.markdown("#### On-campus rooms")
    st.write("Browse and apply for on-campus rooms.")
    # TODO: show room list from DB

    st.markdown("#### Off-campus rentals")
    if role in ("Student", "Teacher", "Parent", "Institution", "Super Admin"):
        st.write("List or find off-campus rentals.")
        # TODO: create housing listings table and forms
    else:
        st.info("Off-campus rentals are for campus community users.")

    st.markdown("#### Maintenance requests")
    if role in ("Student", "Teacher", "Institution", "Super Admin"):
        st.text_area("Describe maintenance issue", key="maint_issue")
        if st.button("Submit maintenance request"):
            # TODO: insert into maintenance_requests table
            st.success("Maintenance request submitted (placeholder).")
    else:
        st.info("Maintenance requests are limited to residents and staff.")

    st.markdown("</div>", unsafe_allow_html=True)


def services_transport_routes(role: str):
    _section_card(
        "Transport & Routes",
        "Shuttle schedules, real-time updates, and booking.",
    )

    st.markdown("#### Shuttle schedules")
    st.write("View shuttle and bus schedules.")
    # TODO: show schedules from DB

    st.markdown("#### Real-time bus updates")
    st.info("Real-time tracking integration can be added here (placeholder).")

    st.markdown("#### Campus shuttle booking")
    if role in ("Student", "Teacher", "Parent", "Institution"):
        st.text_input("Pickup location", key="pickup_location")
        st.text_input("Destination", key="destination")
        if st.button("Book shuttle (demo)"):
            # TODO: insert booking into transport_bookings table
            st.success("Shuttle booked (placeholder).")
    else:
        st.info("Shuttle booking is for campus community only.")

    st.markdown("</div>", unsafe_allow_html=True)


def services_health_wellbeing(role: str):
    _section_card(
        "Health & Wellbeing",
        "First aid, counseling, and emergency support.",
    )

    st.markdown("#### First aid guidance")
    if role in ("Student", "Teacher", "Parent", "Institution", "Security"):
        st.text_area("Describe symptoms or situation", key="fa_symptoms")
        if st.button("Get first aid guidance (demo)"):
            # TODO: call first-aid AI / rules engine
            st.info("First-aid guidance will appear here (placeholder).")
    else:
        st.info("First aid guidance is for campus community users.")

    st.markdown("#### Counseling requests")
    if role in ("Student", "Teacher", "Parent"):
        st.text_area("Counseling request details", key="counsel_request")
        if st.button("Request counseling (demo)"):
            # TODO: insert into counseling_requests table
            st.success("Counseling request submitted (placeholder).")
    else:
        st.info("Counseling is available for students, staff, and parents.")

    st.markdown("#### Panic / emergency button")
    if role in ("Student", "Teacher", "Parent", "Institution", "Security"):
        if st.button("Trigger emergency (demo)"):
            # TODO: insert into emergencies table with user & location
            st.error("Emergency alert triggered (placeholder).")
    else:
        st.info("Emergency button is disabled for this role.")

    st.markdown("</div>", unsafe_allow_html=True)


def services_campus_map(role: str):
    _section_card(
        "Campus Map",
        "Interactive campus navigation for new and existing students.",
    )

    st.markdown("#### Locations")
    st.write(
        "Hostels, libraries, labs, admin offices, departments and more can be shown here."
    )
    # TODO: integrate a map widget or static map images

    if role in ("Institution", "Super Admin"):
        st.markdown("#### Manage locations")
        st.text_input("New location name", key="map_loc_name")
        st.text_area("Description", key="map_loc_desc")
        if st.button("Add / update location (demo)"):
            # TODO: add/update in locations table
            st.success("Location saved (placeholder).")

    st.info("Interactive map UI will be integrated here (placeholder).")

    st.markdown("</div>", unsafe_allow_html=True)


def services_institutional(role: str):
    _section_card(
        "Institutional Services",
        "Cafeteria, hostels, library, transport, and labs.",
    )

    st.markdown("#### Cafeteria (menus, pricing, orders)")
    if role == "Institution":
        st.write("Manage cafeteria menus and prices.")
        st.text_input("Meal name", key="caf_meal_name")
        st.number_input("Price", min_value=0.0, step=1.0, key="caf_price")
        st.selectbox("Availability", ["Available", "Out of stock"], key="caf_status")
        if st.button("Save menu item (demo)"):
            # TODO: write to cafeteria_menu table
            st.success("Menu item saved (placeholder).")
    else:
        st.write("View cafeteria menu and prices.")
        # TODO: show read-only cafeteria menu
        if role == "Student":
            st.number_input("Quantity", min_value=1, value=1, key="caf_qty")
            if st.button("Place order (demo)"):
                # TODO: create cafeteria order, optional payment link
                st.success("Order placed (placeholder).")

    st.markdown("#### Hostels (allocations, rules, payments)")
    if role == "Institution":
        st.write("Manage hostel allocations, rules, and fees.")
        # TODO: admin forms for allocations & hostel fees
    elif role == "Student":
        st.write("View your hostel allocation and payment status.")
        # TODO: show student's hostel record
    elif role == "Parent":
        st.write("View your child's hostel status and related fees (read-only).")
        # TODO: child-linked view

    st.markdown("#### Library, transport, and labs (institution-managed)")
    if role == "Institution":
        st.write("Configure library rules, transport schedules, and lab usage rules.")
        # TODO: configuration UIs
    else:
        st.write("View institution-defined schedules, rules, and availability.")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 3. MARKETPLACE WING
# -------------------------------------------------------------------
def marketplace_wing(role: str):
    st.markdown("### 3. Marketplace Wing")

    # Marketplace accessible to students only
    if role != "Student":
        st.info("Marketplace is only accessible to students.")
        return

    sub = st.selectbox(
        "Choose a Marketplace module",
        [
            "Buy/Sell Products",
            "Campus Services",
            "Jobs & Internships",
        ],
        key="marketplace_sub",
    )

    if sub == "Buy/Sell Products":
        market_buy_sell(role)
    elif sub == "Campus Services":
        market_campus_services(role)
    elif sub == "Jobs & Internships":
        market_jobs_internships(role)


def market_buy_sell(role: str):
    _section_card(
        "Buy/Sell Products",
        "Student-to-student marketplace for items.",
    )

    # Only students reach here because of marketplace_wing guard
    st.markdown("#### Post your business / product")
    st.text_input("Item / business name", key="biz_item_name")
    st.text_area("Description", key="biz_item_desc")
    st.number_input("Price", min_value=0.0, step=1.0, key="biz_item_price")
    st.file_uploader(
        "Upload photo", type=["png", "jpg", "jpeg"], key="biz_item_photo"
    )
    if st.button("Submit listing (demo)"):
        # TODO: insert listing with owner_id=current_student_id
        st.success("Listing submitted and visible to other students (placeholder).")

    st.markdown("#### Browse items and chat with sellers")
    st.info(
        "In production, load items from DB and for each one show a "
        "'Chat seller' button that opens a private chat thread between "
        "buyer and seller only, with no institution involvement."
    )

    # Demo chat thread (static seller)
    if st.button("Open demo chat with seller"):
        _demo_chat_ui("demo_market_chat", "Seller (Student)")

    st.markdown("</div>", unsafe_allow_html=True)


def market_campus_services(role: str):
    _section_card(
        "Campus Services",
        "Service marketplace for tutoring, printing, food, etc.",
    )

    # Still student‑only because marketplace_wing blocks other roles
    st.markdown("#### Offer a service")
    st.text_input("Service name", key="service_name")
    st.text_area("Service description", key="service_desc")
    st.number_input("Price / rate", min_value=0.0, step=1.0, key="service_price")
    if st.button("Publish service (demo)"):
        # TODO: insert into services table with owner_id=current_student_id
        st.success("Service published (placeholder).")

    st.markdown("#### Browse services")
    st.write("Tutoring, printing, photocopying, food delivery and more.")
    st.info(
        "For each service, you can show a 'Chat provider' button that opens "
        "a direct chat thread with the student who offers it."
    )
    # TODO: query and display services table

    st.markdown("</div>", unsafe_allow_html=True)


def market_jobs_internships(role: str):
    _section_card(
        "Jobs & Internships",
        "Part-time jobs, internships, and volunteer opportunities.",
    )

    st.markdown("#### Browse opportunities")
    st.write("View jobs, internships, and volunteer roles.")
    # TODO: query and display jobs table for students

    st.info(
        "If you later want staff to post jobs, create a different posting UI "
        "under Institution dashboards, but keep viewing here for students."
    )

    st.markdown("</div>", unsafe_allow_html=True)



# -------------------------------------------------------------------
# 4. SECURITY & SAFETY WING
# -------------------------------------------------------------------
def security_safety_wing(role: str):
    st.markdown("### 4. Security & Safety Wing")

    sub = st.selectbox(
        "Choose a Security & Safety module",
        [
            "Panic / Emergency Button",
            "Smart ID & Access Control",
            "Campus Alerts & Logs",
        ],
        key="security_sub",
    )

    if sub == "Panic / Emergency Button":
        security_panic_button(role)
    elif sub == "Smart ID & Access Control":
        security_smart_id(role)
    elif sub == "Campus Alerts & Logs":
        security_campus_alerts(role)


def security_panic_button(role: str):
    _section_card(
        "Panic / Emergency Button",
        "Instant alerts to admin with user role and location.",
    )

    if role in ("Student", "Teacher", "Parent", "Institution", "Security"):
        if st.button("Trigger emergency (demo)", key="security_panic"):
            # TODO: insert into emergencies table with location, role, time
            st.error("Emergency alert triggered (placeholder).")
    else:
        st.info("Emergency button is disabled for this role.")

    st.markdown("</div>", unsafe_allow_html=True)


def security_smart_id(role: str):
    _section_card(
        "Smart ID & Access Control",
        "Digital IDs and QR-based building access.",
    )

    st.markdown("#### Scan / show QR")
    if role == "Security":
        st.write("Scan student QR codes at campus entry points.")
        st.text_input("Scan QR token (demo)", key="sec_qr_token")
        if st.button("Lookup student (demo)"):
            # TODO: fetch and show name, department, year, photo, status
            st.info("Student details will appear here (placeholder).")
    elif role in ("Student", "Teacher", "Institution"):
        st.write("Show your digital ID and QR code for entry.")
        # TODO: display QR linked to current user_code
    else:
        st.info("Smart ID is only for campus members and security staff.")

    st.markdown("#### Entry/exit logs")
    if role in ("Security", "Institution", "Super Admin"):
        st.write("View logs of entries and exits (for security monitoring).")
        # TODO: show access_logs table
    else:
        st.info("Access logs are visible to security and institution admins.")

    st.markdown("</div>", unsafe_allow_html=True)


def security_campus_alerts(role: str):
    _section_card(
        "Campus Alerts & Logs",
        "View emergency alerts and security logs.",
    )

    st.markdown("#### Emergency alerts")
    if role in ("Security", "Institution", "Super Admin"):
        st.write("View and acknowledge panic/emergency alerts.")
        # TODO: list emergencies where status='Open'
    else:
        st.info("Emergency alert consoles are for security and admins.")

    st.markdown("#### Send security alerts")
    if role in ("Institution", "Super Admin"):
        st.text_input("Alert title", key="sec_alert_title")
        st.text_area("Alert message", key="sec_alert_msg")
        if st.button("Broadcast security alert (demo)"):
            # TODO: insert into alerts table
            st.success("Security alert broadcasted (placeholder).")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 5. SOCIAL & COMMUNITY WING
# -------------------------------------------------------------------
def social_community_wing(role: str):
    st.markdown("### 5. Social & Community Wing")

    sub = st.selectbox(
        "Choose a Social & Community module",
        [
            "Clubs & Societies",
            "Campus Events Calendar",
            "Polls & Voting",
            "Community Boards",
        ],
        key="social_sub",
    )

    if sub == "Clubs & Societies":
        social_clubs(role)
    elif sub == "Campus Events Calendar":
        social_events_calendar(role)
    elif sub == "Polls & Voting":
        social_polls_voting(role)
    elif sub == "Community Boards":
        social_community_boards(role)


def social_clubs(role: str):
    _section_card(
        "Clubs & Societies",
        "Register, approve, and join campus clubs.",
    )

    if role == "Student":
        st.markdown("#### Join clubs")
        st.write("Browse and request to join existing clubs.")
        # TODO: list clubs with 'Request to join' button
    elif role == "Institution":
        st.markdown("#### Approve club requests")
        st.write("Approve or reject new club registrations and join requests.")
        # TODO: list pending clubs/join requests with Approve/Reject
    elif role in ("Teacher", "Parent"):
        st.markdown("#### Join clubs")
        st.write("Browse and join approved clubs.")
        # TODO: list clubs & join
    else:
        st.info("Club tools are for campus community and institution admins.")

    st.markdown("</div>", unsafe_allow_html=True)


def social_events_calendar(role: str):
    _section_card(
        "Campus Events Calendar",
        "Academic, cultural, and sports events.",
    )

    if role in ("Institution", "Super Admin"):
        st.markdown("#### Create institutional event")
        st.text_input("Event title", key="event_title")
        st.date_input("Event date", key="event_date")
        st.text_area("Event details", key="event_details")
        if st.button("Publish event (demo)"):
            # TODO: insert event into events table
            st.success("Event published (placeholder).")
    else:
        st.info("Only institution admins can publish official events.")

    st.markdown("#### Upcoming events")
    st.write("List of upcoming events will appear here.")
    # TODO: query events table

    st.markdown("</div>", unsafe_allow_html=True)


def social_polls_voting(role: str):
    _section_card(
        "Polls & Voting",
        "Run institution elections and polls with role-based access.",
    )

    st.markdown("#### Your access level")
    st.write(f"Current role: **{role}**")

    if role in ("Institution", "Super Admin"):
        st.markdown("##### Create new election / poll")

        poll_title = st.text_input("Title")
        poll_desc = st.text_area("Description or election rules")

        target_group = st.selectbox(
            "Target group",
            ["Students only", "Staff only", "Students & Staff"],
            help="Select who is allowed to vote.",
        )

        is_anonymous = st.checkbox(
            "Anonymous voting",
            value=True,
            help="If checked, voter identities are not visible even to admins.",
        )

        options_raw = st.text_area(
            "Options (one per line)",
            help="Example:\nCandidate A\nCandidate B\nAbstain",
        )

        if st.button("Create poll / election"):
            # TODO: insert into polls table with target group, flags, etc.
            st.success("Poll / election created (placeholder).")

        st.markdown("##### Manage polls and view results")
        st.write(
            "View live results, close polls, and archive elections. "
            "Results remain hidden from students."
        )
        # TODO: list polls, show vote counts, add Close/Archive actions

    elif role == "Student":
        st.markdown("##### Elections / polls for you")
        st.info("You can vote in active elections. Results are hidden from students.")
        # TODO: fetch polls targeted to students
        st.write("Demo election: **Student Council 2025**")
        choice = st.radio(
            "Choose your candidate",
            ["Candidate A", "Candidate B", "Abstain"],
            key="stud_election_choice",
        )
        if st.button("Submit vote"):
            # TODO: insert into votes table
            st.success("Your vote has been recorded (placeholder).")

    elif role == "Teacher":
        st.markdown("##### Departmental polls (non-election)")
        st.info(
            "Use this for feedback or departmental decisions, "
            "not for campus-wide elections."
        )
        question = st.text_input("Poll question", key="dept_poll_q")
        options = st.text_area("Options (one per line)", key="dept_poll_opts")
        if st.button("Create departmental poll (demo)"):
            # TODO: insert departmental poll
            st.success("Departmental poll created (placeholder).")

        st.markdown("##### Active staff polls")
        st.write("You can respond to staff polls when available.")
        # TODO: fetch polls targeted to staff

    else:
        st.info(
            "Polls & Voting is mainly for institution elections (admins) "
            "and voting for students/staff."
        )

    st.markdown("</div>", unsafe_allow_html=True)


def social_community_boards(role: str):
    _section_card(
        "Community Boards",
        "Discussions, announcements, and peer support.",
    )

    if role in ("Student", "Teacher", "Parent", "Institution"):
        st.markdown("#### New post")
        st.text_input("Title", key="board_title")
        st.text_area("Message", key="board_message")
        if st.button("Post message (demo)"):
            # TODO: insert into community_board table
            st.success("Post published (placeholder).")
    else:
        st.info("Posting is limited to campus community users.")

    st.markdown("#### Recent posts")
    st.write("Recent community posts will appear here.")
    # TODO: query posts table

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 6. ENVIROTECH WING
# -------------------------------------------------------------------
def envirotech_wing(role: str):
    st.markdown("### 6. EnviroTech Wing")

    sub = st.selectbox(
        "Choose an EnviroTech module",
        [
            "Pollution / Environmental Reporting",
            "Waste Management AI",
            "Energy Monitoring",
        ],
        key="enviro_sub",
    )

    if sub == "Pollution / Environmental Reporting":
        enviro_pollution_reporting(role)
    elif sub == "Waste Management AI":
        enviro_waste_management_ai(role)
    elif sub == "Energy Monitoring":
        enviro_energy_monitoring(role)


def enviro_pollution_reporting(role: str):
    _section_card(
        "Pollution / Environmental Reporting",
        "Report environmental issues (air, water, noise, dumping, wildlife).",
    )

    if role in ("Student", "Teacher", "Parent", "Institution"):
        st.selectbox(
            "Type of issue",
            ["Air", "Water", "Noise", "Dumping", "Wildlife", "Other"],
            key="env_issue_type",
        )
        st.text_area("Description", key="env_issue_desc")
        st.file_uploader(
            "Upload media (photo/audio)",
            type=["png", "jpg", "jpeg", "mp3", "wav"],
            key="env_issue_media",
        )
        if st.button("Submit environmental report (demo)"):
            # TODO: insert into env_reports table
            st.success("Environmental report submitted (placeholder).")
    else:
        st.info("EnviroTech reporting is primarily for campus community users.")

    st.markdown("</div>", unsafe_allow_html=True)


def enviro_waste_management_ai(role: str):
    _section_card(
        "Waste Management AI",
        "Smart bin mapping and recycling dashboards.",
    )

    if role in ("Institution", "Super Admin"):
        st.write("Smart bin locations and recycling stats will appear here.")
        # TODO: create and visualize waste management data
    else:
        st.info("Waste analytics is managed at institution/admin level.")

    st.markdown("</div>", unsafe_allow_html=True)


def enviro_energy_monitoring(role: str):
    _section_card(
        "Energy Monitoring",
        "Lab and campus electricity usage with anomaly alerts.",
    )

    if role in ("Institution", "Super Admin"):
        st.write("Energy usage charts and alerts will appear here.")
        # TODO: pull data (manual input or sensors) and visualize
    else:
        st.info("Energy monitoring is handled by institution/admin roles.")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 7. FINANCE & PAYMENTS WING
# -------------------------------------------------------------------
def finance_payments_wing(role: str):
    st.markdown("### 7. Finance & Payments Wing")

    sub = st.selectbox(
        "Choose a Finance & Payments module",
        [
            "Fees & Billing",
            "Payment Gateway",
            "Scholarship / Bursary Applications",
            "Campus Wallet",
            "Institution Financial Reports",
        ],
        key="finance_sub",
    )

    if sub == "Fees & Billing":
        finance_fees_billing(role)
    elif sub == "Payment Gateway":
        finance_payment_gateway(role)
    elif sub == "Scholarship / Bursary Applications":
        finance_scholarships(role)
    elif sub == "Campus Wallet":
        finance_wallet(role)
    elif sub == "Institution Financial Reports":
        finance_reports(role)


def finance_fees_billing(role: str):
    _section_card(
        "Fees & Billing",
        "Tuition, accommodation, and other charges.",
    )

    if role in ("Institution", "Super Admin"):
        st.text_input("Student registration number", key="fee_reg")
        if st.button("View fee statement (demo)"):
            # TODO: show fees from finance table
            st.info("Fee statement will appear here (placeholder).")
    elif role == "Student":
        st.write("View your own fee statement here.")
        if st.button("View my fees (demo)"):
            # TODO: auto-load student fees
            st.info("Your fee statement will appear here (placeholder).")
    elif role == "Parent":
        st.write("View your child's fee status here.")
        # TODO: child-based fee view
    else:
        st.info("Fees & billing is mainly for students, parents, and institution admins.")

    st.markdown("</div>", unsafe_allow_html=True)


def finance_payment_gateway(role: str):
    _section_card(
        "Payment Gateway",
        "Mobile money, bank, card, and international payments.",
    )

    if role in ("Student", "Parent", "Institution"):
        st.write("Integrate with payment providers here.")
        # TODO: hook into real payment APIs (e.g., mobile money, cards)
    else:
        st.info("Payments are available to students, parents, and institution admins.")

    st.markdown("</div>", unsafe_allow_html=True)


def finance_scholarships(role: str):
    _section_card(
        "Scholarship / Bursary Applications",
        "Apply for financial aid and track status.",
    )

    if role in ("Student", "Parent"):
        st.text_input("Student registration number", key="sch_reg")
        st.text_area("Application motivation", key="sch_motivation")
        if st.button("Submit scholarship application (demo)"):
            # TODO: insert into scholarships table
            st.success("Scholarship application submitted (placeholder).")
    else:
        st.info("Scholarship applications are mostly for students/parents.")

    st.markdown("</div>", unsafe_allow_html=True)


def finance_wallet(role: str):
    _section_card(
        "Campus Wallet",
        "Use wallet for marketplace purchases and event tickets.",
    )

    if role in ("Student", "Teacher", "Parent"):
        st.write("Wallet balance and transactions will appear here.")
        # TODO: implement wallet accounts, transactions, and balance
    else:
        st.info("Campus wallet is for individual campus users only.")

    st.markdown("</div>", unsafe_allow_html=True)


def finance_reports(role: str):
    _section_card(
        "Institution Financial Reports",
        "View institution-level or global financial analytics.",
    )

    if role in ("Institution", "Super Admin"):
        st.markdown("#### Service-level reports")
        st.multiselect(
            "Select services",
            ["Tuition", "Scholarships", "Cafeteria", "Hostels", "Marketplace"],
            default=["Tuition", "Marketplace"],
            key="fin_services",
        )
        if st.button("Generate report (demo)"):
            # TODO: aggregate from finance tables by service
            st.info("Financial report and charts will be displayed here (placeholder).")

        st.markdown("#### Audit logs / compliance")
        if role == "Super Admin":
            st.write("View global audit logs across institutions.")
        else:
            st.write("View audit logs for your institution.")
        # TODO: show audit log table filtered by institution/global
    else:
        st.info("Financial reports are restricted to institution admins and Super Admin.")

    # NEW: Super Admin institution control
    if role == "Super Admin":
        st.markdown("---")
        st.markdown("### Institution control (Super Admin only)")
        st.info(
            "Ban blocks login/access; delete should normally be a soft delete "
            "or archive for audit purposes."
        )

        inst_identifier = st.text_input(
            "Institution ID or code", key="inst_control_id"
        )

        col_ban, col_unban, col_delete = st.columns(3)
        with col_ban:
            if st.button("Ban institution", key="btn_ban_inst"):
                # TODO: update institutions set status='banned' where id=inst_identifier
                st.error(
                    f"Institution {inst_identifier} has been banned (placeholder)."
                )
        with col_unban:
            if st.button("Unban institution", key="btn_unban_inst"):
                # TODO: update institutions set status='active' where id=inst_identifier
                st.success(
                    f"Institution {inst_identifier} has been unbanned (placeholder)."
                )
        with col_delete:
            if st.button("Delete institution", key="btn_delete_inst"):
                # TODO: mark institution as archived/deleted in DB (soft delete)
                st.warning(
                    f"Institution {inst_identifier} marked for deletion (placeholder)."
                )

        st.caption(
            "Implementation tip: prefer status flags (active/banned/archived) "
            "instead of hard delete so you keep history and audit logs."
        )

    st.markdown("</div>", unsafe_allow_html=True)
