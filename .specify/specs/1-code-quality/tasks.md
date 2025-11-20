# Implementation Tasks: Critical Fixes and Code Quality

**Spec**: `1-code-quality/spec.md` | **Plan**: `1-code-quality/plan.md`
**Branch**: `upgrade/1-project-analysis`
**Status**: Ready for Implementation

---

## Overview

This document breaks down the implementation plan into actionable tasks organized by priority and dependency. All 12 functional requirements are addressed across 6 phases.

**Total Tasks**: 24 | **Estimated Duration**: 5-6 hours | **Dependencies**: Sequential by phase

---

## Implementation Strategy

### Approach: Bug Fixes First, Code Quality Second

1. **Phase 1**: Critical bug fixes (database constraints, security, URL bug)
2. **Phase 2**: Code quality improvements (docstrings, magic string replacement)
3. **Phase 3**: Exception handling and cache enablement
4. **Phase 4**: Testing and verification

### Why This Order?

- Database constraints must be in place before tests can pass
- Security fix (ArticleUpdateView) is critical and blockers other work
- Code quality (docstrings, constants) can be done while tests are running
- Testing verifies everything works together

### MVP Scope

**Minimum Viable Product** (can deploy after Phase 1):
- All 6 critical bugs fixed (FR-001 to FR-006)
- Database constraints in place
- Tests passing

**Full Feature** (after Phase 4):
- All 12 requirements implemented
- ≥85% test coverage on critical paths
- Code review approval

---

## Phase 1: Critical Bug Fixes

### Profile Property Fix

- [ ] T001 Fix Profile.is_reader property logic in `accounts/models.py` (1 line change)
  - Current: Returns True always
  - Fix: Return `self.role == 'reader'`
  - Test: Reader/Writer/Admin profiles return correct boolean values

### Database Constraints - Article Title Uniqueness

- [ ] T002 Update Article model title constraint in `content/models.py`
  - Remove: `unique=True` from title field
  - Add: `unique_together = ('bulletin', 'title')` to Meta class
  - Test: Same title allowed in different bulletins, blocked in same bulletin

- [ ] T003 Create migration for Article title constraint
  - Command: `python manage.py makemigrations content`
  - Review: Check migration file for correct constraint definition
  - Verify: Migration shows RemoveConstraint then AddConstraint

### Database Constraints - Engagement Models

- [ ] T004 [P] Add unique constraint to Like model in `engagement/models.py`
  - Add: `unique_together = ('user', 'article')` to Meta class
  - Test: Duplicate like raises IntegrityError

- [ ] T005 [P] Add unique constraint to Comment model in `engagement/models.py`
  - Add: `unique_together = ('user', 'article')` to Meta class
  - Test: Duplicate comment raises IntegrityError

- [ ] T006 [P] Add unique constraint to ReadLater model in `engagement/models.py`
  - Add: `unique_together = ('user', 'article')` to Meta class
  - Test: Duplicate read-later raises IntegrityError

- [ ] T007 Create migrations for engagement model constraints
  - Command: `python manage.py makemigrations engagement`
  - Verify: Three migration files created for Like, Comment, ReadLater

- [ ] T008 Apply all migrations to database
  - Command: `python manage.py migrate`
  - Verify: All migrations applied successfully
  - Test: No migration errors, database state valid

### Security Fix - ArticleUpdateView

- [ ] T009 Add ArticleOwnerMixin to ArticleUpdateView in `content/views.py`
  - Current: `class ArticleUpdateView(WriterRequiredMixin, UpdateView):`
  - Fix: `class ArticleUpdateView(ArticleOwnerMixin, WriterRequiredMixin, UpdateView):`
  - Test: Non-owner receives 403 Forbidden on edit attempt

### URL Bug Fix - ArticleDeleteView

- [ ] T010 Fix ArticleDeleteView redirect URL in `content/views.py`
  - Current: Uses `self.user.username` (non-existent attribute)
  - Fix: Use `self.object.bulletin.owner.user.username`
  - Test: Article deletion redirects to bulletin owner's profile correctly

### Form Validation Fix

- [ ] T011 Fix ArticleForm content field validation in `content/forms.py`
  - Current: `required=False` but validates as required (inconsistent)
  - Fix: Change to `required=True`
  - Test: Creating article without content fails validation

---

## Phase 2: Code Quality - Magic String Replacement

### Profile Role Constants

- [ ] T012 Replace magic strings with choice constants in `accounts/models.py`
  - Ensure: `Profile.ROLE_CHOICES` is defined with ('reader', 'writer', 'admin') values
  - Test: Verify constants exist and are used in field definition

### Article Choice Constants

- [ ] T013 [P] Add/verify choice constants in `content/models.py`
  - Add if missing: `Article.STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]`
  - Add if missing: `Article.EVALUATION_CHOICES = [('pending', 'Pending'), ('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected')]`
  - Add if missing: `Article.VISIBILITY_CHOICES = [('public', 'Public'), ('private', 'Private')]`
  - Test: All constants defined and used in field definitions

### Replace Magic Strings - Views

- [ ] T014 Replace magic strings in `content/views.py` with constants
  - Search: Find all hardcoded 'draft', 'published', 'pending', 'under_review', 'approved', 'rejected'
  - Replace: Use `Article.STATUS_CHOICES`, `Article.EVALUATION_CHOICES` constants
  - Test: No hardcoded status strings remain in views

- [ ] T015 [P] Replace magic strings in `accounts/views.py` with constants
  - Search: Find all hardcoded 'reader', 'writer', 'admin'
  - Replace: Use `Profile.ROLE_CHOICES` constants
  - Test: No hardcoded role strings remain in views

- [ ] T016 [P] Replace magic strings in `engagement/views.py` with constants
  - Search: Find all hardcoded status/role values
  - Replace: Use appropriate choice constants
  - Test: No hardcoded magic strings remain in engagement views

### Replace Magic Strings - Templates

- [ ] T017 Replace magic strings in templates with Django template filters
  - Files: `templates/content/article_detail.html`, `templates/accounts/profile_detail.html`
  - Search: Find hardcoded 'draft', 'published', etc.
  - Replace: Use Django template variables with get_*_display() filters
  - Test: Templates render choice labels correctly

---

## Phase 3: Code Quality - View Docstrings

### Accounts Views Docstrings

- [ ] T018 [P] Add docstring to LoginView in `accounts/views.py`
  - Format: Google style with Permissions, Query Optimization, Returns sections
  - Include: Which users can login, any caching, what context is passed

- [ ] T019 [P] Add docstring to SignUpView in `accounts/views.py`
  - Include: Permission requirements, user creation defaults, context variables

- [ ] T020 [P] Add docstring to ProfileDetailView in `accounts/views.py`
  - Include: Permission checks, query optimization, rendered variables

- [ ] T021 [P] Add docstring to PromoteToWriterView in `accounts/views.py`
  - Include: Admin-only permission, role change behavior

- [ ] T022 [P] Add docstring to PromoteToAdminView in `accounts/views.py`
  - Include: Admin-only permission, role change behavior

### Content Views Docstrings

- [ ] T023 Add docstring to ArticleCreateView in `content/views.py`
  - Include: WriterRequiredMixin permission, draft/private defaults, bulletin assignment

- [ ] T024 Add docstring to ArticleUpdateView in `content/views.py`
  - Include: ArticleOwnerMixin enforcement, ownership verification

- [ ] T025 Add docstring to ArticleDeleteView in `content/views.py`
  - Include: Owner-only permission, redirect behavior, bulletin relationship

- [ ] T026 Add docstring to ArticleDetailView in `content/views.py`
  - Include: Public article viewing, engagement counts, prefetch optimization

- [ ] T027 Add docstring to ArticleListView in `content/views.py`
  - Include: Filter by visibility/status, pagination, cache duration

- [ ] T028 Add docstring to BulletinDetailView in `content/views.py`
  - Include: Writer's articles list, subscription status, author info

- [ ] T029 Add docstring to HomePageView in `content/views.py`
  - Include: Popular bulletins caching (60s), recent writers, cache strategy

- [ ] T030 Add docstring to ArticleSearchView in `content/views.py`
  - Include: Search functionality, pagination, query parameters

- [ ] T031 Add docstring to ArticleEvaluationView in `content/views.py`
  - Include: Admin-only permission, evaluation status update, article visibility changes

- [ ] T032 Add docstring to SubscriptionToggleView in `content/views.py`
  - Include: Reader-only permission, prevents self-subscription, toggle behavior

- [ ] T033 Add docstring to VisibilityToggleView in `content/views.py`
  - Include: Owner-only permission, visibility toggle, cache invalidation

### Engagement Views Docstrings

- [ ] T034 [P] Add docstring to LikeToggleView in `engagement/views.py`
  - Include: Prevents self-like (returns 403), toggle behavior, article notifications

- [ ] T035 [P] Add docstring to ReadLaterToggleView in `engagement/views.py`
  - Include: Prevents self-bookmark, toggle behavior, user's bookmarks list

- [ ] T036 [P] Add docstring to CommentCreateView in `engagement/views.py`
  - Include: One comment per user per article, update behavior, author notifications

---

## Phase 4: Exception Handling and Caching

### Fix Bare Except Clauses

- [ ] T037 Search for all bare except clauses in codebase
  - Command: `grep -r "except:" . --include="*.py"` (from project root)
  - Document: List all bare except locations

- [ ] T038 Fix bare except clauses with specific exception types
  - Files: All Python files identified in T037
  - Replace: `except:` → specific exception (IntegrityError, ObjectDoesNotExist, ValidationError, etc.)
  - Test: No bare except clauses remain in codebase

### Enable Cache in HomePageView

- [ ] T039 Enable cache usage in HomePageView in `content/views.py`
  - Current: Cache code exists but not used
  - Fix: Uncomment `@cache_page(60)` decorator OR manually use `cache.get/set()` in get_queryset()
  - Test: First load queries database, second load uses cache (no query)

---

## Phase 5: Testing and Verification

### Create/Update Tests

- [ ] T040 Create/update database constraint tests in `engagement/tests/`
  - Test files: `test_models.py`
  - Tests: Verify unique_together prevents duplicates for Like, Comment, ReadLater
  - Tests: Verify IntegrityError raised on duplicate insert

- [ ] T041 [P] Create/update ArticleUpdateView permission tests in `content/tests/test_views.py`
  - Test: Owner can edit article
  - Test: Non-owner receives 403 Forbidden

- [ ] T042 [P] Create/update ArticleDeleteView redirect tests in `content/tests/test_views.py`
  - Test: Delete redirects to bulletin owner correctly
  - Test: Redirect URL is valid and accessible

- [ ] T043 [P] Create/update Profile property tests in `accounts/tests/test_models.py`
  - Test: Reader profile is_reader=True, is_writer=False, is_admin=False
  - Test: Writer profile is_reader=False, is_writer=True, is_admin=False
  - Test: Admin profile is_reader=False, is_writer=False, is_admin=True

- [ ] T044 [P] Create/update ArticleForm validation tests in `content/tests/test_forms.py`
  - Test: Content field is required (raises validation error if empty)
  - Test: Valid article form saves successfully

### Run Tests and Verify Coverage

- [ ] T045 Run full test suite
  - Command: `python manage.py test`
  - Expected: 100% of tests pass
  - If failures: Fix tests or code, re-run

- [ ] T046 Generate coverage report
  - Command: `coverage run --source='.' manage.py test && coverage report`
  - Target: ≥85% coverage on critical paths (models, views, forms)
  - Expected: Models ≥90%, Views ≥85%, Forms ≥85%

- [ ] T047 Verify all acceptance criteria
  - Checklist:
    - ✅ All 12 functional requirements implemented
    - ✅ All tests passing (100% pass rate)
    - ✅ No bare except clauses in codebase
    - ✅ All views have docstrings
    - ✅ No magic strings in code
    - ✅ Database constraints verified
    - ✅ Cache enabled and working
    - ✅ Coverage ≥85% on critical paths

---

## Task Dependencies

### Dependency Graph

```
Phase 1 (Bug Fixes) - BLOCKING
├── T001: Profile.is_reader fix
├── T002-T003: Article title constraint
├── T004-T007: Engagement constraints + migrations
├── T009: ArticleUpdateView security
├── T010: ArticleDeleteView URL fix
└── T011: ArticleForm validation fix
    └── (All Phase 1 tasks must complete before Phase 2)

Phase 2 (Magic Strings) - PARALLEL
├── T012: Profile role constants
├── T013: Article choice constants
├── T014: Replace in views
├── T015: Replace in accounts views
├── T016: Replace in engagement views
└── T017: Replace in templates
    └── (All can run in parallel, all complete before Phase 3)

Phase 3 (Docstrings) - PARALLEL
├── T018-T022: Accounts views docstrings (parallel)
├── T023-T033: Content views docstrings (parallel)
└── T034-T036: Engagement views docstrings (parallel)
    └── (All can run in parallel, all complete before Phase 4)

Phase 4 (Exception Handling & Cache) - SEQUENTIAL
├── T037: Search for bare excepts
├── T038: Fix bare excepts
└── T039: Enable cache
    └── (All Phase 3 must complete before Phase 4)

Phase 5 (Testing) - SEQUENTIAL
├── T040-T044: Create/update tests (depends on Phase 1 fixes)
├── T045: Run tests (depends on Phase 1-4)
├── T046: Coverage report (depends on T045)
└── T047: Verification (depends on T046)
```

### Parallel Execution Opportunities

**Parallel Block 1** (after Phase 1 migrations):
- T012, T013, T014, T015, T016, T017 can all run in parallel

**Parallel Block 2** (Phase 3):
- T018-T036 (all docstring tasks) can run in parallel

**Parallel Block 3** (Phase 5 tests):
- T040, T041, T042, T043, T044 can run in parallel

---

## Success Criteria (Acceptance)

- [ ] **SC-001**: All 12 functional requirements implemented ✅
- [ ] **SC-002**: Test suite passes 100% ✅
- [ ] **SC-003**: ArticleDeleteView redirects work correctly ✅
- [ ] **SC-004**: ArticleUpdateView rejects non-owners (403) ✅
- [ ] **SC-005**: Database constraints prevent duplicates ✅
- [ ] **SC-006**: No hardcoded magic strings ✅
- [ ] **SC-007**: All views have docstrings ✅
- [ ] **SC-008**: Cache enabled and working ✅
- [ ] **SC-009**: No bare except clauses ✅
- [ ] **SC-010**: Coverage ≥85% on critical paths ✅

---

**Version**: 1.0.0 | **Status**: Ready for Implementation
