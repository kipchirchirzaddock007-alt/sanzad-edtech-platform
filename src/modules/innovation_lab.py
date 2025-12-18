import streamlit as st
import pandas as pd

def render(role: str):
    st.header("Innovation Lab")
    st.write("Hackathons, projects, funding, and collaboration.")

    if "projects" not in st.session_state:
        st.session_state.projects = []

    left, right = st.columns([2, 3])

    with left:
        st.subheader("Submit Project Idea")
        with st.form("project_form"):
            title = st.text_input("Project Title")
            stage = st.selectbox("Stage", ["Idea", "Building", "Prototype", "Launched"])
            summary = st.text_area("Short Summary")
            submitted = st.form_submit_button("Submit Project")
            if submitted:
                if not title.strip():
                    st.error("Project title is required.")
                else:
                    st.session_state.projects.append(
                        {"Title": title, "Stage": stage, "Summary": summary}
                    )
                    st.success("Project submitted.")

    with right:
        st.subheader("Projects (This Session)")
        if st.session_state.projects:
            df = pd.DataFrame(st.session_state.projects)
            st.dataframe(df)
        else:
            st.write("No projects submitted yet.")
