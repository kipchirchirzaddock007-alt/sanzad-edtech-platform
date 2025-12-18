import streamlit as st
import pandas as pd


def _init_env_reports():
    """Ensure the env_reports list exists in session state."""
    if "env_reports" not in st.session_state:
        st.session_state["env_reports"] = []  # list of dicts


def render(role: str):
    _init_env_reports()

    st.header("EnviroTech – Community Environment Watch")
    st.write(
        "Report pollution and environmental issues around you. "
        "This space is for awareness and education, not for legal accusations."
    )

    user_name = st.session_state.get("user_name", "").strip() or "Anonymous"
    user_inst = st.session_state.get("user_institution", "").strip()
    user_loc = st.session_state.get("user_location", {})

    # ---------------- Report form (NOT for Super Admin) ----------------
    if role != "Super Admin":
        st.markdown("### Submit an environment report")

        with st.form("env_report_form"):
            col1, col2 = st.columns(2)
            with col1:
                poll_type = st.selectbox(
                    "Type of issue",
                    [
                        "Air pollution (smoke, fumes)",
                        "Water pollution (rivers, lakes, oceans)",
                        "Noise pollution",
                        "Illegal dumping / solid waste",
                        "Wildlife harm / habitat destruction",
                        "Other",
                    ],
                )
                severity = st.selectbox(
                    "Severity (your estimate)",
                    ["Low", "Medium", "High", "Emergency"],
                )
            with col2:
                datetime_observed = st.text_input(
                    "When did you observe this? (optional)",
                    placeholder="e.g., 2025-12-06 13:00 or 'This morning'",
                )
                people_involved = st.text_input(
                    "People / organizations involved (optional)",
                    help="Avoid full personal details; describe generally if needed.",
                )

            description = st.text_area(
                "Describe what is happening",
                placeholder=(
                    "Example: Thick black smoke from burning rubbish near the school fence, "
                    "blowing into classrooms."
                ),
            )

            st.markdown("**Location information**")
            loc_col1, loc_col2 = st.columns(2)
            with loc_col1:
                use_profile_loc = st.checkbox(
                    "Use my profile location as base",
                    value=True,
                )
            with loc_col2:
                extra_loc = st.text_input(
                    "Exact spot / GPS (optional)",
                    placeholder="e.g., 'Near main gate, coordinates -0.283, 36.07'",
                )

            base_loc_parts = []
            if use_profile_loc:
                if user_loc.get("city"):
                    base_loc_parts.append(user_loc["city"])
                if user_loc.get("country"):
                    base_loc_parts.append(user_loc["country"])
                if user_loc.get("details"):
                    base_loc_parts.append(user_loc["details"])
            base_loc = ", ".join(base_loc_parts)
            full_location = (base_loc + " | " + extra_loc).strip(" |")

            st.markdown("**Upload evidence (optional)**")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                image_file = st.file_uploader(
                    "Photo (image)", type=["png", "jpg", "jpeg"], key="env_image"
                )
            with col_f2:
                audio_file = st.file_uploader(
                    "Sound recording (audio)", type=["wav", "mp3", "ogg"], key="env_audio"
                )

            submitted = st.form_submit_button("Submit report")

            if submitted:
                if not description.strip():
                    st.error("Please describe what is happening.")
                elif not full_location:
                    st.error("Please provide at least some location information.")
                else:
                    report = {
                        "reporter": user_name,
                        "role": role,
                        "institution": user_inst or "Unlinked",
                        "type": poll_type,
                        "severity": severity,
                        "description": description.strip(),
                        "people_involved": people_involved.strip(),
                        "datetime_observed": datetime_observed.strip(),
                        "location": full_location,
                        "has_image": bool(image_file),
                        "has_audio": bool(audio_file),
                        "image_bytes": image_file.read() if image_file is not None else None,
                        "image_name": image_file.name if image_file is not None else "",
                        "audio_bytes": audio_file.read() if audio_file is not None else None,
                        "audio_name": audio_file.name if audio_file is not None else "",
                    }

                    st.session_state["env_reports"].append(report)
                    st.success("Environment report submitted. Thank you for contributing.")
    else:
        st.info("Super Admin only reviews environment reports and statistics here; reporting is for other users.")

    st.markdown("---")

    # ---------------- Browsing reports (all roles, including Super Admin) ----------------
    st.subheader("Browse environment reports")

    reports = st.session_state.get("env_reports", [])
    if not reports:
        st.write("No reports have been submitted yet.")
        return

    # Filters
    filt_col1, filt_col2, filt_col3 = st.columns(3)
    with filt_col1:
        view_scope = st.selectbox(
            "View scope",
            ["All reports", "My reports only"],
        )
    with filt_col2:
        type_filter = st.selectbox(
            "Filter by type",
            ["All"] + sorted({r["type"] for r in reports}),
        )
    with filt_col3:
        severity_filter = st.selectbox(
            "Filter by severity",
            ["All", "Low", "Medium", "High", "Emergency"],
        )

    filtered = []
    for r in reports:
        if view_scope == "My reports only":
            if r["reporter"] != user_name:
                continue
        if type_filter != "All" and r["type"] != type_filter:
            continue
        if severity_filter != "All" and r["severity"] != severity_filter:
            continue
        filtered.append(r)

    if not filtered:
        st.write("No reports match the selected filters.")
        return

    # Simple table with metadata
    df = pd.DataFrame(
        [
            {
                "Reporter": r["reporter"],
                "Role": r["role"],
                "Institution": r["institution"],
                "Type": r["type"],
                "Severity": r["severity"],
                "When observed": r["datetime_observed"],
                "Location": r["location"],
                "People involved": r["people_involved"],
                "Photo?": "Yes" if r["has_image"] else "No",
                "Audio?": "Yes" if r["has_audio"] else "No",
            }
            for r in filtered
        ]
    )
    st.dataframe(df, use_container_width=True)

    # Detailed cards with media and download buttons
    st.markdown("### Report details with media")

    for idx, r in enumerate(filtered):
        with st.expander(f"{r['type']} – {r['severity']} – {r['location'][:50]}"):
            st.write(f"**Reporter:** {r['reporter']} ({r['role']})")
            st.write(f"**Institution:** {r['institution']}")
            st.write(f"**When observed:** {r['datetime_observed']}")
            st.write(f"**Location:** {r['location']}")
            st.write(f"**People involved:** {r['people_involved']}")
            st.write("**Description:**")
            st.write(r["description"])

            media_cols = st.columns(2)

            # Image preview + download
            with media_cols[0]:
                if r.get("has_image") and r.get("image_bytes"):
                    st.markdown("**Photo evidence**")
                    st.image(r["image_bytes"], use_column_width=True)
                    st.download_button(
                        label="Download photo",
                        data=r["image_bytes"],
                        file_name=r.get("image_name") or "envirotech_photo.jpg",
                        mime="image/jpeg",
                        key=f"download_img_{idx}",
                    )
                else:
                    st.markdown("_No photo uploaded._")

            # Audio playback + download
            with media_cols[1]:
                if r.get("has_audio") and r.get("audio_bytes"):
                    st.markdown("**Audio evidence**")
                    st.audio(r["audio_bytes"])
                    st.download_button(
                        label="Download audio",
                        data=r["audio_bytes"],
                        file_name=r.get("audio_name") or "envirotech_audio.mp3",
                        mime="audio/mpeg",
                        key=f"download_audio_{idx}",
                    )
                else:
                    st.markdown("_No audio uploaded._")

    # Extra view for Super Admin: quick stats
    if role == "Super Admin":
        st.markdown("---")
        st.subheader("EnviroTech overview (Super Admin)")

        total = len(reports)
        by_type = pd.Series([r["type"] for r in reports]).value_counts().to_dict()
        by_severity = pd.Series([r["severity"] for r in reports]).value_counts().to_dict()

        st.write(f"Total reports: {total}")
        st.write("By type:")
        for k, v in by_type.items():
            st.write(f"- {k}: {v}")
        st.write("By severity:")
        for k, v in by_severity.items():
            st.write(f"- {k}: {v}")
