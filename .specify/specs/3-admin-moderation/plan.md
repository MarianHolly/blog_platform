# Implementation Plan: Admin Content Moderation Interface

**Branch**: `3-admin-moderation` | **Date**: 2025-11-24 | **Spec**: `3-admin-moderation/spec.md`
**Input**: Feature specification for admin content moderation interface

## Summary

Verify and enhance the ArticleAdmin interface to provide comprehensive article moderation with filtering, bulk actions, and direct editing. The admin interface is largely implemented; this plan focuses on testing, validation, and any missing functionality.

## Technical Context

**Language/Version**: Python 3.11+ | Django 5.2
**Primary Dependencies**: Django admin, PostgreSQL, Celery (optional for notifications)
**Storage**: PostgreSQL (primary)
**Testing**: Django TestCase, Selenium (admin UI tests)
**Target Platform**: Django admin interface (web application)
**Project Type**: Django monolith with 5 apps
**Performance Goals**: Admin list loads within 2 seconds, filters apply within 1 second, bulk actions on 10 articles within 5 seconds
**Constraints**: Must work with large article counts (100+), efficient querying with select_related/prefetch_related
**Scale/Scope**: ~1 admin class (ArticleAdmin), ~10 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Clarity
- ✅ **Descriptive naming**: ArticleAdmin, action_mark_under_review, action_approve, action_reject
- ✅ **Single responsibility**: Each action has one clear purpose
- ✅ **Magic strings eliminated**: Uses Article.EVALUATION_CHOICES, Article.VISIBILITY_CHOICES, Article.STATUS_CHOICES
- ✅ **Docstrings**: ArticleAdmin has comprehensive docstring; all actions have docstrings
- **GATE PASS**: Admin interface follows code quality principles

### Principle II: Test-Driven Development
- ✅ **All requirements have test acceptance criteria** defined in spec.md
- ✅ **Admin interface tests**: Test list view, filters, bulk actions, permissions
- ✅ **Search tests**: Test title and author search
- **GATE PASS**: Feature spec includes test scenarios for all 10 functional requirements

### Principle III: Testing Standards & Coverage
- ✅ **Target coverage**: Admin interface should have ≥85% coverage
- ✅ **Unit tests**: Filter logic, action execution, queryset optimization
- ✅ **Integration tests**: Full admin workflows (filter → select → action)
- ✅ **UI tests**: Admin list view renders correctly, filters work, actions execute
- **GATE PASS**: Testing strategy aligns with constitution

### Principle IV: Readable Minimalistic Design
- ✅ **YAGNI**: Only includes necessary admin features (list, filter, search, bulk actions)
- ✅ **Simplicity**: Uses Django's built-in admin framework (no custom dashboard)
- ✅ **Minimal dependencies**: No new external libraries required
- **GATE PASS**: Design is minimal and justified

### Principle V: Consistency & Coherent UX
- ✅ **Django conventions**: Uses standard admin ModelAdmin patterns
- ✅ **Consistent naming**: Action methods follow Django admin pattern (action_*)
- ✅ **Error handling**: Uses Django admin's message_user for feedback
- **GATE PASS**: Changes maintain consistency with existing codebase

**Overall Constitution Compliance**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
.specify/specs/3-admin-moderation/
├── spec.md                    # Feature specification
├── plan.md                    # This file
├── checklists/requirements.md # Quality validation
└── tasks.md                   # Phase 2 (to be generated)
```

### Source Code (repository root)

```text
Django Monolith

content/
├── admin.py                   # ArticleAdmin (ALREADY IMPLEMENTED)
├── models.py                  # Article model (ALREADY IMPLEMENTED)
└── tests/
    ├── test_admin.py         # Tests for ArticleAdmin (TO CREATE)
    └── test_models.py        # Existing model tests

accounts/
├── models.py                  # Profile model
└── tests/

engagement/
├── models.py                  # Like, Comment, ReadLater models
└── tests/
```

**Structure Decision**: ArticleAdmin is already fully implemented in `content/admin.py`. All 10 functional requirements appear to be met. Plan focuses on testing and validation.

## Implementation Tasks

### Phase 1: Verification & Testing (2 hours)

**Task 1.1**: Verify ArticleAdmin implementation
- **File**: `content/admin.py`
- **Check**: All 10 functional requirements are implemented
  - list_display shows title, author, evaluation, visibility, status, created
  - list_filter includes evaluation, visibility, status, created
  - search_fields includes title and bulletin__owner__user__username
  - list_editable allows editing evaluation and visibility
  - date_hierarchy for easy navigation
  - Bulk actions: mark_under_review, approve, reject
  - get_queryset optimizes with select_related
- **Test**: Verify implementation matches spec

**Task 1.2**: Create admin interface tests
- **File**: `content/tests/test_admin.py` (new file)
- **Tests needed**:
  - Admin list view renders all articles
  - Evaluation status filter works
  - Visibility filter works
  - Status filter works
  - Multiple filters work together (AND logic)
  - Date filter works
  - Author name displays correctly
  - Search by title works
  - Search by author username works
  - Bulk action: mark_under_review updates articles
  - Bulk action: approve updates articles
  - Bulk action: reject updates articles
  - list_editable fields update article state
  - Permission check: only admins can access
  - Performance: queryset uses select_related

**Task 1.3**: Create integration tests for admin workflows
- **File**: `content/tests/test_admin.py`
- **Tests needed**:
  - Admin can filter by evaluation, then apply bulk action
  - Admin can search for article, then edit evaluation
  - Admin can apply multiple filters, then select all and approve
  - Admin action provides confirmation message

**Task 1.4**: Run tests and validate coverage
- **Command**: `python manage.py test content.tests.test_admin`
- **Expected**: All tests pass
- **Coverage**: ≥85% on ArticleAdmin

**Task 1.5**: Test admin interface manually
- Open Django admin
- Navigate to Articles
- Verify list display, filters, search, bulk actions work
- Test filtering by multiple criteria
- Test bulk actions and confirmations

---

### Phase 2: Enhancement (optional, 1 hour)

**Task 2.1**: Add ordering options (if not present)
- **File**: `content/admin.py`
- **Check**: Can order by evaluation, status, author, date
- **Current**: Default ordering is by creation date (newest first)

**Task 2.2**: Add readonly_fields for content (if not present)
- **File**: `content/admin.py`
- **Check**: Article content is visible but not editable in admin
- **Rationale**: Admins should not edit article content; use evaluation/visibility for moderation

**Task 2.3**: Test performance with large dataset
- **Test**: Load admin with 100+ articles
- **Expected**: <2 seconds load time
- **Verify**: select_related prevents N+1 queries

---

### Phase 3: Completion & Verification (0.5 hours)

**Task 3.1**: Run full test suite
- **Command**: `python manage.py test content`
- **Expected**: All tests pass, ≥85% coverage

**Task 3.2**: Code review checklist
- ✅ All 10 functional requirements implemented
- ✅ All tests passing (100% pass rate)
- ✅ No permission issues (admin-only)
- ✅ Search and filters work
- ✅ Bulk actions work correctly
- ✅ Performance acceptable (select_related used)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admin list loads within 2 seconds ✅
- **SC-002**: Filter applies within 1 second ✅
- **SC-003**: Multiple filters work together (AND logic) ✅
- **SC-004**: Bulk action on 10 articles completes within 5 seconds ✅
- **SC-005**: Search by title finds articles within 1 second ✅
- **SC-006**: Search by author finds articles within 1 second ✅
- **SC-007**: Bulk action updates article evaluation status immediately ✅
- **SC-008**: Admin sees confirmation message after action ✅
- **SC-009**: Non-admins cannot access article admin ✅
- **SC-010**: All functional requirements implemented and tested ✅

---

## Assumptions

- Django admin is the appropriate location for moderation (confirmed in spec)
- Admin users have superuser or staff status (Django standard)
- Bulk actions use Django admin's standard action framework (confirmed in implementation)
- Filters use Django admin's list_filter (confirmed in implementation)
- Performance targets assume development environment (not production-optimized)
- Article counts stay within reasonable range (< 10,000 articles)

---

**Version**: 1.0.0 | **Status**: Ready for Task Generation | **Next**: Run `/speckit.tasks` to generate task list
