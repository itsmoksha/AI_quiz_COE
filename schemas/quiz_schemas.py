from pydantic import BaseModel, Field
from typing import List, Literal

class QuestionSchema(BaseModel):
    question: str = Field(description="The question text.")
    options: List[str] = Field(
        min_length=4, 
        max_length=4, 
        description="Exactly 4 distinct multiple-choice options."
    )
    correct_answer: str = Field(
        description="The exact string matching one of the options."
    )
    explanation: str = Field(
        description="Technical justification explaining why the answer is correct."
    )

class QuizResponse(BaseModel):
    quiz_type: Literal["placement", "chapter"] = Field(
        description="Identifies whether this is a diagnostic placement or module chapter quiz."
    )
    topic_or_chapter: str = Field(description="The topic or chapter identifier.")
    difficulty: Literal["beginner", "advanced"] = Field(
        description="Target difficulty level."
    )
    questions: List[QuestionSchema] = Field(
        description="List of validated multiple-choice questions."
    )