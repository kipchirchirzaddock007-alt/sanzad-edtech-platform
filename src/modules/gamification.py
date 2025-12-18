import streamlit as st
import pandas as pd

def render(role: str):
    st.header("Gamification")
    st.write("Points, leaderboards, and rewards for Sanzad Global.")

    # Sample leaderboard data
    data = [
        {"Name": "John Doe", "Role": "Student", "Points": 1200, "Level": "Gold"},
        {"Name": "Jane Smith", "Role": "Student", "Points": 1150, "Level": "Gold"},
        {"Name": "Mr. Brown", "Role": "Teacher", "Points": 980, "Level": "Silver"},
        {"Name": "East High School", "Role": "Institution", "Points": 5000, "Level": "Platinum"},
    ]
    df = pd.DataFrame(data)

    # Leaderboard table
    st.subheader("Leaderboard")
    st.dataframe(df)

    # Simple points summary
    st.markdown("---")
    st.subheader("Gamification Summary")
    st.write("- Students earn points by completing assignments and participating in activities.")
    st.write("- Teachers and institutions earn points for engagement and performance.")
    st.write("- Future: connect points to badges, certificates, and scholarships.")
