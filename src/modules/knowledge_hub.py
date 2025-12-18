import streamlit as st
import pandas as pd
import base64

def render(role: str):
    st.header("Knowledge Hub")
    st.write("Subjects with codes, PDFs, and a simple lesson repository.")

    # ---------------------------------
    # Session state setup
    # ---------------------------------
    if "subjects" not in st.session_state:
        # list of dicts: {name, code}
        st.session_state.subjects = [
            {"Name": "Math", "Code": "MATH-101"},
            {"Name": "Science", "Code": "SCI-101"},
            {"Name": "English", "Code": "ENG-101"},
        ]

    if "subject_pdfs" not in st.session_state:
        # key: subject code, value: list of dicts {filename, data}
        st.session_state.subject_pdfs = {}

    # ---------------------------------
    # LEFT: manage subjects (Teacher / Super Admin)
    # ---------------------------------
    left, right = st.columns([2, 3])

    with left:
        st.subheader("Manage Subjects & Codes")

        if role in ["Teacher", "Super Admin"]:
            # Show current subjects
            if st.session_state.subjects:
                df_subj = pd.DataFrame(st.session_state.subjects)
                st.write("Current subjects:")
                st.dataframe(df_subj)
            else:
                st.write("No subjects defined yet.")

            st.markdown("**Add or edit subject**")

            # Add / Edit subject form
            subject_names = [s["Name"] for s in st.session_state.subjects]
            mode = st.radio("Mode", ["Add new", "Edit existing"])

            if mode == "Edit existing" and subject_names:
                selected = st.selectbox("Select subject to edit", subject_names)
                existing = next(s for s in st.session_state.subjects if s["Name"] == selected)
                default_name = existing["Name"]
                default_code = existing["Code"]
            else:
                selected = None
                default_name = ""
                default_code = ""

            with st.form("subject_form"):
                name = st.text_input("Subject Name", value=default_name)
                code = st.text_input("Subject Code", value=default_code, placeholder="e.g., MATH-101")

                submitted = st.form_submit_button("Save Subject")
                if submitted:
                    n = name.strip()
                    c = code.strip()
                    if not n or not c:
                        st.error("Both name and code are required.")
                    else:
                        if mode == "Add new":
                            # Prevent duplicates by code
                            if any(s["Code"] == c for s in st.session_state.subjects):
                                st.error("A subject with this code already exists.")
                            else:
                                st.session_state.subjects.append({"Name": n, "Code": c})
                                st.success(f"Added subject: {n} ({c})")
                        else:
                            # Update existing
                            for s in st.session_state.subjects:
                                if s["Name"] == selected:
                                    s["Name"] = n
                                    s["Code"] = c
                                    st.success(f"Updated subject to: {n} ({c})")
                                    break

            # Delete subject
            st.markdown("**Delete subject**")
            if st.session_state.subjects:
                with st.form("delete_subject_form"):
                    delete_target = st.selectbox(
                        "Select subject to delete",
                        [f'{s["Name"]} ({s["Code"]})' for s in st.session_state.subjects],
                    )
                    delete_submit = st.form_submit_button("Delete Subject")
                    if delete_submit:
                        code_to_delete = delete_target.split("(")[-1].strip(")")
                        st.session_state.subjects = [
                            s for s in st.session_state.subjects if s["Code"] != code_to_delete
                        ]
                        # Also remove any PDFs tied to that subject code
                        st.session_state.subject_pdfs.pop(code_to_delete, None)
                        st.success(f"Deleted subject and its PDFs: {delete_target}")
            else:
                st.write("No subjects to delete.")

        else:
            st.info("Only Teachers and Super Admin can manage subjects.")

        st.markdown("---")

        # Upload PDFs for a subject (Teacher / Super Admin)
        if role in ["Teacher", "Super Admin"] and st.session_state.subjects:
            st.subheader("Upload Lesson PDF for a Subject")

            df_subj = pd.DataFrame(st.session_state.subjects)
            choices = [f'{row["Name"]} ({row["Code"]})' for _, row in df_subj.iterrows()]
            target = st.selectbox("Select subject", choices)

            target_code = target.split("(")[-1].strip(")")

            pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="knowledge_hub_pdf")
            if st.button("Save PDF to Subject"):
                if pdf_file is None:
                    st.error("Please choose a PDF file first.")
                else:
                    if target_code not in st.session_state.subject_pdfs:
                        st.session_state.subject_pdfs[target_code] = []
                    st.session_state.subject_pdfs[target_code].append(
                        {"filename": pdf_file.name, "data": pdf_file.read()}
                    )
                    st.success(f"Saved PDF '{pdf_file.name}' under {target}.")

    # ---------------------------------
    # RIGHT: students/any role view lessons & PDFs
    # ---------------------------------
    with right:
        st.subheader("Subjects & Lesson PDFs")

        if st.session_state.subjects:
            df_subj = pd.DataFrame(st.session_state.subjects)
            st.write("Available subjects:")
            st.dataframe(df_subj)

            # Filter by subject (name+code)
            options = ["All"] + [f'{row["Name"]} ({row["Code"]})' for _, row in df_subj.iterrows()]
            selected_subject = st.selectbox("Filter by subject", options)

            # Show PDFs for selected subject(s)
            st.markdown("### Lesson PDFs")
            if selected_subject == "All":
                any_pdf = False
                for s in st.session_state.subjects:
                    code = s["Code"]
                    if code in st.session_state.subject_pdfs and st.session_state.subject_pdfs[code]:
                        any_pdf = True
                        st.write(f'**{s["Name"]} ({s["Code"]})**')
                        for file_info in st.session_state.subject_pdfs[code]:
                            b64 = base64.b64encode(file_info["data"]).decode()
                            href = f'<a href="data:application/pdf;base64,{b64}" download="{file_info["filename"]}">Download: {file_info["filename"]}</a>'
                            st.markdown(href, unsafe_allow_html=True)
                if not any_pdf:
                    st.write("No PDFs uploaded yet for any subject.")
            else:
                code = selected_subject.split("(")[-1].strip(")")
                st.write(f"Subject: {selected_subject}")
                if code in st.session_state.subject_pdfs and st.session_state.subject_pdfs[code]:
                    for file_info in st.session_state.subject_pdfs[code]:
                        b64 = base64.b64encode(file_info["data"]).decode()
                        href = f'<a href="data:application/pdf;base64,{b64}" download="{file_info["filename"]}">Download: {file_info["filename"]}</a>'
                        st.markdown(href, unsafe_allow_html=True)
                else:
                    st.write("No PDFs uploaded yet for this subject.")
        else:
            st.write("No subjects available yet. A teacher needs to add them first.")

        st.markdown("---")
        st.info(
            "Future: link these subjects and PDFs to Smart Teacher, AI recommendations, and multilingual tagging."
        )
