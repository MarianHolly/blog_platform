# Implementation Tasks: Admin Content Moderation Interface

**Spec**: `3-admin-moderation/spec.md` | **Plan**: `3-admin-moderation/plan.md`
**Branch**: `3-admin-moderation`
**Status**: Ready for Implementation

---

## Overview

This document breaks down the admin moderation interface into actionable tasks. The ArticleAdmin is already implemented; this plan focuses on testing and validation of all 10 functional requirements across 5 user stories.

**Total Tasks**: 15 | **Estimated Duration**: 2-3 hours | **Dependencies**: Sequential by phase

---

## Implementation Strategy

### Approach: Testing & Validation First

1. **Phase 1**: Create comprehensive test suite for existing ArticleAdmin implementation
2. **Phase 2**: Verify all 10 functional requirements pass tests
3. **Phase 3**: Manual testing and UI validation
4. **Phase 4**: Performance testing with large datasets

### Why This Order?

- ArticleAdmin is already implemented
- Tests verify requirements are met
- Manual testing confirms UX works as expected
- Performance testing validates scalability

### MVP Scope

**Minimum Viable Product** (all requirements met):
- All 10 functional requirements tested and passing
- Admin interface fully functional
- Performance targets met
- All acceptance scenarios verified

---

## Phase 1: Setup & Test Infrastructure

- [ ] T001 Create `content/tests/test_admin.py` test file for ArticleAdmin tests
  - File: `content/tests/test_admin.py`
  - Include: AdminTestCase base class, import necessary modules
  - Prepare: Setup test admin user, create test articles with various statuses

- [ ] T002 Verify ArticleAdmin is registered in `content/admin.py`
  - File: `content/admin.py`
  - Check: Article model is registered with ArticleAdmin class
  - Verify: All required attributes exist (list_display, list_filter, search_fields, actions)

---

## Phase 2: Foundational Tests

### User Story 1 & 2 & 3 Tests: Filtering and Bulk Actions

- [ ] T003 [P] [US1] Create test_admin_list_view() to verify articles display in list
  - File: `content/tests/test_admin.py`
  - Test: Admin list view renders all articles with evaluation status, visibility, status, created date visible
  - Expected: list_display includes ['title', 'author', 'evaluation', 'visibility', 'status', 'created']

- [ ] T004 [P] [US1] Create test_evaluation_filter() to verify evaluation status filter
  - File: `content/tests/test_admin.py`
  - Test: Filter articles by evaluation='pending', 'under_review', 'approved', 'rejected'
  - Expected: Only articles with matching evaluation status are shown

- [ ] T005 [P] [US3] Create test_visibility_filter() to verify visibility filter
  - File: `content/tests/test_admin.py`
  - Test: Filter articles by visibility='public', 'private'
  - Expected: Only articles with matching visibility are shown

- [ ] T006 [P] [US3] Create test_status_filter() to verify publication status filter
  - File: `content/tests/test_admin.py`
  - Test: Filter articles by status='draft', 'published'
  - Expected: Only articles with matching status are shown

- [ ] T007 [P] [US3] Create test_date_filter() to verify creation date filter
  - File: `content/tests/test_admin.py`
  - Test: Filter articles by creation date range
  - Expected: Only articles created within date range are shown

- [ ] T008 [US3] Create test_multiple_filters() to verify AND logic for combined filters
  - File: `content/tests/test_admin.py`
  - Test: Apply evaluation='pending' AND visibility='public' simultaneously
  - Expected: Only articles matching BOTH criteria are shown

- [ ] T009 [P] [US2] Create test_mark_under_review_action() to verify bulk action
  - File: `content/tests/test_admin.py`
  - Test: Select articles, execute "Mark Under Review" action
  - Expected: All selected articles' evaluation changed to 'under_review'

- [ ] T010 [P] [US2] Create test_approve_action() to verify bulk action
  - File: `content/tests/test_admin.py`
  - Test: Select articles, execute "Approve" action
  - Expected: All selected articles' evaluation changed to 'approved'

- [ ] T011 [P] [US2] Create test_reject_action() to verify bulk action
  - File: `content/tests/test_admin.py`
  - Test: Select articles, execute "Reject" action
  - Expected: All selected articles' evaluation changed to 'rejected'

---

## Phase 3: User Story Tests

### User Story 1: Admin Can View All Articles with Evaluation Status

- [ ] T012 [US1] Create test_admin_list_display_all_fields() to verify list display
  - File: `content/tests/test_admin.py`
  - Test: Admin list shows title, author, evaluation, visibility, status, created
  - Expected: All 6 fields are visible in list view
  - Acceptance: User Story 1, Scenario 1

- [ ] T013 [US1] Create test_can_sort_articles() to verify sorting
  - File: `content/tests/test_admin.py`
  - Test: Articles can be sorted by status, date, author, evaluation
  - Expected: Sorted results match sort order specified

### User Story 2: Admin Can Take Approval Actions

- [ ] T014 [US2] Create test_action_confirmation_message() to verify user feedback
  - File: `content/tests/test_admin.py`
  - Test: Admin receives confirmation message after action (e.g., "5 article(s) approved.")
  - Expected: message_user is called with correct count and action description

- [ ] T015 [US2] Create test_action_updates_database() to verify persistence
  - File: `content/tests/test_admin.py`
  - Test: After bulk action, articles in database have updated evaluation status
  - Expected: Database reflects changes immediately

### User Story 3: Admin Can Filter by Multiple Criteria

- [ ] T016 [US3] Create test_filter_state_persists() to verify filter persistence
  - File: `content/tests/test_admin.py`
  - Test: Apply filters, navigate away, return to article list
  - Expected: Filters are still active (state persists in URL query parameters)

### User Story 4: Admin Can Edit Articles Directly

- [ ] T017 [P] [US4] Create test_list_editable_evaluation() to verify inline editing
  - File: `content/tests/test_admin.py`
  - Test: Edit evaluation field directly in list view and save
  - Expected: Article evaluation is updated in database

- [ ] T018 [P] [US4] Create test_list_editable_visibility() to verify inline editing
  - File: `content/tests/test_admin.py`
  - Test: Edit visibility field directly in list view and save
  - Expected: Article visibility is updated in database

- [ ] T019 [US4] Create test_readonly_fields() to verify content is not editable
  - File: `content/tests/test_admin.py`
  - Test: Verify created, updated, bulletin fields are readonly
  - Expected: Fields cannot be edited in admin interface

### User Story 5: Admin Can See Article Author and Information

- [ ] T020 [P] [US5] Create test_author_field_display() to verify author name shows
  - File: `content/tests/test_admin.py`
  - Test: Author field displays writer's full name or username
  - Expected: Author name is visible in list view

- [ ] T021 [P] [US5] Create test_creation_date_display() to verify date shows
  - File: `content/tests/test_admin.py`
  - Test: Created field displays article creation date
  - Expected: Date is formatted and visible

- [ ] T022 [US5] Create test_search_by_title() to verify search functionality
  - File: `content/tests/test_admin.py`
  - Test: Search for articles by title substring
  - Expected: Only articles matching title substring are shown

- [ ] T023 [US5] Create test_search_by_author() to verify search functionality
  - File: `content/tests/test_admin.py`
  - Test: Search for articles by author username or name
  - Expected: Only articles from matching author are shown

---

## Phase 4: Security & Performance Tests

- [ ] T024 Create test_admin_permission_required() to verify admin-only access
  - File: `content/tests/test_admin.py`
  - Test: Non-admin user cannot access article admin
  - Expected: Non-admin receives 403 Forbidden or redirect

- [ ] T025 Create test_admin_list_performance() to verify query efficiency
  - File: `content/tests/test_admin.py`
  - Test: Load admin with 50+ articles
  - Expected: get_queryset uses select_related, no N+1 queries (verify with Django assertions)
  - Expected: List loads within 2 seconds

- [ ] T026 Create test_bulk_action_performance() to verify bulk action efficiency
  - File: `content/tests/test_admin.py`
  - Test: Perform bulk action on 10 articles
  - Expected: Completes within 5 seconds, uses efficient queryset.update()

---

## Phase 5: Integration & Manual Testing

- [ ] T027 Run full test suite for content app
  - Command: `python manage.py test content.tests.test_admin`
  - Expected: All tests pass (100% pass rate)

- [ ] T028 Generate test coverage report for ArticleAdmin
  - Command: `coverage run --source='content.admin' manage.py test content.tests.test_admin && coverage report`
  - Expected: Coverage ≥85% for ArticleAdmin class

- [ ] T029 Manual testing: Open Django admin and verify all features
  - Steps:
    1. Navigate to Django admin → Articles
    2. Verify list displays: title, author, evaluation, visibility, status, created
    3. Test each filter (evaluation, visibility, status, created)
    4. Test multiple filters together
    5. Test search by title
    6. Test search by author
    7. Test bulk actions (select 3 articles, execute "Approve")
    8. Test inline editing (change evaluation in list view)
    9. Test sorting by each column
    10. Open article detail and verify readonly/editable fields
  - Expected: All features work as described

- [ ] T030 Performance testing with large dataset
  - Steps:
    1. Create 100+ test articles with various statuses/evaluations
    2. Load article list in admin
    3. Measure load time (target <2 seconds)
    4. Apply filter and measure response time (target <1 second)
    5. Select 10 articles and run bulk action (target <5 seconds)
  - Expected: All performance targets met

---

## Phase 6: Verification & Sign-Off

- [ ] T031 Verify all 10 functional requirements are met
  - Checklist:
    - ✅ FR-001: ArticleAdmin displays all articles with evaluation status
    - ✅ FR-002: Filters for Evaluation, Visibility, Status, Date
    - ✅ FR-003: Multiple simultaneous filters with AND logic
    - ✅ FR-004: Bulk actions (Mark Under Review, Approve, Reject)
    - ✅ FR-005: Edit evaluation and visibility directly
    - ✅ FR-006: Display author, creation date, evaluation status
    - ✅ FR-007: Order by creation date (newest first)
    - ✅ FR-008: Admin-only access (permission check)
    - ✅ FR-009: Readonly fields for title, content, author
    - ✅ FR-010: Search by title and author

- [ ] T032 Verify all success criteria are met
  - Checklist:
    - ✅ SC-001: Admin list loads within 2 seconds
    - ✅ SC-002: Filter applies within 1 second
    - ✅ SC-003: Multiple filters work within 1 second
    - ✅ SC-004: Bulk action on 10 articles within 5 seconds
    - ✅ SC-005: List displays 25+ articles per page
    - ✅ SC-006: Search by title within 1 second
    - ✅ SC-007: Evaluation change reflected immediately
    - ✅ SC-008: Admin UI elements load correctly
    - ✅ SC-009: Non-admins see 403 error
    - ✅ SC-010: Works in modern browsers

- [ ] T033 Code review: Verify ArticleAdmin implementation quality
  - Checklist:
    - ✅ ArticleAdmin has comprehensive docstring
    - ✅ All action methods have docstrings
    - ✅ Uses Article choice constants (not magic strings)
    - ✅ Uses select_related for query optimization
    - ✅ No N+1 queries
    - ✅ All imports are necessary
    - ✅ Code follows Django admin patterns

---

## Task Dependencies

### Dependency Graph

```
Phase 1: Setup
├── T001: Create test file
└── T002: Verify ArticleAdmin registered
    └── (All Phase 2+ tests depend on Phase 1)

Phase 2: Foundational Tests
├── T003-T008: Filtering tests (can run in parallel)
└── T009-T011: Bulk action tests (can run in parallel)

Phase 3: User Story Tests
├── T012-T013: US1 tests (depends on T003)
├── T014-T015: US2 tests (depends on T009-T011)
├── T016: US3 tests (depends on T008)
├── T017-T019: US4 tests (no dependencies)
└── T020-T023: US5 tests (no dependencies)

Phase 4: Security & Performance
├── T024: Permission test (no dependencies)
├── T025-T026: Performance tests (no dependencies)

Phase 5: Integration
├── T027: Run test suite (depends on all tests)
├── T028: Coverage report (depends on T027)
├── T029-T030: Manual testing (no dependencies on automated tests)

Phase 6: Verification
├── T031-T033: Sign-off checks (depends on all prior tasks)
```

### Parallel Execution Opportunities

**Parallel Block 1** (Phase 2):
- T003-T011 can all run in parallel (different filter/action types)

**Parallel Block 2** (Phase 3):
- T012-T023 can mostly run in parallel (different user stories, no cross-dependencies)

**Parallel Block 3** (Phase 4):
- T024-T026 can run in parallel (different test types)

**Manual Testing** (Phase 5):
- T029-T030 can run in parallel or sequentially based on test environment

---

## Success Criteria (Acceptance)

- [ ] **SC-001**: All 10 functional requirements tested and passing ✅
- [ ] **SC-002**: Test suite passes 100% ✅
- [ ] **SC-003**: Admin list loads within 2 seconds ✅
- [ ] **SC-004**: Filters apply within 1 second ✅
- [ ] **SC-005**: Bulk actions complete within 5 seconds ✅
- [ ] **SC-006**: Search functionality works for title and author ✅
- [ ] **SC-007**: Inline editing updates database immediately ✅
- [ ] **SC-008**: Confirmation messages display correctly ✅
- [ ] **SC-009**: Permission checks enforce admin-only access ✅
- [ ] **SC-010**: Coverage ≥85% on ArticleAdmin ✅

---

**Version**: 1.0.0 | **Status**: Ready for Implementation
