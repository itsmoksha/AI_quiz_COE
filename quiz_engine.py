import json
import uuid
from ollama import chat
from schemas.quiz_schemas import QuizResponse
from vectorstore.dummy_chroma import get_chroma_collection, retrieve_chapter_context

from guardrails.pipeline import apply_input_guardrails, apply_output_guardrails

# ==========================================
# 1. POST-LOGIN PLACEMENT QUIZ (No RAG)
# ==========================================
def generate_placement_quiz(target_level: str = "beginner") -> QuizResponse:
    """
    Generates a 2-question placement diagnostic to determine 
    if the user routes to the Beginner module or Advanced track.
    """
    # Apply Input Guardrails
    apply_input_guardrails(target_level)
    
    prompt = f"""
You are an expert cybersecurity examiner evaluating a student's placement level.
Generate exactly 20 multiple-choice questions for a {target_level.upper()} diagnostic test.
Ensure the questions are highly diverse and cover different concepts each time. (Randomization Seed: {uuid.uuid4()})

=== REQUIREMENTS ===
1. Quiz Type: placement
2. Target Level: {target_level} (Beginner = basic terms/concepts; Advanced = attack scenarios/architecture).
3. Exactly 4 options per question.
4. Distractor Rule: The 3 wrong choices MUST be realistic cybersecurity terms, not absurd or silly answers.
5. Strict output format: Return ONLY valid JSON matching this schema:
{{
  "quiz_type": "placement",
  "topic_or_chapter": "General Placement ({target_level})",
  "difficulty": "{target_level}",
  "questions": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": "string (must match one option exactly)",
      "explanation": "string"
    }}
  ]
}}
"""
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "system", "content": "You are a cybersecurity examiner that outputs strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        format="json",
        options={"temperature": 0.8}
    )

    # Apply Output Guardrails
    parsed = apply_output_guardrails(response["message"]["content"])
    return QuizResponse(**parsed)

# ==========================================
# 2. END-OF-MODULE CHAPTER QUIZ (RAG Grounded)
# ==========================================
def generate_chapter_quiz(chapter_title: str, difficulty: str = "beginner") -> QuizResponse:
    """
    Retrieves context from ChromaDB and forces Qwen to generate questions 
    strictly bounded by that context.
    """
    # Step A: Apply Input Guardrails
    apply_input_guardrails(chapter_title)
    apply_input_guardrails(difficulty)

    # Step B: Retrieve context from ChromaDB
    collection = get_chroma_collection()
    context = retrieve_chapter_context(collection, chapter_title)
    
    if not context:
        raise ValueError(f"No context found in ChromaDB for: {chapter_title}")

    # Step C: Construct RAG Prompt
    prompt = f"""
You are an expert cybersecurity examiner. Generate exactly 20 multiple-choice questions strictly from the CONTEXT provided below.
Ensure the questions are highly diverse and test different parts of the context each time. (Randomization Seed: {uuid.uuid4()})

=== CONTEXT ===
{context}

=== REQUIREMENTS ===
1. Quiz Type: chapter
2. Difficulty: {difficulty}
3. Plausible Distractors: All 4 options must be related technical terms.
4. Grounding: Do NOT invent facts outside the provided CONTEXT.
5. Strict output format: Return ONLY valid JSON matching this schema:
{{
  "quiz_type": "chapter",
  "topic_or_chapter": "{chapter_title}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": "string (must match one option exactly)",
      "explanation": "string"
    }}
  ]
}}
"""
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "system", "content": "You are a cybersecurity quiz engine that outputs strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        format="json",
        options={"temperature": 0.8}
    )

    # Apply Output Guardrails (with Context for Grounding Check)
    parsed = apply_output_guardrails(response["message"]["content"], context=context)
    return QuizResponse(**parsed)