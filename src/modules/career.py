import streamlit as st
import pandas as pd

def render(role: str):
    st.header("Career Module")
    st.write("Internships, jobs, skills, and certifications.")

    internships = [
        {"Company": "TechCorp", "Role": "Junior Developer", "Status": "Open"},
        {"Company": "EduGlobal", "Role": "Content Intern", "Status": "Applied"},
    ]
    df = pd.DataFrame(internships)

    st.subheader("Internships & Jobs")
    st.dataframe(df)

    st.markdown("---")
    st.subheader("Skill-Building Paths")
    st.write("- Python for Data & AI")
    st.write("- Teaching with Technology")
    st.write("- Global Communication Skills")

    st.markdown("---")
    st.subheader("Certifications")
    st.write("Future: auto-generate certificates based on achievements and course completions.")
