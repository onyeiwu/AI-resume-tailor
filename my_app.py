# ============================================================
# my_app.py — My AI Resume/ Job description Analyser
# ============================================================

import streamlit as st
from pipeline_runner import run_full_analysis
import tempfile
import os

try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass


st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.title("📄 AI Resume Tailor")

if "page" not in st.session_state:
    st.session_state["page"] = "📤 Upload & Analyze"

if st.sidebar.button("📤 Upload & Analyze", use_container_width=True):
    st.session_state["page"] = "📤 Upload & Analyze"
st.sidebar.divider()

if st.sidebar.button("📊 ATS Score", use_container_width=True):
    st.session_state["page"] = "📊 ATS Score"
st.sidebar.divider()

if st.sidebar.button("✨ Tailor My Resume", use_container_width=True):
    st.session_state["page"] = "✨ Tailor My Resume"
st.sidebar.divider()

if st.sidebar.button("🎤 Interview Practice", use_container_width=True):
    st.session_state["page"] = "🎤 Interview Practice"
st.sidebar.divider()
if st.sidebar.button("📥 Download Resume", use_container_width=True):
    st.session_state["page"] = "📥 Download Resume"
st.sidebar.divider()
if st.sidebar.button("💬 Career Chat", use_container_width=True):
    st.session_state["page"] = "💬 Career Chat"
st.sidebar.divider()

page = st.session_state["page"]

# Lock later pages until analysis has actually run
# (Career Chat is exempt — it can be used standalone, without an analysis)
if page not in ["📤 Upload & Analyze", "💬 Career Chat"] and "result" not in st.session_state:
    st.warning("⚠️ Please upload your resume and job description first, on the 'Upload & Analyze' page.")
    st.stop()

# ============================================================
# PAGE 1: UPLOAD & ANALYZE
# ============================================================
if page == "📤 Upload & Analyze":
    st.title("📄 AI Resume Tailor & Job Matching Agent")
    st.write("Upload your resume and a job description to get started.")

    # --- Clear buttons ---
    clear_col1, clear_col2 = st.columns(2)
    with clear_col1:
        if st.button("🗑️ Clear Resume"):
            for key in ["cv_file_bytes", "cv_file_name", "result", "tailored", "quiz", "cv_raw_text"]:
                st.session_state.pop(key, None)
            st.rerun()
    with clear_col2:
        if st.button("🗑️ Clear Job Description"):
            st.session_state.pop("jd_text_value", None)
            st.session_state.pop("fetched_jd_text", None)
            st.rerun()

    st.divider()

    # --- CV Upload ---
    cv_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if cv_file is not None:
        # Use getvalue(), not read() — read() consumes the stream, so a
        # second read (e.g. on a later rerun) would return empty bytes
        # and silently corrupt the saved file. getvalue() is safe to
        # call repeatedly and always returns the full file content.
        if st.session_state.get("cv_file_name") != cv_file.name:
            st.session_state["cv_file_bytes"] = cv_file.getvalue()
            st.session_state["cv_file_name"] = cv_file.name
        st.success(f"✅ '{cv_file.name}' uploaded successfully!")
    elif "cv_file_name" in st.session_state:
        st.info(f"📎 Currently using: **{st.session_state['cv_file_name']}** (upload a new file above to replace it, or click 'Clear Resume' to remove it)")

    # --- JD Input: paste text OR fetch from a URL ---
    jd_input_method = st.radio("How would you like to provide the job description?", ["Paste text", "Provide a URL"], horizontal=True)

    jd_text = ""
    if jd_input_method == "Paste text":
        jd_text = st.text_area(
            "Paste the job description here",
            value=st.session_state.get("jd_text_value", ""),
            height=250,
            key="jd_text_input"
        )
        st.session_state["jd_text_value"] = jd_text
    else:
        jd_url = st.text_input("Paste the job posting URL")
        if jd_url:
            if st.button("Fetch Job Description"):
                with st.spinner("Fetching job description..."):
                    from extraction.url_reader import extract_text_from_url
                    try:
                        fetched_text = extract_text_from_url(jd_url)
                        st.session_state["fetched_jd_text"] = fetched_text
                        st.success("✅ Job description fetched successfully!")
                    except ValueError as e:
                        st.error(f"❌ {e}")
                        st.info("Please paste the job description text directly instead.")

        # Show the fetched text in an editable box, and use it as jd_text
        if "fetched_jd_text" in st.session_state:
            jd_text = st.text_area(
                "Fetched job description (you can edit before analyzing)",
                value=st.session_state["fetched_jd_text"],
                height=250,
                key="fetched_jd_display"
            )
            st.session_state["fetched_jd_text"] = jd_text

    if jd_text.strip():
        st.success("✅ Job description received!")

    # --- Analyze button ---
    have_cv = cv_file is not None or "cv_file_bytes" in st.session_state
    if have_cv and jd_text.strip():
        if st.button("🔍 Analyze Match", type="primary"):
            # Use getvalue() here too, for the same reason as above
            cv_bytes = cv_file.getvalue() if cv_file is not None else st.session_state["cv_file_bytes"]
            cv_name = cv_file.name if cv_file is not None else st.session_state["cv_file_name"]

            # Streamlit needs a real file path, so we save the upload to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{cv_name}") as tmp:
                tmp.write(cv_bytes)
                tmp_path = tmp.name

            with st.spinner("Analyzing your resume against the job description..."):
                from extraction.pipeline import process_resume
                cv_raw_text = process_resume(tmp_path)
                result = run_full_analysis(tmp_path, jd_text)

            st.session_state["result"] = result
            st.session_state["cv_raw_text"] = cv_raw_text
            st.snow()
            st.success("Analysis complete! 🎉 Head to the '📊 ATS Score' tab in the sidebar to see your results.")

# ============================================================
# PAGE 2: ATS SCORE DASHBOARD
# ============================================================
elif page == "📊 ATS Score":
    score_data = st.session_state["result"]["score"]
    breakdown = score_data["breakdown"]

    st.subheader("📊 ATS Match Results")

    # --- Overall score, color-coded ---
    overall = score_data["overall_score"]
    if overall >= 70:
        color = "🟢"
    elif overall >= 45:
        color = "🟡"
    else:
        color = "🔴"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Overall Match", value=f"{overall}%")
        st.write(f"{color} " + (
            "Strong match" if overall >= 70 else
            "Moderate match" if overall >= 45 else
            "Weak match"
        ))
    with col2:
        st.caption(score_data["note"])

    st.divider()

    # --- Component breakdown, as a Plotly horizontal bar chart ---
    st.write("### Component Breakdown")

    components = [
        ("🔑 Keyword Match", breakdown["keyword_match"], 30),
        ("🛠️ Skills Match", breakdown["skills_match_blended"], 25),
        ("💼 Experience Match", breakdown["experience_match"], 20),
        ("🎓 Education Match", breakdown["education_match"], 10),
        ("📋 Responsibilities Match", breakdown["responsibilities_match"], 10),
        ("📐 Formatting", breakdown["formatting_score"], 5),
    ]

    import plotly.graph_objects as go

    chart_labels = [f"{label} ({weight}%)" for label, value, weight in components]
    chart_values = [value for label, value, weight in components]

    fig = go.Figure(go.Bar(
        x=chart_values,
        y=chart_labels,
        orientation='h',
        marker=dict(
            color=chart_values,
            colorscale=[[0, '#e74c3c'], [0.5, '#f1c40f'], [1, '#2ecc71']],
            cmin=0, cmax=100
        ),
        text=[f"{v}%" for v in chart_values],
        textposition='outside'
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 105], title="Match %"),
        height=350,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Status notes for components that have them ---
    if breakdown.get("experience_status") == "unknown":
        st.info(f"ℹ️ {breakdown['experience_note']}")
    if breakdown.get("education_status") == "unknown":
        st.info(f"ℹ️ {breakdown['education_note']}")

    # --- Formatting issues, surfaced explicitly ---
    formatting_issues = breakdown.get("formatting_issues", [])
    if formatting_issues:
        st.write("### 📐 Formatting Issues Found")
        for issue in formatting_issues:
            st.write(f"- {issue}")
    elif breakdown.get("formatting_score") == 100:
        st.success("✅ No formatting issues detected.")

    st.divider()

    # --- Missing items, shown as readable tags ---
    st.write("### What's Missing")

    tab1, tab2, tab3 = st.tabs(["Missing Keywords", "Missing Skills", "Missing Responsibilities"])

    with tab1:
        missing_kw = score_data.get("missing_keywords", [])
        if missing_kw:
            st.write(" &nbsp; ".join([f"`{kw}`" for kw in missing_kw]))
        else:
            st.write("None — great keyword coverage!")

    with tab2:
        missing_skills = score_data.get("missing_skills", [])
        if missing_skills:
            st.write(" &nbsp; ".join([f"`{sk}`" for sk in missing_skills]))
        else:
            st.write("None — great skills coverage!")

    with tab3:
        missing_resp = score_data.get("missing_responsibilities", [])
        if missing_resp:
            st.write(" &nbsp; ".join([f"`{r}`" for r in missing_resp]))
        else:
            st.write("None — great responsibilities coverage!")

# ============================================================
# PAGE 3: TAILORING REVIEW SCREEN
# ============================================================
elif page == "✨ Tailor My Resume":
    st.subheader("✨ Tailor My Resume")
    st.caption("AI-generated suggestions — always shown next to your original content. Nothing here is final until you review it.")
    st.warning("⚠️ Automated fact-checking is applied but is not perfect. We've observed real cases where fabricated details slipped through undetected. Always personally verify every specific claim, tool, or technique before using AI-tailored content.")

    if st.button("Generate Tailored Content"):
        cv_analysis = st.session_state["result"]["cv_analysis"]
        jd_analysis = st.session_state["result"]["jd_analysis"]

        with st.spinner("Tailoring your resume content..."):
            from tailoring.tailor_pipeline import generate_verified_summary
            from tailoring.tailor_skills import tailor_skills
            from tailoring.tailor_experience import tailor_experience
            from tailoring.verify import verify_summary

            summary_result = generate_verified_summary(cv_analysis, jd_analysis)
            reordered_skills = tailor_skills(cv_analysis["skills"], jd_analysis["required_skills"])
            bullets = tailor_experience(cv_analysis, jd_analysis)
            bullets_check = verify_summary(cv_analysis, "\n".join(bullets))

        st.session_state["tailored"] = {
            "summary_result": summary_result,
            "reordered_skills": reordered_skills,
            "bullets": bullets,
            "bullets_check": bullets_check
        }

    if "tailored" in st.session_state:
        t = st.session_state["tailored"]

        # --- Summary: side-by-side ---
        st.write("### Professional Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Original data (real skills & duties)")
            st.write(f"Skills: {', '.join(st.session_state['result']['cv_analysis']['skills'][:8])}...")
        with col2:
            st.caption("AI-tailored summary")
            st.write(t["summary_result"]["tailored_summary"])

        if t["summary_result"]["recommendation"] == "review_required":
            st.warning(f"⚠️ Review needed: {t['summary_result']['verification']['reasoning']}")
        else:
            st.info("ℹ️ Our automated check found no issues, but it isn't perfect — please read the tailored text above carefully and confirm every specific detail, tool, or technique actually reflects your real experience before using it.")

        st.divider()

        # --- Skills: side-by-side ---
        st.write("### Skills (reordered by relevance)")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Original order")
            st.write(", ".join(st.session_state["result"]["cv_analysis"]["skills"]))
        with col2:
            st.caption("Reordered for this job")
            st.write(", ".join(t["reordered_skills"]))

        st.divider()

        # --- Experience bullets ---
        st.write("### Tailored Experience Bullets")
        for b in t["bullets"]:
            st.write(f"- {b}")

        if t["bullets_check"].get("has_unsupported_claims"):
            st.warning(f"⚠️ Review needed: {t['bullets_check']['reasoning']}")
        else:
            st.info("ℹ️ Our automated check found no issues, but it isn't perfect — please read the tailored bullets above carefully and confirm every specific detail, tool, or technique actually reflects your real experience before using it.")

# ============================================================
# PAGE 4: INTERVIEW QUIZ SCREEN
# ============================================================
elif page == "🎤 Interview Practice":
    st.subheader("🎤 Practice Interview Questions")
    st.caption("Technical & role-specific questions are multiple choice. Behavioral & CV-based questions are open-ended. Nothing is scored until you finish all questions — feel free to go back and change any answer.")

    if st.button("Generate Interview Questions"):
        cv_analysis = st.session_state["result"]["cv_analysis"]
        jd_analysis = st.session_state["result"]["jd_analysis"]

        with st.spinner("Preparing your interview questions..."):
            from interview.interview_pipeline import generate_verified_questions
            interview_result = generate_verified_questions(cv_analysis, jd_analysis)

        q = interview_result["questions"]

        all_questions = []
        for item in q.get("technical_questions", []):
            all_questions.append({"type": "mcq", "category": "Technical", **item})
        for item in q.get("role_specific_questions", []):
            all_questions.append({"type": "mcq", "category": "Role-Specific", **item})
        for text in q.get("behavioral_questions", []):
            all_questions.append({"type": "open", "category": "Behavioral", "question": text})
        for text in q.get("cv_based_questions", []):
            all_questions.append({"type": "open", "category": "CV-Based", "question": text})

        total_q = len(all_questions)
        # roughly 1 minute per question, minimum 10 minutes
        time_limit_minutes = max(10, total_q)

        import time
        st.session_state["quiz"] = {
            "questions": all_questions,
            "current_index": 0,
            "answers": {},
            "review_note": interview_result["review_note"],
            "start_time": time.time(),
            "time_limit_seconds": time_limit_minutes * 60,
            "finished": False
        }

    if "quiz" in st.session_state:
        quiz = st.session_state["quiz"]
        questions = quiz["questions"]
        total = len(questions)
        answered = len(quiz["answers"])
        idx = quiz["current_index"]

        st.info(f"ℹ️ {quiz['review_note']}")

        # --- Timer ---
        import time
        elapsed = time.time() - quiz["start_time"]
        remaining = max(0, quiz["time_limit_seconds"] - elapsed)
        mins, secs = divmod(int(remaining), 60)
        st.write(f"⏱️ Time remaining: **{mins:02d}:{secs:02d}**")
        if remaining <= 0 and not quiz["finished"]:
            st.warning("⏰ Time's up! Submitting your answers now.")
            quiz["finished"] = True
            st.rerun()

        # --- Progress bar ---
        st.progress(answered / total if total else 0)
        st.write(f"**{answered} / {total} answered**")

        # ---------- FINAL REVIEW (after last question or time up) ----------
        if quiz["finished"]:
            st.divider()
            st.subheader("📋 Your Results")

            mcq_correct = 0
            mcq_total = 0

            for i, q_item in enumerate(questions):
                user_ans = quiz["answers"].get(i)
                st.write(f"**Q{i+1} ({q_item['category']}):** {q_item['question']}")

                if q_item["type"] == "mcq":
                    mcq_total += 1
                    if user_ans == q_item["correct_answer"]:
                        mcq_correct += 1
                        st.success(f"✅ Your answer: {user_ans} — Correct!")
                    else:
                        st.error(f"❌ Your answer: {user_ans or '(not answered)'} — Correct answer: {q_item['correct_answer']}")
                else:
                    st.write(f"Your answer: {user_ans or '(not answered)'}")
                    if user_ans:
                        if f"feedback_{i}" not in st.session_state:
                            with st.spinner("Getting feedback..."):
                                from interview.answer_reviewer import review_answer
                                st.session_state[f"feedback_{i}"] = review_answer(q_item["question"], user_ans)
                        st.info(f"💡 Coaching tip: {st.session_state[f'feedback_{i}']}")
                st.divider()

            if mcq_total:
                st.metric("Multiple Choice Score", f"{mcq_correct} / {mcq_total}")

        # ---------- QUIZ IN PROGRESS ----------
        else:
            current_q = questions[idx]
            st.write(f"**Question {idx + 1} of {total}** — _{current_q['category']}_")
            st.write(current_q["question"])

            if current_q["type"] == "mcq":
                prior = quiz["answers"].get(idx)
                options = current_q["options"]
                choice = st.radio(
                    "Choose an answer:", options,
                    index=options.index(prior) if prior in options else 0,
                    key=f"q_{idx}"
                )
                quiz["answers"][idx] = choice

            else:
                prior = quiz["answers"].get(idx, "")
                response = st.text_area("Type your answer:", value=prior, key=f"q_open_{idx}")
                quiz["answers"][idx] = response

            nav_col1, nav_col2, nav_col3 = st.columns(3)
            with nav_col1:
                if idx > 0:
                    if st.button("⬅️ Previous"):
                        quiz["current_index"] -= 1
                        st.rerun()
            with nav_col2:
                if idx < total - 1:
                    if st.button("Next ➡️"):
                        quiz["current_index"] += 1
                        st.rerun()
            with nav_col3:
                if st.button("✅ Finish & See Results"):
                    quiz["finished"] = True
                    st.rerun()


# ============================================================
# PAGE 5: DOCUMENT DOWNLOAD
# ============================================================
elif page == "📥 Download Resume":
    st.subheader("📥 Download Your Tailored Resume")

    if "tailored" not in st.session_state:
        st.warning("⚠️ Please generate your tailored content first, on the '✨ Tailor My Resume' page.")
        st.stop()

    cv_analysis = st.session_state["result"]["cv_analysis"]
    t = st.session_state["tailored"]

    st.caption("Note: your real job history (titles, companies, dates) is shown exactly as extracted, unedited. Tailored bullet points appear in a separate 'Key Highlights' section rather than under a specific employer, since we don't reliably know which duty belongs to which job.")

    candidate_name = st.text_input("Enter your full name (for the document header)", value="")

    if candidate_name.strip():
        st.divider()
        st.warning(
            "⚠️ This document contains AI-generated content. We've observed real cases "
            "where fabricated details slipped through our automated checks. Please read "
            "the entire document carefully before sending it anywhere, and correct anything "
            "that doesn't accurately reflect your real experience."
        )
        acknowledged = st.checkbox("I understand and have reviewed the content above")

        if acknowledged:
            if st.button("Generate Document"):
                with st.spinner("Building your resume document..."):
                    from generation.docx_builder import build_tailored_resume

                    output_path = build_tailored_resume(
                        candidate_name=candidate_name,
                        tailored_summary=t["summary_result"]["tailored_summary"],
                        reordered_skills=t["reordered_skills"],
                        tailored_bullets=t["bullets"],
                        experience=cv_analysis["experience"],
                        education=cv_analysis["education"],
                        certifications=cv_analysis["certifications"],
                        cv_text=st.session_state.get("cv_raw_text", ""),
                        output_path="tailored_resume.docx"
                    )

                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Tailored Resume (.docx)",
                        data=f,
                        file_name=f"{candidate_name.replace(' ', '_')}_Tailored_Resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    else:
        st.info("Enter your name above to continue.")

# ============================================================
# PAGE 6: CAREER CHAT
# ============================================================
elif page == "💬 Career Chat":
    st.subheader("💬 Career Chat")
    st.caption("Talk through your skills, career direction, or job search with an AI career coach.")
    st.warning("⚠️ AI-generated responses. This assistant does not browse the internet or verify facts beyond your analyzed resume data — always double-check any specific advice.")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if st.button("🗑️ Clear Conversation"):
        st.session_state["chat_messages"] = []
        st.rerun()

    # Display conversation so far
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask about your career, skills, or job search...")
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})

        cv_analysis = st.session_state.get("result", {}).get("cv_analysis")
        jd_analysis = st.session_state.get("result", {}).get("jd_analysis")

        with st.spinner("Thinking..."):
            from chat.career_chat import get_chat_response
            reply = get_chat_response(st.session_state["chat_messages"], cv_analysis, jd_analysis)

        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        st.rerun()