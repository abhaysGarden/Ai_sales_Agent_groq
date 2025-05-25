# Architecture Document

## 1. Overview

This document explains the architecture of the AI agent backend system designed for sales conversation analysis and response generation. The system orchestrates multiple components including LLMs, external tool integrations, data storage, and evaluation modules to deliver real-time, context-aware interactions.

---

## 2. System Architecture

```plaintext
+-------------------+        +----------------+        +------------------+
|   User Interface  | <----> |   Backend API  | <----> | External Tools   |
|  (Web/Mobile App) |        | (FastAPI/Uvicorn) |      | - CRM Database   |
+-------------------+        +----------------+        | - Knowledge Base |
                                                     | - RAG Retrieval  |
                                                     +------------------+
                                                           |
                                                           v
                                                +--------------------+
                                                |    LLM Orchestration |
                                                |  (Prompt Engineering, |
                                                |   Context Management) |
                                                +--------------------+
                                                           |
                                                           v
                                                +---------------------+
                                                |   Data Storage &     |
                                                |    Analytics Layer   |
                                                | (PostgreSQL, Vector  |
                                                |   DB, Logging)       |
                                                +---------------------+
                                                           |
                                                           v
                                                +---------------------+
                                                | Evaluation & Monitoring|
                                                |  (Metrics, Feedback,   |
                                                |   Error Handling)      |
                                                +---------------------+
```

---

## 3. Key Components

### 3.1 User Interface
- Provides chat interface for sales representatives or agents.
- Sends conversation turns and context to backend API.

### 3.2 Backend API
- Built with FastAPI and Uvicorn.
- Handles requests, manages session context.
- Coordinates calls to LLM orchestration and external tools.

### 3.3 LLM Orchestration
- Manages multi-turn dialogue context.
- Uses prompt engineering to generate structured outputs.
- Handles tool invocation commands embedded in LLM responses.
- Combines multiple knowledge sources through Retrieval-Augmented Generation (RAG).

### 3.4 External Tools
- CRM system: retrieves and updates prospect data.
- Knowledge base: fetches relevant documents or answers.
- RAG system: supplies context to LLM from indexed data stores.

### 3.5 Data Storage & Analytics
- PostgreSQL stores conversation logs, intents, entities, and user progress.
- Vector databases store embeddings for quick retrieval in RAG.
- Logging of interaction data for analysis and model fine-tuning.

### 3.6 Evaluation & Monitoring
- Tracks response accuracy, user satisfaction metrics.
- Monitors system errors and flags unusual behavior.
- Supports ongoing improvement of prompts and system design.

---

## 4. Data Flow

1. User sends a message via UI.
2. Backend API receives message and current session context.
3. API invokes LLM orchestration with combined context.
4. LLM generates structured response with possible tool calls.
5. Backend executes tool calls (CRM queries, RAG lookups) if requested.
6. Results merged into final response sent back to user.
7. All interactions logged for evaluation.

---

## 5. Design Decisions

- **FastAPI for backend**: Lightweight, async-friendly for real-time chat.
- **LLM orchestration**: Separates prompt management from tool execution for modularity.
- **Structured outputs from LLM**: Ensures predictable, machine-readable responses.
- **RAG integration**: Combines generative power of LLM with factual retrieval to reduce hallucination.
- **PostgreSQL + Vector DB**: Hybrid storage supports relational data and semantic search.
- **Monitoring & Evaluation**: Essential for production readiness and continuous improvement.
