# Implementation Plan: Joyfull UI Hub Backend

**Branch**: `001-ai-dashboard-backend` | **Date**: 2026-01-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-dashboard-backend/spec.md`

## Summary

Build a production-ready backend API for a multi-tool AI dashboard platform. The system provides
user authentication (JWT), profile management with API keys, AI tool discovery and invocation,
usage tracking, subscription management (free/pro/enterprise tiers), and admin capabilities.
Built on FastAPI + PostgreSQL with async database access per Constitution requirements.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0, python-jose, passlib[bcrypt]
**Storage**: PostgreSQL 15+ with asyncpg driver
**Testing**: pytest + pytest-asyncio + httpx
**Target Platform**: Linux server (Docker container)
**Project Type**: Single backend API service
**Performance Goals**: 1,000 concurrent users, <500ms auth requests, <1s dashboard queries
**Constraints**: <200ms p95 for auth endpoints, stateless for horizontal scaling
**Scale/Scope**: Multi-tenant SaaS, 6 modules, 28 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Production-Ready Code | No placeholders, proper validation, transactions | ✅ PASS |
| II. RESTful API Standards | Versioned URIs, standard methods, JSON envelope | ✅ PASS |
| III. FastAPI + PostgreSQL Stack | FastAPI, SQLAlchemy 2.0 async, Alembic | ✅ PASS |
| IV. JWT Authentication | Short-lived tokens, refresh rotation, bcrypt | ✅ PASS |
| V. Role-Based Access Control | Explicit roles, FastAPI dependencies | ✅ PASS |
| VI. Cloud-Native Architecture | Stateless, env config, health checks, Docker | ✅ PASS |

**Gate Status**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-dashboard-backend/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Development setup guide
├── contracts/
│   └── openapi.yaml     # API contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── auth.py           # Authentication endpoints
│       ├── users.py          # User profile endpoints
│       ├── tools.py          # Tool discovery & invocation
│       ├── subscriptions.py  # Subscription management
│       ├── usage.py          # Usage tracking endpoints
│       └── admin.py          # Admin endpoints
├── core/
│   ├── __init__.py
│   ├── config.py             # Environment configuration
│   ├── security.py           # JWT, password hashing
│   └── dependencies.py       # FastAPI dependencies (auth, RBAC)
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── subscription.py
│   ├── tool.py
│   ├── usage_log.py
│   ├── api_key.py
│   └── refresh_token.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── auth.py
│   ├── subscription.py
│   ├── tool.py
│   ├── usage.py
│   └── common.py             # API envelope, pagination
├── services/
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── tool.py
│   ├── subscription.py
│   └── usage.py
├── db/
│   ├── __init__.py
│   ├── session.py            # Async session factory
│   └── base.py               # Base model class
└── main.py                   # Application entry point

tests/
├── conftest.py               # Shared fixtures
├── unit/
│   ├── test_security.py
│   ├── test_services.py
│   └── ...
├── integration/
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_tools.py
│   └── ...
└── contract/
    └── test_api_contract.py

alembic/
├── env.py
├── script.py.mako
└── versions/
    └── (migration files)

# Root files
requirements.txt
requirements-dev.txt
Dockerfile
docker-compose.yml
.env.example
pytest.ini
```

**Structure Decision**: Single backend project selected. No frontend (API-only service).
Modular layout separates API routes, business logic (services), data models, and schemas
per Constitution best practices.

## Implementation Phases

### Phase 1 - Core (Foundation)

Setup project infrastructure and authentication:

1. Initialize FastAPI project with folder structure
2. Configure PostgreSQL + SQLAlchemy 2.0 async
3. Setup Alembic migrations
4. Implement User model and initial migration
5. Implement JWT authentication (login, register, refresh)
6. Add password hashing with bcrypt
7. Create base API envelope and error handling

**Deliverables**: Working auth endpoints, User table, JWT token flow

### Phase 2 - Business Logic

Implement core business entities and services:

1. Subscription model and service (free/pro/enterprise)
2. Tool model and registry service
3. UsageLog model and tracking service
4. APIKey model and management
5. Token limit enforcement per subscription
6. RefreshToken model with rotation

**Deliverables**: All models, migrations, business services

### Phase 3 - API Endpoints

Build out all REST endpoints:

1. User profile endpoints (GET/PATCH /users/me)
2. API key management endpoints
3. Tool listing and details endpoints
4. Tool invocation endpoint with subscription check
5. Usage history and summary endpoints
6. Subscription management endpoints
7. Admin endpoints (users, tools, stats)

**Deliverables**: All API endpoints per OpenAPI contract

### Phase 4 - Production Readiness

Finalize for deployment:

1. Dockerfile with multi-stage build
2. docker-compose.yml for local development
3. Environment configuration (.env.example)
4. Health check endpoints (/health, /ready)
5. Structured JSON logging
6. CORS configuration
7. OpenAPI documentation validation
8. Integration tests for all endpoints

**Deliverables**: Deployable container, complete test suite

## Complexity Tracking

> No Constitution violations to justify. All design decisions align with principles.

| Decision | Rationale | Simpler Alternative Considered |
|----------|-----------|-------------------------------|
| SQLAlchemy over raw SQL | ORM required by Constitution Principle III | Raw asyncpg rejected |
| httpx for external calls | Async HTTP client for tool invocation | requests rejected (sync) |
| RefreshToken table | Enables token rotation per Constitution IV | Stateless refresh rejected |

## Dependencies

| Artifact | Required For |
|----------|--------------|
| research.md | Technical decisions reference |
| data-model.md | Entity implementations |
| contracts/openapi.yaml | API endpoint implementations |
| quickstart.md | Developer onboarding |

## Next Steps

Run `/sp.tasks` to generate the detailed implementation task list based on this plan.

---

## References

- [Feature Specification](spec.md)
- [Technical Research](research.md)
- [Data Model](data-model.md)
- [API Contract](contracts/openapi.yaml)
- [Quickstart Guide](quickstart.md)
- [Constitution](.specify/memory/constitution.md)
