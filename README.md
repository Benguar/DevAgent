# DevAgent

DevAgent is a command-line RAG assistant for asking questions about PDF documents. It extracts and semantically chunks PDF text, stores embeddings in PostgreSQL with pgvector, then gives llm only the most relevant chunks when answering a question.

## Requirements

- Python 3.14+
- PostgreSQL with the pgvector extension
- A Google Gemini API key
- Internet access the first time FastEmbed downloads its model

Dependencies are defined in [`pyproject.toml`](pyproject.toml).

## Setup

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Create `.env` in the project root:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/devagent
GEMINI_API_KEY=your_gemini_api_key
```

Create the database before running the application. On startup, the project enables pgvector and creates `devagent_table` automatically. The database user must be allowed to install the `vector` extension.

## Architecture
[Architecture](./architecture.drawio.png)

## Usage

Index a PDF:

```powershell
python -m ochestration.pdf_save
```

Enter the PDF path when prompted. The ingestion process:

1. Converts the PDF to Markdown with `pymupdf4llm`.
2. Uses Gemini to split the text into topic-based JSON chunks.
3. Creates 384-dimensional embeddings with `BAAI/bge-small-en-v1.5`.
4. Saves each chunk and embedding in PostgreSQL.

Ask questions about indexed documents:

```powershell
python -m ochestration.main
```

The assistant embeds each question, uses cosine similarity to retrieve up to two chunks below the `0.4` distance threshold, and sends those chunks to `gemini-3.1-flash-lite`. If the database context does not contain the answer, it is instructed to say so.

## Project Files

- [`ochestration/pdf_save.py`](ochestration/pdf_save.py): PDF extraction, chunking, embedding, and storage
- [`ochestration/main.py`](ochestration/main.py): interactive retrieval and answering
- [`database/models.py`](database/models.py): pgvector model and table creation
- [`database/conn.py`](database/conn.py): SQLAlchemy connection and sessions
- [`core/settings.py`](core/settings.py): environment-backed settings

## Current Limitations

- Retrieval is limited to two chunks and a fixed similarity threshold.
- There is no delete command, duplicate detection, page metadata, or source filtering.
- Ingestion depends on Gemini returning valid JSON in the expected format.
- Schema creation happens at import time; migrations are not configured.
- Changing the embedding model requires re-indexing existing documents.
