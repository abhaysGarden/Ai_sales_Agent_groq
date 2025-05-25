
# Sales Assistant AI Backend

This repository contains the backend implementation for a Sales Assistant AI. It analyzes incoming messages from prospects, performs knowledge base and CRM lookups, and synthesizes helpful responses with recommended next steps.

## Features

- Intent, sentiment, and entity analysis using OpenAI's GPT models.
- Knowledge augmentation via CRM data and a FAISS-backed knowledge base.
- Tool usage logging for auditability.
- Response synthesis with actionable next steps.
- Evaluation utilities for model output quality.

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) or pip for dependency management
- An OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/sales-assistant-ai.git
cd sales-assistant-ai
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Prepare data:

Ensure the following JSON files are present in the `data/` directory:

- `crm.json` : Contains CRM prospect data.
- `kb.json` : Contains knowledge base documents.

5. Set environment variables:

Create a `.env` file in the root directory and add:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
```

You can adjust `OPENAI_MODEL` and `OPENAI_TEMPERATURE` as needed.

### Running the API

Run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### API Endpoint

- `POST /process_message`

Request Body:

```json
{
  "conversation_history": [
    {
      "timestamp": "2025-05-21T10:00:00Z",
      "sender": "user",
      "content": "Hello, can you tell me about your products?"
    }
  ],
  "current_prospect_message": "I'm interested in pricing details.",
  "prospect_id": "12345"
}
```

Response includes analysis, suggested response, next steps, tool usage logs, and confidence scores.

## Evaluation

The `app/evaluation/evaluation.py` module provides utilities to evaluate model predictions against a golden dataset, including intent accuracy, entity F1, response BLEU scores, and tool/step accuracy.

## Notes

- The knowledge base uses SentenceTransformers and FAISS for semantic search.
- For best results, ensure data files are properly formatted JSON.
- Logging is enabled to monitor loading errors and warnings.

## License

MIT License

---

For questions or contributions, please open an issue or submit a pull request.
