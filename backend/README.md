# Enterprise Knowledge Assistant - Backend

The FastAPI-based backend application responsible for multi-tenant authentication, semantic document chunking/indexing, and context retrieval for conversational queries.

---

## Technical Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Vector DB:** Qdrant Cloud or Local instance
- **LLM/Embeddings:** Ollama (local Phi3-mini engine)
- **Workflow & Testing:** pytest, ruff, black, uv

---

## Development Setup

1. **Install uv Package Manager:**
   Ensure `uv` is installed on your system. If not, follow instructions from [astral.sh/uv](https://astral.sh/uv).
2. **Install Dependencies:**
   Run from the `backend/` directory:
   ```bash
   uv pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Copy `.env.template` to `.env` and fill in your local Postgres database details, JWT secrets, Qdrant URL/API Key, and Ollama connection parameters:
   ```bash
   cp .env.template .env
   ```
4. **Initialize Database:**
   Schemas are created dynamically during the application lifespan/startup.

---

## Running Commands

All commands can be run from the `backend/` directory:

- **Start FastAPI Development Server:**
  ```bash
  uv run uvicorn main:app --reload
  ```
- **Run Tests:**
  ```bash
  uv run pytest
  ```
- **Format Code:**
  ```bash
  uv run ruff format .
  ```
- **Lint Code:**
  ```bash
  uv run ruff check .
  ```

---

## Utility Diagnostics Scripts

Several testing/verification scripts are available in the `scripts/` directory to troubleshoot integrations:
- `check_ollama.py` - Verifies Phi-3 connectivity and model availability.
- `check_qdrant.py` - Asserts Qdrant collection presence and write privileges.
- `check_indexing.py` - Runs sample file index pipeline diagnostics.
- `check_retrieval.py` - Runs target text retrieval searches.
- `inspect_qdrant.py` - Returns vector indexes details.

Run any script like so:
```bash
uv run python scripts/check_ollama.py
```
