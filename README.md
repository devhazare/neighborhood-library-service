# Neighborhood Library Service

A modern library management application for a small neighborhood library branch.
Staff-operated (no member login required). Built with a Python/FastAPI backend,
Next.js frontend, and PostgreSQL database.

---

## Features

- **Book management** — add, edit, search books with availability tracking
- **Member management** — register and manage library members
- **Borrow / return workflow** — issue books, process returns, automatic overdue detection
- **Duplicate borrowing prevention** — members cannot borrow the same book twice until returned
- **Fine tracking** — automatic fine calculation for overdue books, payment tracking
- **AI-powered book enrichment** — auto-generate summaries, tags, and reading levels via OpenAI
- **Member book recommendations** — personalised suggestions based on borrowing history
- **Overdue reminder generation** — draft reminder messages for overdue borrowings
- **PDF upload** — attach PDF files to book records with AI metadata extraction
- **Data integrity constraints** — database-level constraints ensure data consistency

---

## Architecture

The application follows a clean layered architecture with strict separation of concerns:

```
HTTP Request
    │
    ▼
Routes (FastAPI routers)     ← Input validation, auth, response formatting
    │
    ▼
Services (business logic)    ← Business rules, orchestration, transactions
    │
    ▼
Repositories (data access)   ← Database queries, CRUD operations
    │
    ▼
Database (PostgreSQL)        ← Data storage with constraints
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| **Routes** | HTTP handling, request validation, authentication, response serialization |
| **Services** | Business logic, validation rules, orchestrating repository calls |
| **Repositories** | Database operations, query building, data mapping |
| **Models** | SQLAlchemy ORM entities with constraints |
| **Schemas** | Pydantic models for request/response validation |

### Key Principles
- Routes never access repositories directly — always through services
- Services handle all business logic and validation
- Repositories are pure data access with no business logic
- Batch operations used to avoid N+1 query patterns

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
| **API** | REST (FastAPI) + gRPC-Web (Protocol Buffers) |
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
| http://localhost:8000 | Backend API (REST) |
| http://localhost:8000/docs | Swagger UI (interactive API docs) |
| localhost:50051 | gRPC Server |

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
| `FINE_PER_DAY` | Fine amount per overdue day | `0.50` |
| `MAX_FINE_AMOUNT` | Maximum fine cap | `25.00` |
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

## API Endpoints

### Books

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/books` | Create a new book |
| `GET` | `/api/v1/books` | List all books |
| `GET` | `/api/v1/books/search` | Search and filter books |
| `GET` | `/api/v1/books/{id}` | Get book by ID |
| `PUT` | `/api/v1/books/{id}` | Update a book |
| `DELETE` | `/api/v1/books/{id}` | Delete a book |
| `POST` | `/api/v1/books/{id}/upload-pdf` | Upload PDF for a book |
| `POST` | `/api/v1/books/{id}/ai-enrich` | AI-enrich book metadata |

**Search Parameters** (`/api/v1/books/search`):
- `q` — Search query (matches title, author, ISBN, publisher)
- `category` — Filter by category
- `author` — Filter by author
- `available_only` — Only show available books (true/false)

### Members

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/members` | Create a new member |
| `GET` | `/api/v1/members` | List all members |
| `GET` | `/api/v1/members/search` | Search and filter members |
| `GET` | `/api/v1/members/{id}` | Get member by ID |
| `PUT` | `/api/v1/members/{id}` | Update a member |
| `DELETE` | `/api/v1/members/{id}` | Delete a member |
| `GET` | `/api/v1/members/{id}/borrowed-books` | Get member's borrowed books |
| `GET` | `/api/v1/members/{id}/recommendations` | Get AI book recommendations |

**Search Parameters** (`/api/v1/members/search`):
- `q` — Search query (matches name, email, membership ID, phone)
- `status` — Filter by status (active/inactive)

### Borrow Operations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/borrow` | Borrow a book |
| `POST` | `/api/v1/return` | Return a book |
| `GET` | `/api/v1/borrow/active` | List active borrowings |
| `GET` | `/api/v1/borrow/overdue` | List overdue borrowings |
| `POST` | `/api/v1/borrow/{id}/generate-reminder` | Generate AI overdue reminder |

### Fines

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/fines/pay` | Pay a fine |
| `GET` | `/api/v1/fines/unpaid` | List unpaid fines |
| `GET` | `/api/v1/members/{id}/fines` | Get member's fines summary |

---

## Database Constraints

The database enforces data integrity through various constraints:

### Borrow Transactions
| Constraint | Description |
|---|---|
| `ix_unique_active_borrow` | Prevents duplicate active borrowings (same member + book) |
| `ck_borrow_status` | Status must be 'borrowed', 'overdue', or 'returned' |
| `ck_borrow_fine_positive` | Fine amount must be >= 0 |
| `ck_borrow_overdue_days_positive` | Overdue days must be >= 0 |
| `ck_borrow_due_after_borrow` | Due date must be >= borrow date |
| `ck_borrow_return_after_borrow` | Return date must be >= borrow date |

### Books
| Constraint | Description |
|---|---|
| `ck_books_copies` | Available copies must be between 0 and total copies |
| `ck_books_total_copies_positive` | Total copies must be >= 0 |
| `books_isbn_key` | ISBN must be unique |

### Members
| Constraint | Description |
|---|---|
| `ck_member_status` | Status must be 'active' or 'inactive' |
| `members_membership_id_key` | Membership ID must be unique |
| `members_email_key` | Email must be unique |

---

## Business Rules

The application enforces the following business rules:

| Rule | Description |
|---|---|
| **Duplicate borrowing prevention** | A member cannot borrow the same book if they already have an active (borrowed/overdue) transaction for it |
| **Available copies check** | A book can only be borrowed if `available_copies > 0` |
| **Active member required** | Only members with `status = 'active'` can borrow books |
| **Maximum borrowings limit** | Members cannot exceed `MAX_ACTIVE_BORROWINGS` (default: 5) concurrent loans |
| **Outstanding fines block** | Members with unpaid fines cannot borrow new books |
| **Automatic overdue detection** | Transactions past `due_date` are marked as 'overdue' |
| **Fine calculation** | Fines are calculated as `overdue_days × FINE_PER_DAY`, capped at `MAX_FINE_AMOUNT` |

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

## gRPC-Web Service

The application also exposes gRPC endpoints for better performance and type safety.

### Proto Files

Located in `backend/protos/`:

| File | Description |
|---|---|
| `common.proto` | Common types (pagination, IDs, status) |
| `books.proto` | Book CRUD, PDF upload, AI enrichment |
| `members.proto` | Member CRUD, recommendations |
| `borrow.proto` | Borrow/return operations |
| `auth.proto` | Authentication |

### Generate gRPC Code

```bash
cd backend
python scripts/generate_grpc.py
```

### Test with grpcurl

```bash
# List available services
grpcurl -plaintext localhost:50051 list

# List books
grpcurl -plaintext -d '{"skip": 0, "limit": 10}' \
  localhost:50051 library.books.BookService/ListBooks
```

See [docs/grpc-service.md](docs/grpc-service.md) for full documentation.

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
- Email / SMS notifications for due-date reminders
- Mobile application (React Native)
- Advanced analytics dashboard (popular books, borrowing trends)
- Multi-branch support

---

## Performance Optimizations

The application implements several performance optimizations:

| Optimization | Description |
|---|---|
| **Batch enrichment** | List endpoints fetch related books and members in 2 queries instead of N+1 |
| **Set-based lookups** | Recommendation scoring uses sets for O(1) membership testing |
| **Database indexes** | Indexes on frequently queried columns (status, due_date, member_id, book_id) |
| **Partial unique index** | `ix_unique_active_borrow` only indexes active transactions |

