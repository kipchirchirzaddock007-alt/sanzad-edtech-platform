import streamlit as st

def render(role: str):
    st.header("Wellbeing & Health AI (Global)")
    st.write(
        "This space helps anyone in SANZAD reflect on wellbeing and get general self-care tips. "
        "It does not provide medical diagnosis or emergency support."
    )

    # Who are you today? (beyond student only)
    profile_role = st.selectbox(
        "What describes you best today?",
        [
            "Student / Learner",
            "Teacher / Trainer",
            "Parent / Guardian",
            "Professional / Worker",
            "Entrepreneur / Founder",
            "Job Seeker",
            "Retired",
            "Other",
        ],
    )

    st.markdown("---")
    st.subheader("Quick wellbeing check-in")

    col1, col2 = st.columns(2)
    with col1:
        mood = st.slider("Mood today", 0, 10, 5, help="0 = very low, 10 = very good")
        energy = st.slider("Energy level", 0, 10, 5)
    with col2:
        stress = st.slider("Stress level", 0, 10, 5)
        sleep = st.slider("Sleep quality last night", 0, 10, 5)

    notes = st.text_area("Anything you want to note (optional)")

    if "wellbeing_logs" not in st.session_state:
        st.session_state["wellbeing_logs"] = []

    if st.button("Save my check-in"):
        st.session_state["wellbeing_logs"].append(
            {
                "profile_role": profile_role,
                "mood": mood,
                "energy": energy,
                "stress": stress,
                "sleep": sleep,
                "notes": notes.strip(),
            }
        )
        st.success("Check-in saved for you only on this device/session.")

    st.markdown("---")
    st.subheader("General self-care suggestions")

    suggestions = []

    # Simple rule-based suggestions (placeholder for future AI)
    if stress >= 7:
        suggestions.append(
            "Stress looks high. Try a short break, breathing exercises, or a walk if possible. "
            "If stress stays high for many days, consider talking to a trusted person or professional."
        )
    if mood <= 3:
        suggestions.append(
            "Mood is low today. Be gentle with yourself, reduce unnecessary pressure, "
            "and reach out to someone you trust if you feel comfortable."
        )
    if sleep <= 4:
        suggestions.append(
            "Sleep seems poor. Aim for a consistent bedtime, reduce screens before sleep, "
            "and keep caffeine low in the evening."
        )
    if energy <= 4:
        suggestions.append(
            "Energy is low. Light movement, hydration, and short breaks away from screens can help."
        )

    # Role-specific layer (still non-medical)
    if profile_role == "Student / Learner":
        suggestions.append(
            "Plan study in small focused blocks with breaks (e.g., 25 minutes study + 5 minutes pause) "
            "to avoid burnout."
        )
    elif profile_role == "Teacher / Trainer":
        suggestions.append(
            "If many sessions feel draining, schedule buffer time between classes and share "
            "clear expectations with learners to reduce pressure."
        )
    elif profile_role == "Parent / Guardian":
        suggestions.append(
            "Balance caring for others with small moments for yourself (even 5–10 minutes) "
            "to recharge and avoid burnout."
        )
    elif profile_role == "Professional / Worker":
        suggestions.append(
            "Protect focus time by limiting multitasking and setting boundaries for after-hours work when possible."
        )
    elif profile_role == "Entrepreneur / Founder":
        suggestions.append(
            "Build rest into your calendar like any other meeting; long-term creativity needs recovery."
        )
    elif profile_role == "Job Seeker":
        suggestions.append(
            "Job search is emotionally heavy; break tasks into small steps and schedule non-job activities you enjoy."
        )

    if suggestions:
        for s in suggestions:
            st.write(f"- {s}")
    else:
        st.write(
            "Your levels look fairly balanced today. Keep the habits that work for you—regular sleep, movement, "
            "breaks, and healthy social connections."
        )

    st.markdown("---")
    st.subheader("Emergency & First Aid (Non-medical)")

    st.write(
        "If something feels serious or life-threatening, call your local emergency number immediately. "
        "The information below is general first-aid education, not medical advice or a replacement for real training."
    )

    emergency_text = st.text_area(
        "Describe what is happening or your symptoms",
        placeholder="Example: I spilled hot water on my hand and it is very painful.",
    )

    col_e1, col_e2 = st.columns([1, 1])

    # First-aid tips (rule-based, short and generic)
    with col_e1:
        if st.button("Get first-aid tips"):
            if not emergency_text.strip():
                st.error("Please describe what is happening first.")
            else:
                txt = emergency_text.lower()
                tips = []

                # Burns and scalds
                if any(word in txt for word in ["burn", "scald", "hot water", "fire"]):
                    tips.append(
                        "For minor burns or scalds: cool the area immediately with cool (not icy) running water for at least 20 minutes. "
                        "Remove tight items like rings if possible before swelling, and do not apply ice, butter, or oil."
                    )

                # Bleeding and cuts
                if any(word in txt for word in ["bleed", "bleeding", "cut", "wound", "laceration"]):
                    tips.append(
                        "For bleeding: apply firm, direct pressure with a clean cloth or bandage. "
                        "Keep pressure until bleeding slows or stops. If blood soaks through, add more layers without removing the first one."
                    )

                # Nosebleed
                if any(word in txt for word in ["nosebleed", "nose bleed"]):
                    tips.append(
                        "For a nosebleed: sit up, lean slightly forward, and pinch the soft part of the nose for 10–15 minutes. "
                        "Breathe through the mouth and avoid tilting the head back."
                    )

                # Choking
                if any(word in txt for word in ["choke", "choking"]):
                    tips.append(
                        "For choking in a conscious adult: encourage strong coughing if they can breathe. "
                        "If they cannot cough, speak, or breathe, call emergency services immediately and seek help from someone trained in back blows and abdominal thrusts."
                    )

                # Sprains and minor strains
                if any(word in txt for word in ["sprain", "ankle", "twisted", "strain"]):
                    tips.append(
                        "For a possible sprain: rest the injured area, apply a cold pack wrapped in cloth for short periods, "
                        "elevate the limb if possible, and avoid putting full weight on it until assessed."
                    )

                # Possible fracture / broken bone
                if any(word in txt for word in ["fracture", "broken bone", "bone sticking", "cannot move limb"]):
                    tips.append(
                        "For a possible broken bone: keep the injured area as still as possible. "
                        "Do not try to push any bone back in. Support the limb with cushions or folded cloth while you seek urgent medical help."
                    )

                # Head injury
                if any(word in txt for word in ["hit head", "head injury", "concussion", "knocked out"]):
                    tips.append(
                        "After a head injury: watch for worsening headache, confusion, repeated vomiting, seizures, or drowsiness—these need urgent medical care. "
                        "Keep the person awake and still while arranging medical assessment."
                    )

                # Cold / flu-like symptoms
                if any(word in txt for word in ["cold", "cough", "flu", "runny nose", "sore throat"]):
                    tips.append(
                        "For cold or flu-like symptoms: rest, drink fluids, and consider warm drinks and simple salt-water gargles for throat discomfort. "
                        "Seek medical care if there is high fever, difficulty breathing, chest pain, or symptoms that keep getting worse."
                    )

                # Fever
                if any(word in txt for word in ["fever", "high temperature"]):
                    tips.append(
                        "For fever: dress lightly, drink plenty of fluids, and rest in a cool, comfortable environment. "
                        "If fever is very high, lasts several days, or is combined with rash, stiff neck, confusion, or difficulty breathing, seek medical attention urgently."
                    )

                # Possible allergic reaction
                if any(word in txt for word in ["allergy", "allergic", "swollen lips", "swollen tongue", "hives"]):
                    tips.append(
                        "For a possible allergic reaction: remove or avoid the suspected trigger if known, and watch closely for any difficulty breathing, swelling of the tongue or throat, or feeling faint—these need immediate emergency care."
                    )

                # Chest pain / possible heart issue (very generic)
                if any(word in txt for word in ["chest pain", "tight chest", "pressure chest"]):
                    tips.append(
                        "Chest pain or pressure that is heavy, spreading to arm, jaw, or back, or comes with shortness of breath, sweating, or nausea can be serious. "
                        "Sit the person down, keep them calm, and call emergency services immediately."
                    )

                # Breathing difficulty
                if any(word in txt for word in ["difficulty breathing", "short of breath", "hard to breathe", "cannot breathe"]):
                    tips.append(
                        "Difficulty breathing can be life-threatening. Help the person sit upright, loosen tight clothing, and stay with them. "
                        "Call emergency services immediately."
                    )

                # Dizziness / fainting (very generic)
                if any(word in txt for word in ["faint", "fainting", "dizzy", "dizziness", "lightheaded"]):
                    tips.append(
                        "If someone feels faint: help them lie down or sit with head between knees, and loosen tight clothing. "
                        "If they lose consciousness or do not respond, call emergency services."
                    )

                # Default if nothing matched
                if not tips:
                    tips.append(
                        "No specific match was found. Keep the person safe, monitor their breathing and responsiveness, "
                        "and contact a health professional or emergency service if you are worried."
                    )

                st.markdown("**General first-aid guidance (not a diagnosis):**")
                for t_line in tips:
                    st.write(f"- {t_line}")

                st.warning(
                    "If the situation seems serious, getting worse, or you are unsure, call your local emergency number "
                    "or contact a health professional immediately."
                )

    # Panic button – logs emergency internally (for Sanzad admins only)
    with col_e2:
        if "emergencies" not in st.session_state:
            st.session_state["emergencies"] = []

        if st.button("PANIC BUTTON – Alert Sanzad Admin"):
            user_name = st.session_state.get("user_name", "").strip() or "Unknown user"
            role_override = st.session_state.get("role_override", "").strip() or "Unknown role"
            location = st.session_state.get("user_location", {})
            location_str = ", ".join(
                [location.get("city", ""), location.get("country", ""), location.get("details", "")]
            ).strip(", ")

            st.session_state["emergencies"].append(
                {
                    "user": user_name,
                    "role": role_override,
                    "description": emergency_text.strip() or "No description provided",
                    "location": location_str or "Location not provided",
                }
            )

            st.error(
                "Emergency alert recorded for Sanzad administrators inside this system. "
                "This does NOT contact ambulances or national emergency lines. "
                "Please call your local emergency number immediately if this is serious."
            )

    st.markdown("---")
    st.caption(
        "This module is for general wellbeing and first-aid education only. It is not medical advice or a replacement "
        "for qualified training. If you feel unsafe or unwell, please contact local health services or emergency "
        "numbers immediately."
    )
