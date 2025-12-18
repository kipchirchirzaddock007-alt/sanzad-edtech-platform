import streamlit as st
import pandas as pd

def render(role: str):
    st.header("Analytics Module")
    st.write("High-level performance overview for Sanzad Global.")

    # --------------------------------
    # Load student data (base layer)
    # --------------------------------
    try:
        df_students = pd.read_csv("data/sample_students.csv")
    except FileNotFoundError:
        st.warning("Student data not found. Check data/sample_students.csv.")
        return

    # Top metrics
    col1, col2, col3 = st.columns(3)

    avg_progress = df_students["progress_score"].mean()
    num_students = len(df_students)
    active_today = (df_students["last_active"] == df_students["last_active"].max()).sum()

    col1.metric("Total Students", num_students)
    col2.metric("Average Progress", f"{avg_progress:.1f}%")
    col3.metric("Active Today", int(active_today))

    st.markdown("---")

    # Progress by grade
    st.subheader("Progress by Grade")
    grade_stats = df_students.groupby("grade")["progress_score"].mean().reset_index()
    st.bar_chart(grade_stats.set_index("grade"))

    # --------------------------------
    # Scholarship & Competition View
    # --------------------------------
    st.markdown("---")
    st.subheader("Scholarship & Competition Insights (Demo Rules)")

    # Simple demo thresholds – can be tuned later
    scholarship_threshold = 90
    risk_threshold = 75

    # Candidates for scholarships
    scholarship_candidates = df_students[df_students["progress_score"] >= scholarship_threshold]
    at_risk = df_students[df_students["progress_score"] <= risk_threshold]

    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Scholarship Threshold", f"{scholarship_threshold}%")
    col_s2.metric("At-Risk Threshold", f"{risk_threshold}%")

    st.write("")

    st.markdown("**Scholarship Candidates (progress >= threshold)**")
    if not scholarship_candidates.empty:
        st.dataframe(scholarship_candidates[["name", "grade", "progress_score"]])
    else:
        st.write("No students currently meet the scholarship threshold.")

    st.markdown("**At-Risk Students (progress <= threshold)**")
    if not at_risk.empty:
        st.dataframe(at_risk[["name", "grade", "progress_score"]])
    else:
        st.write("No students currently flagged as at-risk by this rule.")

    # --------------------------------
    # Future: link to Smart Teacher grades
    # --------------------------------
    st.markdown("---")
    st.subheader("Data Preview (Current Source)")
    st.dataframe(df_students)

    st.info(
        "Future steps: replace sample progress scores with real data from Smart Teacher "
        "grades and use AI models to refine scholarship and risk predictions."
    )
