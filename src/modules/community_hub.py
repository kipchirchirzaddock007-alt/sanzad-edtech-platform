import streamlit as st
import pandas as pd

def render(role: str):
    st.header("Community Hub")
    st.write("Discussions, mentorship, clubs, and events.")

    # In-session storage for topics
    if "community_topics" not in st.session_state:
        st.session_state.community_topics = []

    left, right = st.columns([2, 3])

    with left:
        st.subheader("Create Discussion Topic")
        with st.form("community_topic_form"):
            title = st.text_input("Topic Title")
            category = st.selectbox("Category", ["General", "Homework Help", "Mentorship", "Events"])
            description = st.text_area("Description")
            submitted = st.form_submit_button("Post Topic")
            if submitted:
                if not title.strip():
                    st.error("Title is required.")
                else:
                    st.session_state.community_topics.append(
                        {"Title": title, "Category": category, "Description": description}
                    )
                    st.success("Topic posted.")

    with right:
        st.subheader("Active Topics (This Session)")
        if st.session_state.community_topics:
            df = pd.DataFrame(st.session_state.community_topics)
            st.dataframe(df)
        else:
            st.write("No topics yet. Create the first one!")
