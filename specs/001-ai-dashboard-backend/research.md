# Research: Joyfull UI Hub Backend

**Feature Branch**: `001-ai-dashboard-backend`
**Date**: 2026-01-11
**Status**: Complete

## Executive Summary

This document captures technical research and decisions for the Joyfull UI Hub Backend.
All decisions align with the Experlinx Constitution v1.0.0 requirements.

---

## 1. Framework & Language

### Decision: Python 3.11+ with FastAPI

**Rationale**:
- Constitution mandates FastAPI as the framework (Principle III)
- Python 3.11+ provides significant performance improvements and better error messages
- Native async/await support aligns with async-first database access requirement

**Alternatives Considered**:
- Python 3.10: Rejected due to missing performance optimizations in 3.11
- Python 3.12: Acceptable but 3.11 has broader library compatibility

---

## 2. Database & ORM

### Decision: PostgreSQL 15+ with SQLAlchemy 2.0 Async + asyncpg

**Rationale**:
- Constitution mandates PostgreSQL 15+ and SQLAlchemy 2.0 async (Principle III)
- asyncpg provides the fastest async PostgreSQL driver for Python
- SQLAlchemy 2.0 style uses native Python async/await patterns

**Configuration**:
- Connection pooling via SQLAlchemy's async pool (pool_size=10, max_overflow=20)
- Statement caching enabled for prepared statement performance
- Connection recycling at 3600 seconds to prevent stale connections

**Alternatives Considered**:
- SQLModel: Rejected; less mature, limited advanced query support
- Tortoise ORM: Rejected; less ecosystem support than SQLAlchemy
- Raw asyncpg: Rejected; Constitution requires ORM for consistency

---

## 3. Authentication

### Decision: JWT with python-jose, bcrypt password hashing

**Rationale**:
- Constitution mandates JWT authentication (Principle IV)
- python-jose is well-maintained and supports RS256/HS256
- bcrypt via passlib provides proven password hashing with configurable cost

**Token Configuration**:
- Access token: HS256, 30-minute expiry (within 15-60 minute Constitution requirement)
- Refresh token: HS256, 7-day expiry, stored in database, rotated on use
- Claims: user_id, role, exp, iat, jti (for refresh token revocation)

**Alternatives Considered**:
- PyJWT: Acceptable alternative, python-jose chosen for broader algorithm support
- Argon2: Acceptable for hashing, bcrypt chosen for wider deployment experience

---

## 4. Authorization

### Decision: FastAPI Dependencies with Role-Based Decorators

**Rationale**:
- Constitution mandates RBAC via FastAPI dependencies (Principle V)
- Declarative approach makes authorization visible in endpoint signatures
- Centralized role checking enables consistent audit logging

**Implementation Pattern**:
```python
async def require_role(roles: list[str]) -> Callable:
    async def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency

# Usage: @router.get("/admin/users", dependencies=[Depends(require_role(["admin"]))])
```

**Alternatives Considered**:
- Casbin: Rejected; adds complexity for simple two-role system
- Custom middleware: Rejected; dependencies provide better per-endpoint control

---

## 5. API Response Format

### Decision: Consistent JSON Envelope Structure

**Rationale**:
- Constitution mandates `data`, `error`, `meta` envelope (Principle II)
- Enables consistent client-side error handling
- Supports pagination metadata without breaking response structure

**Response Schema**:
```json
{
  "data": { ... } | null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [...]
  } | null,
  "meta": {
    "pagination": { "offset": 0, "limit": 20, "total": 100 },
    "request_id": "uuid"
  }
}
```

**Alternatives Considered**:
- Raw data responses: Rejected; Constitution requires envelope
- JSON:API format: Rejected; more complex than needed, envelope pattern sufficient

---

## 6. Database Migrations

### Decision: Alembic with Auto-generation

**Rationale**:
- Constitution mandates Alembic for migrations (Principle III)
- Auto-generation reduces human error in migration scripts
- Reversible migrations required by Constitution (Development Workflow)

**Configuration**:
- Migrations directory: `alembic/versions/`
- Naming convention: `{revision}_{slug}.py`
- All migrations include both `upgrade()` and `downgrade()` functions

**Alternatives Considered**:
- Manual migrations only: Rejected; auto-generation catches model drift
- Django-style migrations: Not applicable (FastAPI stack)

---

## 7. Project Structure

### Decision: Single Backend Project with Modular Layout

**Rationale**:
- This is a backend-only API service (no frontend in scope)
- Modular structure separates concerns while keeping deployment simple
- Aligns with Constitution's cloud-native stateless service pattern (Principle VI)

**Selected Structure**:
```
src/
├── api/
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       ├── tools.py
│       ├── subscriptions.py
│       ├── usage.py
│       └── admin.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── dependencies.py
├── models/
│   ├── user.py
│   ├── subscription.py
│   ├── tool.py
│   ├── usage_log.py
│   └── api_key.py
├── schemas/
│   ├── user.py
│   ├── subscription.py
│   ├── tool.py
│   ├── usage.py
│   └── common.py
├── services/
│   ├── auth.py
│   ├── user.py
│   ├── tool.py
│   ├── subscription.py
│   └── usage.py
├── db/
│   ├── session.py
│   └── base.py
└── main.py

tests/
├── conftest.py
├── unit/
├── integration/
└── contract/

alembic/
├── env.py
├── script.py.mako
└── versions/
```

**Alternatives Considered**:
- Monolithic single file: Rejected; doesn't scale with 6 modules
- Microservices: Rejected; premature for initial deployment, adds operational complexity

---

## 8. External Tool Invocation

### Decision: Async HTTP Client (httpx) with Circuit Breaker

**Rationale**:
- External AI tools are accessed via HTTP (spec assumption)
- httpx provides async HTTP client compatible with FastAPI
- Circuit breaker prevents cascade failures when external services are down

**Configuration**:
- Timeout: 30 seconds per request (configurable per tool)
- Retry: 3 attempts with exponential backoff for transient failures
- Circuit breaker: Opens after 5 consecutive failures, half-open after 60 seconds

**Alternatives Considered**:
- aiohttp: Acceptable, httpx chosen for simpler API and better typing
- Synchronous requests: Rejected; Constitution mandates async (Principle III)

---

## 9. Logging & Observability

### Decision: Structured JSON Logging with Correlation IDs

**Rationale**:
- Constitution mandates structured JSON logging (Principle VI)
- Correlation IDs enable distributed tracing across requests
- JSON format enables log aggregation in cloud environments

**Implementation**:
- Python `logging` with `python-json-logger`
- Middleware injects correlation ID from `X-Request-ID` header or generates UUID
- All log entries include: timestamp, level, correlation_id, message, extra context

**Alternatives Considered**:
- Plain text logging: Rejected; Constitution requires structured JSON
- OpenTelemetry: Future enhancement; structured logging is Phase 1 priority

---

## 10. Health Checks

### Decision: `/health` and `/ready` Endpoints

**Rationale**:
- Constitution mandates health check endpoints (Principle VI)
- Kubernetes/container orchestrators require these for lifecycle management
- Separating liveness from readiness enables graceful degradation

**Implementation**:
- `/health`: Returns 200 if process is running (liveness)
- `/ready`: Returns 200 if database connection is healthy (readiness)
- Both return JSON with status and optional diagnostics

**Alternatives Considered**:
- Single `/healthz` endpoint: Rejected; separate endpoints provide finer control

---

## 11. Containerization

### Decision: Docker Multi-Stage Build

**Rationale**:
- Constitution mandates Docker with multi-stage builds (Principle VI)
- Multi-stage reduces final image size by excluding build dependencies
- Enables consistent builds across development and production

**Dockerfile Strategy**:
1. Stage 1: Build stage with full Python + dev dependencies
2. Stage 2: Runtime stage with slim Python image + production dependencies only
3. Non-root user for security
4. Health check instruction for Docker native health monitoring

**Alternatives Considered**:
- Single-stage build: Rejected; results in larger images
- Distroless: Future consideration; slim Python images are sufficient initially

---

## 12. Testing Strategy

### Decision: pytest + pytest-asyncio + httpx TestClient

**Rationale**:
- Constitution mandates pytest with pytest-asyncio (Technology Stack)
- httpx AsyncClient provides async test client for FastAPI
- Factory pattern for fixtures enables isolated test data

**Test Categories**:
- **Unit tests**: Business logic, utilities (no database)
- **Integration tests**: API endpoints with test database
- **Contract tests**: External API consumer expectations

**Configuration**:
- Separate test database (PostgreSQL container or SQLite for fast unit tests)
- Fixtures use factory-boy or manual factories
- Coverage target: >80% for critical paths (Constitution requirement)

**Alternatives Considered**:
- unittest: Rejected; pytest is more expressive and has better async support
- SQLite for integration tests: Acceptable for speed, PostgreSQL preferred for fidelity

---

## Unresolved Items

None. All technical decisions align with Constitution requirements and spec assumptions.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [python-jose JWT Library](https://python-jose.readthedocs.io/)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/)
- [Experlinx Constitution v1.0.0](.specify/memory/constitution.md)
