---
id: 001
title: Establish Backend SaaS Constitution
stage: constitution
date: 2026-01-11
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["constitution", "backend", "fastapi", "postgresql", "saas", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document, no tests)
---

## Prompt

You are an expert backend architect and security engineer.

You must always:
- Generate production-ready code
- Follow RESTful API standards
- Use FastAPI + PostgreSQL
- Use async database access
- Use JWT authentication
- Never generate toy or demo code
- Always include migrations, models, and validation
- Enforce role-based access control

You must optimize for:
- Scalability
- Security
- Cloud deployment
- Clear API contracts

You must treat this as a real SaaS product.

## Response snapshot

Created the Experlinx Constitution v1.0.0 with 6 core principles:

1. **Production-Ready Code** - No placeholders, proper validation, transactions, externalized secrets
2. **RESTful API Standards** - Standard HTTP methods, versioned URIs, consistent response envelopes
3. **FastAPI + PostgreSQL Stack** - Fixed tech stack with async-only database access via SQLAlchemy 2.0
4. **JWT Authentication** - Short-lived access tokens, refresh token rotation, proper hashing
5. **Role-Based Access Control** - Explicit roles, declarative permissions, server-side enforcement
6. **Cloud-Native & Scalable Architecture** - Stateless services, 12-factor app, health checks, structured logging

Additional sections added:
- Technology Stack & Standards (required dependencies table, code quality, security standards)
- Development Workflow (migration discipline, model/validation separation, testing requirements)
- Governance (amendment process, versioning policy, compliance review)

## Outcome

- ✅ Impact: Established foundational governance for Experlinx backend development
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created/replaced)
- 🔁 Next prompts: /sp.specify to create first feature spec following these principles
- 🧠 Reflection: Constitution covers all user requirements; no placeholders remain

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding API rate limiting principle if needed
