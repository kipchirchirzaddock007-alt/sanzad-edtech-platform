import streamlit as st

def render(role: str):
    st.markdown("## 🎓 Sanzad Campus Hub")
    st.write(f"This is a minimal test view. You are viewing as **{role}**.")
