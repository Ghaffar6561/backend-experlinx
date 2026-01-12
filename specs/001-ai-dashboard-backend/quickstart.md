# Quickstart: Joyfull UI Hub Backend

**Feature Branch**: `001-ai-dashboard-backend`
**Date**: 2026-01-11

This guide covers local development setup and running the Joyfull UI Hub Backend.

---

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for containerized setup)

---

## Option 1: Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd experlinx

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/joyfull_hub

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Email (for password reset)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@joyfullhub.com

# Optional: Admin seed user
ADMIN_EMAIL=admin@joyfullhub.com
ADMIN_PASSWORD=changeme123!
```

### 3. Setup Database

```bash
# Start PostgreSQL (if not running)
# On macOS with Homebrew:
brew services start postgresql

# Create database
createdb joyfull_hub

# Run migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`.

- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Alternative Docs: `http://localhost:8000/redoc` (ReDoc)

---

## Option 2: Docker Compose Setup

### 1. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 2. Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/joyfull_hub
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key}
      - APP_ENV=development
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=joyfull_hub
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_auth.py
```

### Test Database Setup

Tests use a separate database. Configure in `pytest.ini` or `conftest.py`:

```bash
# Create test database
createdb joyfull_hub_test
```

---

## API Quick Reference

### Authentication

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "SecurePass123!"}'

# Response includes access_token and refresh_token
```

### Using the Access Token

```bash
# Get current user profile
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"

# List available tools
curl -X GET http://localhost:8000/api/v1/tools \
  -H "Authorization: Bearer <access_token>"

# Invoke a tool
curl -X POST http://localhost:8000/api/v1/tools/<tool_id>/invoke \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello, AI!"}}'
```

### API Key Authentication

```bash
# Create an API key
curl -X POST http://localhost:8000/api/v1/users/me/api-keys \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Integration"}'

# Use API key (X-API-Key header)
curl -X GET http://localhost:8000/api/v1/tools \
  -H "X-API-Key: <api_key>"
```

---

## Health Checks

```bash
# Liveness probe
curl http://localhost:8000/health
# Response: {"status": "ok"}

# Readiness probe
curl http://localhost:8000/ready
# Response: {"status": "ready", "database": "connected"}
```

---

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Common Issues

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct.

### JWT Decode Error

```
jose.exceptions.JWTError: Signature verification failed
```

**Solution**: Ensure JWT_SECRET_KEY is consistent across restarts.

### CORS Error in Browser

**Solution**: Add your frontend URL to CORS_ORIGINS in `.env`.

---

## Project Structure

```
src/
├── api/v1/          # API route handlers
├── core/            # Configuration, security, dependencies
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
├── db/              # Database session management
└── main.py          # Application entry point

tests/
├── conftest.py      # Test fixtures
├── unit/            # Unit tests
├── integration/     # Integration tests
└── contract/        # Contract tests

alembic/
├── versions/        # Migration files
└── env.py           # Alembic configuration
```

---

## Next Steps

1. Review the [API Contract](contracts/openapi.yaml) for full endpoint documentation
2. Check [Data Model](data-model.md) for entity relationships
3. See [Research](research.md) for technical decisions and rationale
