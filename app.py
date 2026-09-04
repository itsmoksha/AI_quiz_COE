import streamlit as st
from quiz_engine import generate_placement_quiz, generate_chapter_quiz
from vectorstore.dummy_chroma import get_chroma_collection

st.set_page_config(page_title="Cybersecurity LMS - AI Quiz Prototype", page_icon="🛡️", layout="centered")

st.title("🛡️ AI-Powered Cybersecurity LMS")
st.caption("Local Qwen 2.5 3B (Ollama) + ChromaDB RAG + Pydantic Guardrails")

# Initialize Vector DB in session state
if "chroma_col" not in st.session_state:
    st.session_state.chroma_col = get_chroma_collection()

# Create Tabs for the two core user workflows
tab1, tab2 = st.tabs(["1. Post-Login Placement Test", "2. End-of-Module Chapter Quiz (RAG)"])

# ==========================================
# TAB 1: PLACEMENT TEST (Track Routing)
# ==========================================
with tab1:
    st.header("🎯 Student Onboarding & Track Routing")
    st.write("Take a quick diagnostic evaluation to determine whether you route to the **Beginner Module** or **Advanced (Red/Blue Team) Track**.")
    
    target_level = st.selectbox("Select Target Diagnostic Level:", ["beginner", "advanced"], key="placement_level")
    
    if st.button("Generate Placement Quiz", key="btn_placement"):
        with st.spinner("Generating diagnostic assessment via local Qwen model..."):
            try:
                quiz_data = generate_placement_quiz(target_level)
                st.session_state.placement_quiz = quiz_data
                st.session_state.placement_submitted = False
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if "placement_quiz" in st.session_state:
        quiz = st.session_state.placement_quiz
        st.info(f"**Track:** {quiz.topic_or_chapter.title()} | **Difficulty:** {quiz.difficulty.title()}")
        
        placement_answers = {}
        with st.form("placement_form"):
            for i, q in enumerate(quiz.questions):
                st.markdown(f"**Q{i+1}: {q.question}**")
                placement_answers[i] = st.radio(
                    f"Choose option for Q{i+1}",
                    q.options,
                    key=f"p_opt_{i}",
                    label_visibility="collapsed"
                )
                st.write("")
            
            p_submit = st.form_submit_button("Submit Placement Test")
            if p_submit:
                st.session_state.placement_submitted = True

        if st.session_state.get("placement_submitted", False):
            score = 0
            total = len(quiz.questions)
            st.divider()
            st.subheader("Placement Evaluation Results")
            
            for i, q in enumerate(quiz.questions):
                user_choice = placement_answers[i]
                if user_choice == q.correct_answer:
                    score += 1
                    st.success(f"**Q{i+1}: Correct!**")
                else:
                    st.error(f"**Q{i+1}: Incorrect.** Your choice: `{user_choice}`")
                    st.info(f"**Correct Answer:** `{q.correct_answer}`")
                st.caption(f"💡 **Explanation:** {q.explanation}")
                st.write("---")
            
            score_pct = (score / total) * 100
            st.metric("Diagnostic Score", f"{score} / {total} ({score_pct}%)")
            
            if target_level == "advanced":
                if score_pct >= 50:
                    st.balloons()
                    st.success("🎉 **Passed!** Routed to **Advanced Track (Red/Blue Teaming)**.")
                else:
                    st.warning("⚠️ **Score below threshold.** Routed to **Beginner Module**.")
            else:
                st.info("📚 **Assigned to Beginner Module.** Complete your chapter readings to proceed.")

# ==========================================
# TAB 2: CHAPTER QUIZ (RAG Grounded)
# ==========================================
with tab2:
    st.header("📖 End-of-Module Chapter Assessment (RAG)")
    st.write("Generates a quiz grounded strictly in retrieved textbook context stored in ChromaDB.")
    
    chapter_choice = st.selectbox("Select Completed Chapter:", [
        "SQL Injection & Defense",
        "Kubernetes Container Health"
    ], key="chapter_select")
    
    chapter_diff = st.selectbox("Select Difficulty:", ["beginner", "advanced"], key="chap_diff")

    if st.button("Generate Context-Grounded Quiz", key="btn_chapter"):
        with st.spinner("Retrieving vector chunks from ChromaDB & generating quiz..."):
            try:
                chapter_quiz = generate_chapter_quiz(chapter_choice, chapter_diff)
                st.session_state.chapter_quiz = chapter_quiz
                st.session_state.chapter_submitted = False
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if "chapter_quiz" in st.session_state:
        c_quiz = st.session_state.chapter_quiz
        st.info(f"**Module Chapter:** {c_quiz.topic_or_chapter}")
        
        chap_answers = {}
        with st.form("chapter_form"):
            for i, q in enumerate(c_quiz.questions):
                st.markdown(f"**Q{i+1}: {q.question}**")
                chap_answers[i] = st.radio(
                    f"Choose option for chapter Q{i+1}",
                    q.options,
                    key=f"c_opt_{i}",
                    label_visibility="collapsed"
                )
                st.write("")
            
            c_submit = st.form_submit_button("Submit Chapter Quiz")
            if c_submit:
                st.session_state.chapter_submitted = True

        if st.session_state.get("chapter_submitted", False):
            c_score = 0
            c_total = len(c_quiz.questions)
            st.divider()
            st.subheader("Chapter Quiz Evaluation")
            
            for i, q in enumerate(c_quiz.questions):
                user_choice = chap_answers[i]
                if user_choice == q.correct_answer:
                    c_score += 1
                    st.success(f"**Q{i+1}: Correct!**")
                else:
                    st.error(f"**Q{i+1}: Incorrect.** Your choice: `{user_choice}`")
                    st.info(f"**Correct Answer:** `{q.correct_answer}`")
                st.caption(f"💡 **Explanation:** {q.explanation}")
                st.write("---")
            
            st.metric("Final Chapter Score", f"{c_score} / {c_total}")