# Neighborhood Library Service

A modern library management application for a small neighborhood library branch.
Staff-operated (no member login required). Built with a Python/FastAPI backend,
Next.js frontend, and PostgreSQL database.

---

## Features

- **Book management** — add, edit, search books with availability tracking
- **Member management** — register and manage library members
- **Borrow / return workflow** — issue books, process returns, automatic overdue detection
- **AI-powered book enrichment** — auto-generate summaries, tags, and reading levels via OpenAI
- **Member book recommendations** — personalised suggestions based on borrowing history
- **Overdue reminder generation** — draft reminder messages for overdue borrowings
- **PDF upload** — attach PDF files to book records (optional)

---

## Architecture

The application follows a clean layered architecture:

```
HTTP Request
    │
    ▼
Routes (FastAPI routers)
    │
    ▼
Services (business logic)
    │
    ▼
Repositories (database access)
    │
    ▼
Database (PostgreSQL via SQLAlchemy)
```

---

## Assumptions

- Single neighborhood library branch
- Staff-operated — library staff use the app on behalf of members; members do not log in
- Expected scale: 500–5 000 members, 2 000–20 000 books
- AI features are optional assistive enhancements — the application works fully without an OpenAI API key (a `MockAIProvider` is used instead)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Database** | PostgreSQL 15 |
| **AI** | OpenAI GPT-4o (optional); MockAIProvider as fallback |
| **Containerisation** | Docker, Docker Compose |

---

## Local Setup

### Prerequisites

- **Docker & Docker Compose** (recommended), **or**
- Python 3.11+, Node.js 20+, PostgreSQL 15+

---

### Quick Start with Docker

```bash
git clone <repo>
cd neighborhood-library-service
cp .env.example .env
# Optionally add your OPENAI_API_KEY to .env
docker compose up --build
```

Once running, open:

| URL | Description |
|---|---|
| http://localhost:3000 | Frontend UI |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger UI (interactive API docs) |

---

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL instance
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://library:library@postgres:5432/library_db` |
| `SECRET_KEY` | Application secret key | — (required in production) |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `""` (MockAIProvider used when empty) |
| `PDF_UPLOAD_DIR` | Directory for uploaded PDFs | `./uploads/pdfs` |
| `MAX_BORROW_DAYS` | Default loan period in days | `14` |
| `MAX_ACTIVE_BORROWINGS` | Maximum concurrent borrowings per member | `5` |
| `DEBUG` | Enable debug mode | `false` |
| `NEXT_PUBLIC_API_URL` | Backend API URL (frontend) | `http://localhost:8000` |

Copy `.env.example` to `.env` and update values as needed.

---

## Database Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Create a new migration from model changes
alembic revision --autogenerate -m "description"

# Roll back the last migration
alembic downgrade -1
```

---

## Seed Data

Populate the database with sample books, members, and borrow transactions:

```bash
cd backend
python scripts/seed_data.py
```

This creates:
- **8 books** across categories: Self-Help, Fiction, History, Technology, Science
- **5 members** (4 active, 1 inactive)
- **3 borrow transactions** — one active, one overdue, one returned

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## API Documentation

| URL | Description |
|---|---|
| http://localhost:8000/docs | Swagger UI — interactive exploration |
| http://localhost:8000/redoc | ReDoc — clean reference documentation |

---

## AI Features

AI features are powered by OpenAI and activated when `OPENAI_API_KEY` is set.
When the key is absent, a `MockAIProvider` returns placeholder responses so
the application remains fully functional.

| Feature | Description |
|---|---|
| **Book enrichment** | Generates a summary, tags, reading level, and audience recommendation for a book |
| **Member recommendations** | Suggests books based on a member's borrowing history |
| **Overdue reminders** | Drafts a polite reminder message for a member with overdue books |

Trigger enrichment from the book detail page, and recommendations from the
member detail page in the frontend UI.

---

## AWS Deployment

See **[docs/aws-deployment.md](docs/aws-deployment.md)** for the full deployment guide.

**Summary:**
- ECS Fargate runs backend and frontend containers
- RDS PostgreSQL for the managed database
- S3 for PDF file storage
- Application Load Balancer for traffic routing
- CloudWatch Logs for centralised log aggregation
- Secrets Manager for `DATABASE_URL`, `SECRET_KEY`, and `OPENAI_API_KEY`

A sample ECS task definition is provided at
[docs/ecs-task-definition.json](docs/ecs-task-definition.json).

---

## Future Improvements

- Member authentication portal (self-service borrowing history)
- Fine tracking and payment workflow
- Email / SMS notifications for due-date reminders
- Mobile application (React Native)
- Advanced analytics dashboard (popular books, borrowing trends)
- Multi-branch support

