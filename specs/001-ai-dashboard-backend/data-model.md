# Data Model: Joyfull UI Hub Backend

**Feature Branch**: `001-ai-dashboard-backend`
**Date**: 2026-01-11
**Status**: Complete

## Overview

This document defines the database entities, relationships, and validation rules for the
Joyfull UI Hub Backend. All models use SQLAlchemy 2.0 async patterns per Constitution
Principle III.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │───────│   Subscription   │       │    Tool     │
│             │  1:1  │                  │       │             │
│  id (PK)    │       │  id (PK)         │       │  id (PK)    │
│  name       │       │  user_id (FK)    │       │  name       │
│  email      │       │  plan            │       │  description│
│  password   │       │  status          │       │  api_endpoint│
│  role       │       │  expires_at      │       │  created_at │
│  created_at │       │  created_at      │       │  updated_at │
└─────────────┘       └──────────────────┘       └─────────────┘
       │                                               │
       │ 1:N                                           │
       ▼                                               │
┌─────────────┐                                        │
│   APIKey    │                                        │
│             │                                        │
│  id (PK)    │                                        │
│  user_id(FK)│                                        │
│  key_hash   │                                        │
│  name       │                                        │
│  active     │                                        │
│  created_at │                                        │
│  last_used  │                                        │
└─────────────┘                                        │
       │                                               │
       │                                               │
       │               ┌──────────────────┐            │
       │               │    UsageLog      │            │
       │               │                  │            │
       │               │  id (PK)         │            │
       └───────────────│  user_id (FK)    │────────────┘
                       │  tool_id (FK)    │
                       │  timestamp       │
                       │  tokens_used     │
                       │  request_id      │
                       └──────────────────┘
```

---

## Entities

### 1. User

Represents a registered platform user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| name | VARCHAR(100) | NOT NULL | User's display name |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| role | ENUM('user', 'admin') | NOT NULL, DEFAULT 'user' | User's role for RBAC |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW(), ON UPDATE | Last modification time |

**Validation Rules**:
- `email`: Valid email format, case-insensitive uniqueness
- `name`: 1-100 characters, no leading/trailing whitespace
- `password`: Minimum 8 characters, mixed case, number, special character (validated before hashing)

**Indexes**:
- `ix_users_email` on `email` (unique)
- `ix_users_role` on `role` (for admin queries)

**Relationships**:
- One-to-one with `Subscription`
- One-to-many with `APIKey`
- One-to-many with `UsageLog`

---

### 2. Subscription

Represents a user's subscription plan.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK(users.id), UNIQUE, NOT NULL | Reference to user |
| plan | ENUM('free', 'pro', 'enterprise') | NOT NULL | Subscription tier |
| status | ENUM('active', 'cancelled', 'expired') | NOT NULL, DEFAULT 'active' | Subscription state |
| token_limit | INTEGER | NOT NULL | Tokens allowed per billing period |
| tokens_used | INTEGER | NOT NULL, DEFAULT 0 | Tokens consumed this period |
| period_start | TIMESTAMP | NOT NULL | Current billing period start |
| expires_at | TIMESTAMP | NULL | Subscription expiration (NULL = no expiry) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Subscription creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW(), ON UPDATE | Last modification time |

**Validation Rules**:
- `user_id`: Must reference existing user
- `token_limit`: Must be positive integer
- `tokens_used`: Must be non-negative, <= token_limit triggers rate limit

**State Transitions**:
```
                    ┌──────────┐
                    │  active  │◄───────────────┐
                    └────┬─────┘                │
                         │                      │
            ┌────────────┼────────────┐         │
            │            │            │         │
            ▼            ▼            ▼         │
      ┌──────────┐ ┌──────────┐ ┌──────────┐    │
      │cancelled │ │ expired  │ │ upgraded │────┘
      └──────────┘ └──────────┘ └──────────┘
```

**Indexes**:
- `ix_subscriptions_user_id` on `user_id` (unique)
- `ix_subscriptions_status` on `status`
- `ix_subscriptions_expires_at` on `expires_at` (for expiration job)

**Relationships**:
- Many-to-one with `User` (each user has at most one subscription)

---

### 3. Tool

Represents an AI tool available on the platform.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Tool display name |
| description | TEXT | NOT NULL | Tool description and usage info |
| api_endpoint | VARCHAR(500) | NOT NULL | External API URL for invocation |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether tool is available |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Tool creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW(), ON UPDATE | Last modification time |

**Validation Rules**:
- `name`: 1-100 characters, unique
- `api_endpoint`: Valid URL format, HTTPS required in production
- `description`: Non-empty, supports markdown

**Indexes**:
- `ix_tools_name` on `name` (unique)
- `ix_tools_is_active` on `is_active`

**Relationships**:
- One-to-many with `UsageLog`

---

### 4. UsageLog

Records each tool invocation for billing and analytics.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Reference to user |
| tool_id | UUID | FK(tools.id), NOT NULL, INDEX | Reference to tool |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEX | Invocation time |
| tokens_used | INTEGER | NOT NULL | Tokens consumed by this invocation |
| request_id | UUID | NOT NULL | Correlation ID for tracing |
| response_status | VARCHAR(20) | NOT NULL | success/error/timeout |
| duration_ms | INTEGER | NULL | Request duration in milliseconds |

**Validation Rules**:
- `tokens_used`: Must be non-negative
- `duration_ms`: Must be non-negative if present

**Indexes**:
- `ix_usage_logs_user_id` on `user_id`
- `ix_usage_logs_tool_id` on `tool_id`
- `ix_usage_logs_timestamp` on `timestamp`
- `ix_usage_logs_user_timestamp` on `(user_id, timestamp)` (composite for user history queries)

**Relationships**:
- Many-to-one with `User`
- Many-to-one with `Tool`

---

### 5. APIKey

Represents a programmatic access credential.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Reference to user |
| key_hash | VARCHAR(255) | NOT NULL, UNIQUE | SHA-256 hash of the key |
| key_prefix | VARCHAR(8) | NOT NULL | First 8 chars for identification |
| name | VARCHAR(100) | NOT NULL | User-provided key name |
| active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether key is active |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Key creation time |
| last_used_at | TIMESTAMP | NULL | Last successful authentication |
| expires_at | TIMESTAMP | NULL | Optional expiration time |

**Validation Rules**:
- `key_hash`: SHA-256 hash, key is shown once at creation then never stored in plain text
- `name`: 1-100 characters
- `key_prefix`: Derived from original key, used for display (e.g., "jfui_abc1...")

**Indexes**:
- `ix_api_keys_key_hash` on `key_hash` (unique)
- `ix_api_keys_user_id` on `user_id`
- `ix_api_keys_active` on `active`

**Relationships**:
- Many-to-one with `User`

---

### 6. RefreshToken (Supporting Entity)

Stores refresh tokens for JWT session management.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Reference to user |
| token_hash | VARCHAR(255) | NOT NULL, UNIQUE | SHA-256 hash of token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token is revoked |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation time |
| replaced_by | UUID | FK(refresh_tokens.id), NULL | Token that replaced this one |

**Validation Rules**:
- `token_hash`: SHA-256 hash, actual token shown once then not stored
- `expires_at`: Must be in the future at creation

**Indexes**:
- `ix_refresh_tokens_token_hash` on `token_hash` (unique)
- `ix_refresh_tokens_user_id` on `user_id`
- `ix_refresh_tokens_expires_at` on `expires_at` (for cleanup job)

**Relationships**:
- Many-to-one with `User`
- Self-referential for token rotation chain

---

## Enumerations

### UserRole
```python
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
```

### SubscriptionPlan
```python
class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
```

### SubscriptionStatus
```python
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
```

### UsageResponseStatus
```python
class UsageResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
```

---

## Plan Token Limits (Configuration)

Default values (configurable via admin):

| Plan | Token Limit / Month |
|------|---------------------|
| free | 1,000 |
| pro | 50,000 |
| enterprise | 500,000 |

---

## Migration Strategy

1. **Initial migration**: Create all tables with indexes
2. **Seed data migration**: Create default admin user (password set via env var)
3. **Plan configuration**: Seed default plan token limits

All migrations follow Constitution Development Workflow requirements:
- Include both `upgrade()` and `downgrade()` functions
- Committed alongside model changes
- Destructive changes require explicit approval
