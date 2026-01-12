# Tasks: Joyfull UI Hub Backend

**Input**: Design documents from `/specs/001-ai-dashboard-backend/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the spec. Test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the plan.md structure

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize FastAPI project and configure core infrastructure

- [x] T001 Create project directory structure per plan.md in src/
- [x] T002 Create requirements.txt with FastAPI, SQLAlchemy, asyncpg, python-jose, passlib, pydantic dependencies
- [x] T003 [P] Create requirements-dev.txt with pytest, pytest-asyncio, httpx, ruff dependencies
- [x] T004 [P] Create .env.example with DATABASE_URL, JWT_SECRET_KEY, and other config variables
- [x] T005 [P] Create pytest.ini with asyncio_mode=auto configuration
- [x] T006 Implement environment configuration in src/core/config.py using pydantic-settings
- [x] T007 Implement database session factory in src/db/session.py with async SQLAlchemy engine
- [x] T008 [P] Create SQLAlchemy base model class in src/db/base.py with UUID primary key mixin
- [x] T009 Initialize Alembic with async support in alembic/ directory
- [x] T010 [P] Create common Pydantic schemas (ApiResponse, ApiError, PaginationMeta) in src/schemas/common.py
- [x] T011 Create FastAPI application entry point in src/main.py with lifespan handler

**Checkpoint**: Project structure ready, FastAPI app starts, database connection configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Create User SQLAlchemy model in src/models/user.py with all fields from data-model.md
- [x] T013 [P] Create UserRole enum in src/models/user.py
- [x] T014 Create initial Alembic migration for users table in alembic/versions/
- [x] T015 Run migration to create users table
- [x] T016 Implement password hashing utilities (hash, verify) in src/core/security.py using passlib[bcrypt]
- [x] T017 [P] Implement JWT token creation (access, refresh) in src/core/security.py using python-jose
- [x] T018 [P] Implement JWT token validation in src/core/security.py
- [x] T019 Create get_current_user dependency in src/core/dependencies.py
- [x] T020 Create require_role dependency factory in src/core/dependencies.py for RBAC
- [x] T021 [P] Create RefreshToken SQLAlchemy model in src/models/refresh_token.py
- [x] T022 Create Alembic migration for refresh_tokens table in alembic/versions/
- [x] T023 [P] Create auth Pydantic schemas (UserRegistration, LoginRequest, TokenPair) in src/schemas/auth.py
- [x] T024 [P] Create user Pydantic schemas (UserProfile, UserUpdate) in src/schemas/user.py
- [x] T025 Implement exception handlers for validation and auth errors in src/main.py
- [x] T026 [P] Implement health check endpoints (/health, /ready) in src/api/v1/health.py
- [x] T027 Configure CORS middleware in src/main.py
- [x] T028 Configure structured JSON logging in src/core/config.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1)

**Goal**: Users can register, login, refresh tokens, and reset passwords

**Independent Test**: Register a new user, login, verify tokens work on protected endpoints

### Implementation for User Story 1

- [x] T029 [US1] Implement AuthService.register() in src/services/auth.py
- [x] T030 [US1] Implement AuthService.login() in src/services/auth.py
- [x] T031 [US1] Implement AuthService.refresh_token() with rotation in src/services/auth.py
- [x] T032 [US1] Implement AuthService.logout() (revoke refresh token) in src/services/auth.py
- [x] T033 [US1] Implement AuthService.request_password_reset() in src/services/auth.py
- [x] T034 [US1] Implement AuthService.reset_password() in src/services/auth.py
- [x] T035 [US1] Create POST /auth/register endpoint in src/api/v1/auth.py
- [x] T036 [US1] Create POST /auth/login endpoint in src/api/v1/auth.py
- [x] T037 [US1] Create POST /auth/refresh endpoint in src/api/v1/auth.py
- [x] T038 [US1] Create POST /auth/logout endpoint in src/api/v1/auth.py
- [x] T039 [US1] Create POST /auth/password-reset endpoint in src/api/v1/auth.py
- [x] T040 [US1] Create POST /auth/password-reset/{token} endpoint in src/api/v1/auth.py
- [x] T041 [US1] Register auth router in src/main.py under /api/v1/auth prefix
- [x] T042 [US1] Add email validation with duplicate check in AuthService.register()
- [x] T043 [US1] Add password complexity validation in AuthService.register()

**Checkpoint**: User Story 1 complete - users can register, login, refresh tokens, reset passwords

---

## Phase 4: User Story 2 - Profile Management (Priority: P2)

**Goal**: Users can view/update profile and manage API keys

**Independent Test**: Login, view profile, update name, create API key, revoke API key

### Implementation for User Story 2

- [x] T044 [US2] Create APIKey SQLAlchemy model in src/models/api_key.py
- [x] T045 [US2] Create Alembic migration for api_keys table in alembic/versions/
- [x] T046 [US2] Create API key Pydantic schemas (ApiKeyInfo, ApiKeyCreated) in src/schemas/user.py
- [x] T047 [US2] Implement UserService.get_profile() in src/services/user.py
- [x] T048 [US2] Implement UserService.update_profile() in src/services/user.py
- [x] T049 [US2] Implement UserService.create_api_key() in src/services/user.py
- [x] T050 [US2] Implement UserService.list_api_keys() in src/services/user.py
- [x] T051 [US2] Implement UserService.revoke_api_key() in src/services/user.py
- [x] T052 [US2] Create GET /users/me endpoint in src/api/v1/users.py
- [x] T053 [US2] Create PATCH /users/me endpoint in src/api/v1/users.py
- [x] T054 [US2] Create GET /users/me/api-keys endpoint in src/api/v1/users.py
- [x] T055 [US2] Create POST /users/me/api-keys endpoint in src/api/v1/users.py
- [x] T056 [US2] Create DELETE /users/me/api-keys/{key_id} endpoint in src/api/v1/users.py
- [x] T057 [US2] Register users router in src/main.py under /api/v1/users prefix
- [x] T058 [US2] Implement API key authentication as alternative to JWT in src/core/dependencies.py

**Checkpoint**: User Story 2 complete - users can manage profile and API keys

---

## Phase 5: User Story 3 - AI Tool Discovery and Access (Priority: P3)

**Goal**: Users can list tools, view details, and invoke tools (with subscription check)

**Independent Test**: List tools, get tool details, invoke a tool with valid subscription

### Implementation for User Story 3

- [x] T059 [US3] Create Tool SQLAlchemy model in src/models/tool.py
- [x] T060 [US3] Create Alembic migration for tools table in alembic/versions/
- [x] T061 [US3] Create tool Pydantic schemas (ToolSummary, ToolDetail, ToolInvocationResult) in src/schemas/tool.py
- [x] T062 [US3] Implement ToolService.list_tools() with pagination in src/services/tool.py
- [x] T063 [US3] Implement ToolService.get_tool() in src/services/tool.py
- [x] T064 [US3] Implement ToolService.invoke_tool() with httpx async client in src/services/tool.py
- [x] T065 [US3] Add subscription check in tool invocation (deny if no active subscription)
- [x] T066 [US3] Add circuit breaker pattern for external tool calls in src/services/tool.py
- [x] T067 [US3] Create GET /tools endpoint in src/api/v1/tools.py
- [x] T068 [US3] Create GET /tools/{tool_id} endpoint in src/api/v1/tools.py
- [x] T069 [US3] Create POST /tools/{tool_id}/invoke endpoint in src/api/v1/tools.py
- [x] T070 [US3] Register tools router in src/main.py under /api/v1/tools prefix

**Checkpoint**: User Story 3 complete - users can discover and invoke AI tools

---

## Phase 6: User Story 4 - Usage Tracking and Dashboard (Priority: P4)

**Goal**: Users can view usage history and aggregated summaries

**Independent Test**: Invoke a tool, view usage history, view usage summary with correct data

### Implementation for User Story 4

- [x] T071 [US4] Create UsageLog SQLAlchemy model in src/models/usage_log.py
- [x] T072 [US4] Create UsageResponseStatus enum in src/models/usage_log.py
- [x] T073 [US4] Create Alembic migration for usage_logs table in alembic/versions/
- [x] T074 [US4] Create usage Pydantic schemas (UsageLogEntry, UsageSummary) in src/schemas/usage.py
- [x] T075 [US4] Implement UsageService.log_invocation() in src/services/usage.py
- [x] T076 [US4] Implement UsageService.get_history() with date filtering in src/services/usage.py
- [x] T077 [US4] Implement UsageService.get_summary() with aggregation in src/services/usage.py
- [x] T078 [US4] Integrate usage logging into ToolService.invoke_tool()
- [x] T079 [US4] Create GET /usage endpoint in src/api/v1/usage.py
- [x] T080 [US4] Create GET /usage/summary endpoint in src/api/v1/usage.py
- [x] T081 [US4] Register usage router in src/main.py under /api/v1/usage prefix

**Checkpoint**: User Story 4 complete - users can track their tool usage

---

## Phase 7: User Story 5 - Subscription Management (Priority: P5)

**Goal**: Users can view plans, subscribe, upgrade, downgrade, and cancel

**Independent Test**: View plans, subscribe to free plan, upgrade to pro, cancel subscription

### Implementation for User Story 5

- [x] T082 [US5] Create Subscription SQLAlchemy model in src/models/subscription.py
- [x] T083 [US5] Create SubscriptionPlan and SubscriptionStatus enums in src/models/subscription.py
- [x] T084 [US5] Create Alembic migration for subscriptions table in alembic/versions/
- [x] T085 [US5] Create subscription Pydantic schemas (SubscriptionPlan, SubscriptionDetail) in src/schemas/subscription.py
- [x] T086 [US5] Implement SubscriptionService.list_plans() in src/services/subscription.py
- [x] T087 [US5] Implement SubscriptionService.get_current() in src/services/subscription.py
- [x] T088 [US5] Implement SubscriptionService.subscribe() in src/services/subscription.py
- [x] T089 [US5] Implement SubscriptionService.cancel() in src/services/subscription.py
- [x] T090 [US5] Implement token limit enforcement in SubscriptionService
- [x] T091 [US5] Create GET /subscriptions/plans endpoint in src/api/v1/subscriptions.py
- [x] T092 [US5] Create GET /subscriptions/current endpoint in src/api/v1/subscriptions.py
- [x] T093 [US5] Create POST /subscriptions/subscribe endpoint in src/api/v1/subscriptions.py
- [x] T094 [US5] Create POST /subscriptions/cancel endpoint in src/api/v1/subscriptions.py
- [x] T095 [US5] Register subscriptions router in src/main.py under /api/v1/subscriptions prefix
- [x] T096 [US5] Update tool invocation to check token limits before allowing invocation

**Checkpoint**: User Story 5 complete - users can manage subscriptions with token limits

---

## Phase 8: User Story 6 - Admin Tool and User Management (Priority: P6)

**Goal**: Admins can manage tools, view users, and see platform-wide stats

**Independent Test**: Login as admin, create tool, update tool, view all users, view platform stats

### Implementation for User Story 6

- [x] T097 [US6] Create admin Pydantic schemas (AdminUserView, PlatformUsageStats, ToolCreate, ToolUpdate) in src/schemas/admin.py
- [x] T098 [US6] Implement AdminService.list_users() with pagination in src/services/admin.py
- [x] T099 [US6] Implement AdminService.create_tool() in src/services/admin.py
- [x] T100 [US6] Implement AdminService.update_tool() in src/services/admin.py
- [x] T101 [US6] Implement AdminService.delete_tool() in src/services/admin.py
- [x] T102 [US6] Implement AdminService.get_platform_stats() in src/services/admin.py
- [x] T103 [US6] Create GET /admin/users endpoint with admin role check in src/api/v1/admin.py
- [x] T104 [US6] Create POST /admin/tools endpoint with admin role check in src/api/v1/admin.py
- [x] T105 [US6] Create PATCH /admin/tools/{tool_id} endpoint with admin role check in src/api/v1/admin.py
- [x] T106 [US6] Create DELETE /admin/tools/{tool_id} endpoint with admin role check in src/api/v1/admin.py
- [x] T107 [US6] Create GET /admin/usage/stats endpoint with admin role check in src/api/v1/admin.py
- [x] T108 [US6] Register admin router in src/main.py under /api/v1/admin prefix

**Checkpoint**: User Story 6 complete - admins can manage platform

---

## Phase 9: Polish & Production Readiness

**Purpose**: Finalize for deployment with Docker and documentation

- [x] T109 Create Dockerfile with multi-stage build in Dockerfile
- [x] T110 [P] Create docker-compose.yml with api and db services
- [x] T111 [P] Create .dockerignore file
- [x] T112 Add request ID middleware for correlation in src/main.py
- [x] T113 [P] Create seed data migration for default admin user in alembic/versions/
- [x] T114 [P] Create seed data migration for default plan token limits in alembic/versions/
- [x] T115 Validate OpenAPI spec matches implementation using FastAPI's generated schema
- [x] T116 [P] Create __init__.py files in all src/ subdirectories
- [x] T117 [P] Create tests/conftest.py with async test fixtures

**Checkpoint**: Production-ready deployment artifacts complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Auth): No dependencies on other stories
  - US2 (Profile): No dependencies on other stories
  - US3 (Tools): Depends on subscription model for access check (can stub initially)
  - US4 (Usage): Depends on US3 (logs tool invocations)
  - US5 (Subscriptions): No dependencies on other stories
  - US6 (Admin): Depends on Tool and User models (from US1 foundation)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundation) ──┬──► US1 (Auth) ──────────────────────────────┐
                                           ├──► US2 (Profile) ───────────────────────────┤
                                           ├──► US3 (Tools) ──► US4 (Usage) ─────────────┤
                                           ├──► US5 (Subscriptions) ◄── US3 (access) ────┤
                                           └──► US6 (Admin) ─────────────────────────────┴──► Phase 9 (Polish)
```

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before marking checkpoint

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1, US2, US5, US6 can start in parallel
- US3 can start but needs subscription stub for access check
- US4 depends on US3 completion

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch parallelizable foundational tasks together:
Task: "Create UserRole enum in src/models/user.py" (T013)
Task: "Implement JWT token creation in src/core/security.py" (T017)
Task: "Implement JWT token validation in src/core/security.py" (T018)
Task: "Create RefreshToken model in src/models/refresh_token.py" (T021)
Task: "Create auth Pydantic schemas in src/schemas/auth.py" (T023)
Task: "Create user Pydantic schemas in src/schemas/user.py" (T024)
Task: "Implement health check endpoints in src/api/v1/health.py" (T026)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test registration, login, token refresh
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Test independently → **MVP Ready!**
3. Add US2 (Profile) → Test independently
4. Add US5 (Subscriptions) → Test independently
5. Add US3 (Tools) → Test independently
6. Add US4 (Usage) → Test independently
7. Add US6 (Admin) → Test independently
8. Polish phase → Production ready

---

## Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Phase 1: Setup | 11 | 5 |
| Phase 2: Foundational | 17 | 10 |
| Phase 3: US1 (Auth) | 15 | 0 |
| Phase 4: US2 (Profile) | 15 | 0 |
| Phase 5: US3 (Tools) | 12 | 0 |
| Phase 6: US4 (Usage) | 11 | 0 |
| Phase 7: US5 (Subscriptions) | 15 | 0 |
| Phase 8: US6 (Admin) | 12 | 0 |
| Phase 9: Polish | 9 | 5 |
| **Total** | **117** | **20** |

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1: Authentication) = 43 tasks
