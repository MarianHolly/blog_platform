<!--
SYNC IMPACT REPORT
==================
Version change: N/A (placeholder template) → 1.0.0 (initial adoption)

Modified principles: none (first fill — all principles newly authored)

Added sections:
  - Core Principles (5 principles: API-First, Role-Based Security, Test-First,
    Content Integrity, Simplicity & Django Conventions)
  - Technology Stack & Constraints
  - Development Workflow
  - Governance

Removed sections: none

Templates reviewed for consistency:
  - .specify/templates/plan-template.md      ✅ aligned (Constitution Check gate present)
  - .specify/templates/spec-template.md      ✅ aligned (FR/SC structure consistent)
  - .specify/templates/tasks-template.md     ✅ aligned (TDD task ordering matches Principle III)
  - .specify/templates/checklist-template.md ✅ no conflicts observed

Follow-up TODOs: none — all placeholders resolved
-->

# Blog Platform Constitution

## Core Principles

### I. API-First Architecture

The backend and frontend are strictly decoupled. All data access and business logic
MUST be exposed through versioned REST API endpoints (`/api/v1/`). The frontend
MUST NOT bypass the API to access the database directly. New features MUST be
implemented API-first: define the endpoint contract before writing UI code.
API responses MUST remain stable within a major version; breaking changes require
a version bump.

**Rationale**: Enables independent deployment of backend and frontend, supports
multiple clients (web, mobile, CLI), and ensures all business rules are enforced
in one place.

### II. Role-Based Security

Every action MUST be gated by the user's role (reader / writer / admin).
Permissions MUST be enforced at both the view and serializer level — never rely on
the frontend to hide restricted actions. Content visibility rules MUST be respected
throughout:

- Public articles: accessible to all
- Subscriber-only articles: accessible only to authenticated, subscribed readers
- Drafts: accessible only to the owning writer and admins

New views MUST explicitly declare their permission class; implicit defaults are
not acceptable.

**Rationale**: Prevents privilege escalation. A single missing permission check
can expose private content or allow unauthorized mutations.

### III. Test-First (NON-NEGOTIABLE)

TDD is mandatory. Tests MUST be written before implementation. The Red-Green-Refactor
cycle is strictly enforced:

1. Write a failing test that describes the desired behavior.
2. Get approval or review of the test.
3. Implement the minimum code to make the test pass.
4. Refactor without breaking the test.

Every Django app MUST have tests covering its models, views, and serializers.
Integration tests MUST cover the full request/response cycle for all new endpoints.

**Rationale**: The project has had regressions from untested code paths. Test
coverage is the primary quality gate.

### IV. Content Integrity

All user-generated content MUST be sanitized before storage or rendering to prevent
XSS attacks. The `bleach` library is the designated sanitizer — no alternatives
without an explicit amendment. Articles MUST follow the evaluation workflow:

```
draft → pending_review → approved (published) | rejected
```

Admin-only operations (approve/reject) MUST be protected by the admin role check.
CKEditor5 output MUST be sanitized server-side even if the editor applies
client-side sanitization.

**Rationale**: Content sanitization bypasses are among the most common vulnerability
classes in CMS platforms. Defense-in-depth is non-negotiable.

### V. Simplicity & Django Conventions

Follow Django and DRF conventions. Avoid over-engineering. YAGNI: do not build for
hypothetical future requirements. Three similar lines beat a premature abstraction.
Specific rules:

- Use Django's ORM directly; no additional repository layer unless justified.
- Prefer class-based views via DRF generics over custom view logic.
- Add database indexes only on fields used in filters, ordering, or joins.
- Apply Redis caching only to endpoints with demonstrated latency issues.

Complexity MUST be justified in the implementation plan's Complexity Tracking table.

**Rationale**: The codebase is maintained by a small team. Unnecessary abstractions
increase cognitive load and maintenance cost without delivering user value.

## Technology Stack & Constraints

**Backend**: Python 3.x · Django 5.2 · Django REST Framework · PostgreSQL ·
Redis (caching) · Cloudinary (media storage) · CKEditor5 (rich text editing) ·
bleach (content sanitization) · djangorestframework-simplejwt (JWT auth) ·
WhiteNoise (static files)

**Frontend**: Astro (SSR mode) · TypeScript · Tailwind CSS

**Testing**: Django test runner · coverage.py

**Constraints**:

- Python dependencies declared in `requirements.txt`; pinned versions in production.
- Frontend dependencies declared in `package.json`; lock file committed.
- Environment-specific config via `.env` files; secrets MUST NOT be committed.
- All media uploads MUST go through Cloudinary — local file storage is not permitted
  in production.
- The API MUST remain backward compatible within `/api/v1/`; any breaking change
  requires introducing `/api/v2/`.

## Development Workflow

1. **Spec before code**: New features MUST have a spec (`/speckit-specify`) before
   implementation begins.
2. **Plan before tasks**: A plan (`/speckit-plan`) MUST be reviewed before task
   generation (`/speckit-tasks`).
3. **Feature branches**: All work happens on branches named `feature/###-short-name`
   or `refactoring/###-short-name`; direct commits to `master` are not permitted.
4. **Tests first**: Per Principle III, tests MUST be written and confirmed failing
   before implementation.
5. **Code review**: All PRs MUST be reviewed. The reviewer MUST verify compliance
   with this constitution before approving.
6. **Merge only green**: CI MUST pass (tests, linting) before merge.

Quality gates (in order): spec → plan → failing tests → implementation →
green tests → review → merge.

## Governance

This constitution supersedes all other practices and informal conventions. When a
practice conflicts with this document, the constitution wins unless a formal
amendment is made.

**Amendment procedure**:

1. Author proposes a change with motivation and migration plan.
2. Change is documented in a PR that updates this file and any affected templates.
3. Version is bumped according to semantic versioning:
   - **MAJOR**: Principle removed, renamed, or fundamentally redefined.
   - **MINOR**: New principle or section added; material guidance expanded.
   - **PATCH**: Clarifications, wording, non-semantic refinements.
4. PR is merged only after team review.

**Compliance**: All PRs and reviews MUST verify constitution compliance. Use
`.specify/templates/checklist-template.md` as the review checklist baseline.

**Runtime development guidance**: See `CLAUDE.md` (architecture & code patterns)
and `DEVELOPMENT.md` (local setup & workflow) for day-to-day guidance that
supplements but does not override this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-05-28 | **Last Amended**: 2026-05-28
