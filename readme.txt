# AI Study & Code Assistant

## Overview

AI Study & Code Assistant is an AI-powered learning platform that helps students study more effectively and understand programming concepts through intelligent document analysis and code assistance.

The system allows users to upload study materials such as PDF, DOCX, TXT, and source code files, then interact with the content through a conversational AI interface. In addition to question answering, the platform can automatically generate quizzes, flashcards, mind maps, and code analysis to improve learning outcomes.

This project is inspired by modern AI learning tools such as NotebookLM while extending functionality to support programming education.

---

## Objectives

* Provide an AI-powered study assistant for educational materials.
* Enable users to chat with uploaded documents.
* Generate quizzes automatically from study notes.
* Create flashcards for revision and memorization.
* Generate structured mind maps from learning materials.
* Assist students in understanding and improving source code.
* Demonstrate practical applications of Large Language Models (LLMs) in education.

---

## Features

### Study Assistant

#### Document Upload

Supported file formats:

* PDF
* DOCX
* TXT

#### Chat With Notes

Users can ask questions about uploaded study materials.

Examples:

* Summarize this chapter.
* Explain this concept.
* What are the key points?
* Give me a beginner-friendly explanation.

#### Quiz Generator

Automatically creates multiple-choice questions based on uploaded content.

#### Flashcard Generator

Creates revision flashcards to support active recall learning.

#### Mind Map Generator

Generates structured topic hierarchies to visualize relationships between concepts.

---

### Code Assistant

Supported file formats:

* Python (.py)
* Java (.java)
* JavaScript (.js)
* C++ (.cpp)
* HTML (.html)
* CSS (.css)

#### Code Explanation

Provides beginner-friendly explanations of source code.

#### Bug Detection

Identifies potential errors and coding issues.

#### Code Optimization

Suggests improvements for readability and performance.

---

## System Architecture

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ├── File Processor
  ├── Study Tools
  ├── Code Analyzer
  └── AI Engine
          │
          ▼
      Groq API
      (Llama Models)
```

---

## Technology Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Uvicorn

### AI Models

* Groq API
* Llama 3.1 8B Instant
* Llama 3.3 70B Versatile (Optional Upgrade)

### Document Processing

* PyPDF
* Python-Docx

### Environment Management

* Python 3.11
* Virtual Environment (venv)

---

## Project Structure

```text
StudyAssistant/
│
├── app/
│   ├── main.py
│   ├── ai_engine.py
│   ├── file_processor.py
│   ├── study_tools.py
│   ├── code_analyzer.py
│   └── __init__.py
│
├── streamlit_app.py
├── requirements.txt
├── .env
├── test_groq.py
└── README.md
```

---

## Installation

### Create Virtual Environment

```bash
py -3.11 -m venv .senv
```

### Activate Virtual Environment

Windows PowerShell:

```bash
.senv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root directory:

```env
GROQ_API_KEY=YOUR_API_KEY
GROQ_MODEL=llama-3.1-8b-instant
```

---

## Running the Application

### Start Backend

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Start Frontend

```bash
streamlit run streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

---

## Future Improvements

* Retrieval-Augmented Generation (RAG)
* Vector Database Integration (FAISS)
* Source Citation Support
* Interactive Visual Mind Maps
* Multi-Document Chat
* Document Comparison
* UML Diagram Generation
* Complexity Analysis
* AI Study Planner Integration
* User Authentication and Saved Sessions

---

## Educational Value

This project demonstrates the integration of:

* Natural Language Processing (NLP)
* Large Language Models (LLMs)
* Prompt Engineering
* Document Processing
* Educational Technology
* Software Engineering Principles
* Full-Stack Application Development

---

## Author

Developed as a Final Year Project for CSC351.

AI Study & Code Assistant aims to improve learning efficiency by combining intelligent document understanding with programming support in a unified educational platform.
