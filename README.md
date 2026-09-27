# Student Database Backend

A modular FastAPI backend for managing student records, with a LangGraph + Gemini-powered chatbot that can query the database in natural language.

## Tech Stack

- **Backend:** Python + FastAPI
- **Database:** SQLite (via SQLAlchemy ORM)
- **AI Chatbot:** Google Gemini + LangGraph
- **Vector Search:** ChromaDB (embedded)
- **API Docs:** FastAPI Swagger/OpenAPI

## Project Structure

```
app/
├── main.py              # App entrypoint
├── core/
│   ├── config.py         # Settings (env vars)
│   └── database.py       # SQLAlchemy engine/session
├── models/
│   └── student.py        # Student ORM model
├── schemas/
│   └── student.py        # Pydantic request/response schemas
├── crud/
│   └── student.py        # Database operations
├── api/routes/
│   ├── students.py        # CRUD endpoints
│   └── chat.py             # Chatbot endpoint
└── chatbot/
    ├── tools.py           # LangGraph tools (DB queries)
    ├── graph.py           # LangGraph workflow
    └── vector_store.py    # ChromaDB embedding + semantic search
```

## Setup

1. Clone the repository and navigate into it.
2. Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (see `.env.example`):

```
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the server:

```
uvicorn app.main:app --reload
```

6. Open Swagger docs at `http://127.0.0.1:8000/docs`

## API Endpoints

### Students (CRUD)

- `POST /students/` — Create a student
- `GET /students/` — List all students
- `GET /students/{id}` — Get a student by ID
- `PUT /students/{id}` — Update a student
- `DELETE /students/{id}` — Delete a student

### Chatbot

- `POST /chat/` — Ask a natural-language question about student data

## Deployment

See the included `Dockerfile` to build and run this as a container:

```
docker build -t student-db-backend .
docker run -p 8000:8000 --env-file .env student-db-backend
```

## Vector Database

**Choice: ChromaDB**

### Why ChromaDB

- **Embedded, no separate server**: Runs as a local persistent client (`./chroma_db`), matching the project's SQLite-based, dependency-light architecture — no extra infrastructure to deploy or manage.
- **Free and open-source**: No API costs or usage limits, unlike managed options like Pinecone.
- **Native LangChain/LangGraph support**: Integrates directly as a callable tool in the chatbot's LangGraph workflow with minimal glue code.
- **Sufficient for project scale**: Designed for a class-sized student dataset, not a production-scale workload — ChromaDB's performance profile is well within that range.

### Trade-off

ChromaDB does not scale to production-size, multi-million-record workloads the way managed vector databases (Pinecone, Weaviate) do. That scale is not required here, and adopting a managed service would mean an extra external dependency, sign-up, and API key for no practical benefit at this project's size.

### Implementation

- Student records are embedded via Google's Generative AI embedding function and synced into a ChromaDB collection on server startup (`app/chatbot/vector_store.py`).
- A dedicated LangGraph tool, `search_students_by_meaning`, lets the chatbot answer semantic/fuzzy questions (e.g. "who is studying something related to quantum mechanics?") by meaning rather than exact keyword match, alongside the existing exact-match tools (`get_all_students`, `get_student_by_name`).
