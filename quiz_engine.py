import json
import uuid
from ollama import chat
from schemas.quiz_schemas import QuizResponse
from vectorstore.dummy_chroma import get_chroma_collection, retrieve_chapter_context

def _clean_and_parse_json(raw_text: str) -> dict:
    """Isolates the JSON substring to avoid markdown/preamble parse errors."""
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No valid JSON object found in model output.")
    return json.loads(raw_text[start:end])

# ==========================================
# 1. POST-LOGIN PLACEMENT QUIZ (No RAG)
# ==========================================
def generate_placement_quiz(target_level: str = "beginner") -> QuizResponse:
    """
    Generates a 2-question placement diagnostic to determine 
    if the user routes to the Beginner module or Advanced track.
    """
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

    parsed = _clean_and_parse_json(response["message"]["content"])
    return QuizResponse(**parsed)

# ==========================================
# 2. END-OF-MODULE CHAPTER QUIZ (RAG Grounded)
# ==========================================
def generate_chapter_quiz(chapter_title: str, difficulty: str = "beginner") -> QuizResponse:
    """
    Retrieves context from ChromaDB and forces Qwen to generate questions 
    strictly bounded by that context.
    """
    # Step A: Retrieve context from ChromaDB
    collection = get_chroma_collection()
    context = retrieve_chapter_context(collection, chapter_title)
    
    if not context:
        raise ValueError(f"No context found in ChromaDB for: {chapter_title}")

    # Step B: Construct RAG Prompt
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

    parsed = _clean_and_parse_json(response["message"]["content"])
    return QuizResponse(**parsed)