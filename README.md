# 🛡️ AI-Powered Cybersecurity Quiz & Diagnostic Engine (COE)

An intelligent, RAG-grounded assessment system designed for Cybersecurity Learning Management Systems (LMS). Built with **Ollama (Qwen 2.5 3B)**, **ChromaDB**, **Pydantic Guardrails**, and **Streamlit**.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Project Architecture & Directory Structure](#-project-architecture--directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [LMS Portal Integration Guide](#-lms-portal-integration-guide)
- [Environment Variables](#-environment-variables)

---

## 🚀 Overview

This repository provides an automated, AI-driven assessment prototype that powers two critical LMS workflows:
1. **Post-Login Placement Diagnostic**: Evaluates student knowledge levels on onboarding to route them into either **Beginner** or **Advanced (Red/Blue Team)** learning tracks.
2. **End-of-Module RAG Chapter Quiz**: Generates multiple-choice assessments strictly grounded in textbook course material stored in **ChromaDB**, preventing AI hallucinations.

---

## ✨ Key Features

- **Strict Schema Enforcement**: Powered by **Pydantic** (`QuizResponse`, `QuestionSchema`) to guarantee structured JSON output containing questions, realistic options, correct answers, and technical explanations.
- **RAG-Grounded Assessments**: Retrieves module context from **ChromaDB** to ensure questions strictly assess course material.
- **Local LLM Execution**: Uses **Ollama (`qwen2.5:3b`)** for fast, local inference without external API costs or privacy leaks.
- **Realistic Distractors**: Enforces distractor rules so wrong choices are valid cybersecurity terms rather than arbitrary distractors.

---

## 📂 Project Architecture & Directory Structure

```
AI_quiz_COE/
│
├── app.py                      # Interactive Streamlit Web UI (Diagnostic & Chapter Quizzes)
├── quiz_engine.py              # Core logic for Qwen prompt construction, JSON parsing & RAG workflow
├── prepare_data.py             # Script for preparing dataset & loading documents into vector store
│
├── schemas/
│   └── quiz_schemas.py         # Pydantic models (QuizResponse, QuestionSchema)
│
├── vectorstore/
│   └── dummy_chroma.py         # ChromaDB collection setup & semantic context retrieval functions
│
├── data/
│   ├── sample_kaggle.csv       # Sample raw cybersecurity dataset
│   └── train_topics.jsonl      # Formatted topic & chapter datasets
│
├── .env                        # Local environment configuration (Ignored by Git)
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusion rules for bytecode, secrets, and virtualenv
└── README.md                   # Project documentation
```

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed on your machine:

1. **Python 3.10 or higher**
   - Verify installation: `python --version`
2. **Ollama** (Local LLM runner)
   - Download & Install from: [https://ollama.com](https://ollama.com)
   - Pull the Qwen 2.5 3B model:
     ```bash
     ollama pull qwen2.5:3b
     ```
   - Ensure Ollama is running locally (default: `http://localhost:11434`).

---

## 🛠️ Installation & Setup

1. **Clone the Repository & Navigate to Folder**:
   ```bash
   git clone <your-repo-url>
   cd AI_Quiz(COE)/AI_quiz_COE
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   # Windows (PowerShell / CMD)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install streamlit chromadb pydantic ollama python-dotenv pandas
   ```

4. **Set Up Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

---

## 🖥️ Running the Application

Ensure your virtual environment is active and Ollama is running in the background.

Navigate into `AI_quiz_COE` and launch Streamlit:

```bash
cd AI_quiz_COE
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🔗 LMS Portal Integration Guide

If you need to connect this AI Quiz Engine to a **Full LMS Portal Website** (e.g., Moodle, Canvas, or a custom React/Node.js/Django/FastAPI LMS), follow the architecture blueprint below:

### 1. New Files to Create for LMS Integration

| File to Add | Purpose |
| :--- | :--- |
| **`api.py`** (FastAPI / Flask Server) | Expose REST API endpoints (`/api/v1/quiz/placement` & `/api/v1/quiz/chapter`) so the LMS frontend/backend can request dynamically generated quizzes. |
| **`models.py`** (Database ORM - SQLAlchemy / Prisma) | Store student quiz attempts, question history, scores, track routing results (Beginner vs Advanced), and timestamps. |
| **`lti_handler.py`** (Optional LTI 1.3 Provider) | Enables seamless single sign-on (SSO) and direct grade passback into platforms like Moodle or Canvas. |
| **`services/user_service.py`** | Updates student learning paths based on diagnostic score output from `quiz_engine.py`. |

### 2. Files to Modify

- **[`quiz_engine.py`](file:///c:/Users/Moksha/OneDrive/Desktop/AI_Quiz%28COE%29/AI_quiz_COE/quiz_engine.py)**: Pass `user_id` and `module_id` parameters into functions to pull tailored user history or specific module contents.
- **[`vectorstore/dummy_chroma.py`](file:///c:/Users/Moksha/OneDrive/Desktop/AI_Quiz%28COE%29/AI_quiz_COE/vectorstore/dummy_chroma.py)**: Upgrade from in-memory ChromaDB to a persistent vector store directory (`CHROMA_PERSIST_DIRECTORY`) or persistent server instance.

### 3. Example REST API Endpoint (`api.py`)

Below is a starter snippet using **FastAPI** to connect `quiz_engine.py` with your web portal:

```python
from fastapi import FastAPI, HTTPException
from quiz_engine import generate_placement_quiz, generate_chapter_quiz
from schemas.quiz_schemas import QuizResponse

app = FastAPI(title="LMS AI Quiz Microservice")

@app.post("/api/v1/quiz/placement", response_model=QuizResponse)
def get_placement_quiz(level: str = "beginner"):
    try:
        return generate_placement_quiz(target_level=level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/quiz/chapter", response_model=QuizResponse)
def get_chapter_quiz(chapter_title: str, difficulty: str = "beginner"):
    try:
        return generate_chapter_quiz(chapter_title=chapter_title, difficulty=difficulty)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## ⚙️ Environment Variables

Configuration settings located in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
APP_ENV=development
DEBUG=True
PORT=8000
```
