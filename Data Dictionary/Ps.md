ps11
Objective
Build a software-only solution that connects to enterprise databases (Snowflake, PostgreSQL, SQL Server, etc.) and automatically generates comprehensive, AI-enhanced data dictionaries. It should extract schema metadata, analyze data quality, and produce business-friendly documentation. An interactive chat interface should allow users to query and understand the data through natural language.

Challenge
Database documentation is often outdated, incomplete, or non-existent. Technical metadata lacks business context, making it difficult for analysts and business users to understand what data means and how to use it. Your mission is to create a platform that:

- Connects to multiple database types and extracts complete schema metadata (tables, columns, relationships, constraints)
- Performs intelligent data quality analysis with metrics like completeness, freshness, and key health, mathematical statistical analysis of the data on the go would be a plus.
- Uses AI to generate business-friendly summaries and usage recommendations for each table
- Produces documentation in multiple formats (JSON, Markdown) and stores artifacts for future reference
- Provides a conversational chat interface where users can ask natural language questions about their database schema

You may optionally add features to:
  - Support incremental updates when schema changes are detected
  - Visualize data lineage and table relationships
  - Generate SQL query suggestions based on user questions
  - Provide data quality alerts and trend monitoring


Tools Allowed
Any software-based stack — no hardware required. 

Key Focus
Accurate metadata extraction, meaningful AI-generated business context, and intuitive natural language access to database documentation.


# Data Dictionary Monorepo

This repository now contains two top-level projects:

- `backend/` — FastAPI backend (Python)
- `frontend/` — Next.js frontend (TypeScript/React)

To run this project directory:

1. Backend

```bash
# from repo root
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# copy .env.example to .env and fill credentials
uvicorn app.main:app
```

API endpoints (examples):

- GET /healthz
- GET /api/extract/all
- GET /api/quality/table/{table_name}?sample=500
- POST /api/ai/summarize  (body: {"schema": {...}})
- GET /api/export/markdown/{table_name}

Notes:
- Snowflake and SQL Server connectors are thin wrappers; some operations may be synchronous.
- Groq integration is a placeholder and expects `GROQ_API_KEY` in environment.

2. Frontend

```bash
# from repo root
cd frontend
# install with pnpm or npm
npm install
npm run dev
```

Notes

- Backend reads DB and Groq config from `backend/.env` (copy from `backend/.env.example`).
- Frontend files were moved into `frontend/` to keep concerns separated.
- Some connectors (Snowflake, SQL Server) use synchronous drivers; in production consider async alternatives or run blocking calls in executors.
To run this Data Dictionary Project: