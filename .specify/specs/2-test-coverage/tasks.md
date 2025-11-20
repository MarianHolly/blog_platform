# Implementation Tasks: Comprehensive Test Coverage and Integration Tests

**Spec**: `2-test-coverage/spec.md` | **Plan**: `2-test-coverage/plan.md`
**Branch**: `upgrade/1-project-analysis`
**Status**: Ready for Implementation

---

## Overview

This document breaks down the test implementation plan into actionable tasks organized by test type and dependency. Target is ≥85% coverage on critical paths with comprehensive unit, integration, and GUI tests.

**Total Tasks**: 45 | **Estimated Duration**: 6-8 hours | **Dependencies**: Model tests → View tests → Integration tests

---

## Implementation Strategy

### Approach: Test Layers Bottom-Up

1. **Phase 1**: Model tests (simplest, no dependencies)
2. **Phase 2**: Form tests (depend on models)
3. **Phase 3**: View tests (depend on models, forms, and permissions)
4. **Phase 4**: Permission tests (depend on views)
5. **Phase 5**: Integration tests (depend on all components)
6. **Phase 6**: GUI tests (depend on all components)
7. **Phase 7**: Coverage analysis and reporting

### Why This Order?

- Models are foundational; test them first
- Forms depend on models; test after models
- Views depend on models and forms; test after both
- Permissions use existing mixins; test after views
- Integration tests use complete workflows
- GUI tests verify end-to-end user interactions
- Coverage analysis identifies gaps from all tests

### MVP Scope

**Minimum Viable Product** (after Phase 3):
- All model tests passing (100%)
- All form tests passing (100%)
- All view tests passing (100%)
- Coverage ≥80% on critical paths

**Full Feature** (after Phase 7):
- All tests passing (model, form, view, permission, integration, GUI)
- ≥85% coverage on critical paths
- Zero failing tests

---

## Phase 1: Model Tests

### Profile Model Tests

- [ ] T001 Create Profile model tests in `accounts/tests/test_models.py`
  - Test: test_reader_profile_is_reader_returns_true
    - Create: User with profile role='reader'
    - Assert: profile.is_reader == True
  - Test: test_reader_profile_is_writer_returns_false
    - Create: User with profile role='reader'
    - Assert: profile.is_writer == False
  - Test: test_reader_profile_is_admin_returns_false
    - Create: User with profile role='reader'
    - Assert: profile.is_admin == False
  - Test: test_writer_profile_is_writer_returns_true
    - Create: User with profile role='writer'
    - Assert: profile.is_writer == True
  - Test: test_writer_profile_has_bulletin
    - Create: Writer profile
    - Assert: profile.bulletin exists and is Bulletin instance
  - Test: test_admin_profile_is_admin_returns_true
    - Create: User with profile role='admin'
    - Assert: profile.is_admin == True

### Article Model Tests

- [ ] T002 Create Article model tests in `content/tests/test_models.py`
  - Test: test_article_creation_sets_default_status_draft
    - Create: Article without status
    - Assert: article.status == 'draft'
  - Test: test_article_creation_sets_default_visibility_private
    - Create: Article without visibility
    - Assert: article.visibility == 'private'
  - Test: test_article_is_draft_property_returns_true_when_status_draft
    - Create: Article with status='draft'
    - Assert: article.is_draft == True
  - Test: test_article_is_published_property_returns_true_when_status_published
    - Create: Article with status='published'
    - Assert: article.is_published == True
  - Test: test_article_title_unique_per_bulletin_allows_same_title_different_bulletins
    - Create: Article in bulletin1 with title="Test"
    - Create: Article in bulletin2 with title="Test"
    - Assert: No IntegrityError, both articles exist
  - Test: test_article_title_unique_per_bulletin_prevents_duplicate_in_same_bulletin
    - Create: Article in bulletin1 with title="Test"
    - Create: Article in same bulletin with same title
    - Assert: IntegrityError raised
  - Test: test_article_save_sanitizes_html_content
    - Create: Article with unsafe HTML (<script>alert('xss')</script>)
    - Assert: Unsafe tags removed, safe tags preserved
  - Test: test_article_get_absolute_url_returns_correct_path
    - Create: Article
    - Assert: get_absolute_url() returns valid URL

### Like Model Tests

- [ ] T003 [P] Create Like model tests in `engagement/tests/test_models.py`
  - Test: test_like_creation_sets_timestamp
    - Create: Like
    - Assert: created_at timestamp is set
  - Test: test_like_unique_constraint_prevents_duplicate_likes
    - Create: Like for user1 on article1
    - Create: Like for same user on same article
    - Assert: IntegrityError raised

### Comment Model Tests

- [ ] T004 [P] Create Comment model tests in `engagement/tests/test_models.py`
  - Test: test_comment_creation_stores_text
    - Create: Comment with text="Great article!"
    - Assert: comment.text == "Great article!"
  - Test: test_comment_unique_constraint_prevents_duplicate_comments
    - Create: Comment for user1 on article1
    - Create: Comment for same user on same article
    - Assert: IntegrityError raised
  - Test: test_comment_update_preserves_comment_not_duplicate
    - Create: Comment
    - Update: comment.text = "Updated text"
    - Save: comment.save()
    - Assert: Only one comment exists for user/article, text updated

### ReadLater Model Tests

- [ ] T005 [P] Create ReadLater model tests in `engagement/tests/test_models.py`
  - Test: test_read_later_creation_sets_timestamp
    - Create: ReadLater
    - Assert: created_at timestamp is set
  - Test: test_read_later_unique_constraint_prevents_duplicate_bookmarks
    - Create: ReadLater for user1 on article1
    - Create: ReadLater for same user on same article
    - Assert: IntegrityError raised

### Bulletin Model Tests

- [ ] T006 [P] Create Bulletin model tests in `content/tests/test_models.py`
  - Test: test_bulletin_creation_assigns_owner
    - Create: Bulletin with owner=user
    - Assert: bulletin.owner == user
  - Test: test_bulletin_get_articles_returns_only_published_articles
    - Create: Bulletin with 2 published and 2 draft articles
    - Call: bulletin.get_articles()
    - Assert: Returns only published articles

---

## Phase 2: Form Tests

### ArticleForm Tests

- [ ] T007 Create ArticleForm tests in `content/tests/test_forms.py`
  - Test: test_article_form_requires_title
    - Create: Form without title
    - Assert: form.is_valid() == False, error on 'title' field
  - Test: test_article_form_requires_content
    - Create: Form without content
    - Assert: form.is_valid() == False, error on 'content' field
  - Test: test_article_form_accepts_valid_data
    - Create: Form with title and content
    - Assert: form.is_valid() == True
  - Test: test_article_form_saves_to_database
    - Create: Form with valid data
    - Save: article = form.save()
    - Assert: article.id is set, article exists in database

### CommentForm Tests

- [ ] T008 [P] Create CommentForm tests in `engagement/tests/test_forms.py`
  - Test: test_comment_form_requires_text
    - Create: Form without text
    - Assert: form.is_valid() == False
  - Test: test_comment_form_accepts_valid_data
    - Create: Form with text="Great article!"
    - Assert: form.is_valid() == True
  - Test: test_comment_form_saves_to_database
    - Create: Form with valid data
    - Save: comment = form.save()
    - Assert: comment.id is set

### SignUpForm Tests

- [ ] T009 [P] Create SignUpForm tests in `accounts/tests/test_forms.py`
  - Test: test_signup_form_requires_username
    - Create: Form without username
    - Assert: form.is_valid() == False
  - Test: test_signup_form_requires_email
    - Create: Form without email
    - Assert: form.is_valid() == False
  - Test: test_signup_form_requires_password
    - Create: Form without password
    - Assert: form.is_valid() == False
  - Test: test_signup_form_password_confirmation_matches
    - Create: Form with password='pass123' and password_confirm='pass456'
    - Assert: form.is_valid() == False, passwords don't match error
  - Test: test_signup_form_creates_user_and_profile
    - Create: Form with valid data
    - Save: user = form.save()
    - Assert: User created, Profile created with role='reader'

---

## Phase 3: View Tests

### Article Create View Tests

- [ ] T010 Create ArticleCreateView tests in `content/tests/test_views.py`
  - Test: test_article_create_view_requires_writer_role
    - Create: Reader user, login
    - Access: POST to article-create with data
    - Assert: Status 403 (PermissionDenied)
  - Test: test_article_create_view_writer_can_create
    - Create: Writer user, login
    - Access: POST to article-create with valid data
    - Assert: Status 302 (redirect), Article created
  - Test: test_article_create_view_creates_article_as_draft
    - Create: Writer, POST article
    - Assert: article.status == 'draft'
  - Test: test_article_create_view_sets_visibility_to_private
    - Create: Writer, POST article
    - Assert: article.visibility == 'private'
  - Test: test_article_create_view_assigns_to_writer_bulletin
    - Create: Writer with bulletin, POST article
    - Assert: article.bulletin == writer.profile.bulletin

### Article Update View Tests

- [ ] T011 Create ArticleUpdateView tests in `content/tests/test_views.py`
  - Test: test_article_update_view_owner_can_edit
    - Create: Writer, article, login
    - Access: POST to article-update with new title
    - Assert: Status 302, article.title updated
  - Test: test_article_update_view_non_owner_receives_403
    - Create: Article by writer1, writer2 login
    - Access: POST to article-update URL
    - Assert: Status 403 (PermissionDenied)
  - Test: test_article_update_view_superuser_cannot_edit_others_articles
    - Create: Article by writer1, superuser with no bulletin login
    - Access: POST to article-update
    - Assert: Status 403 (ArticleOwnerMixin enforced even for superuser)

### Article Delete View Tests

- [ ] T012 Create ArticleDeleteView tests in `content/tests/test_views.py`
  - Test: test_article_delete_view_owner_can_delete
    - Create: Writer, article, login
    - Access: POST to article-delete
    - Assert: Status 302, article deleted from database
  - Test: test_article_delete_view_redirects_to_bulletin_owner
    - Create: Writer with article, delete article
    - Assert: Redirect URL contains writer's username
  - Test: test_article_delete_view_non_owner_receives_403
    - Create: Article by writer1, writer2 login
    - Access: POST to article-delete
    - Assert: Status 403

### Article Detail View Tests

- [ ] T013 [P] Create ArticleDetailView tests in `content/tests/test_views.py`
  - Test: test_article_detail_view_renders_article
    - Create: Published article
    - Access: GET article-detail
    - Assert: Status 200, article in context
  - Test: test_article_detail_view_shows_comments_and_likes_count
    - Create: Article with 3 likes, 2 comments
    - Access: GET article-detail
    - Assert: Context shows correct counts

### Like Toggle View Tests

- [ ] T014 Create LikeToggleView tests in `engagement/tests/test_views.py`
  - Test: test_like_toggle_adds_like
    - Create: Reader, article, login
    - Access: POST to like-toggle for article
    - Assert: Status 200, Like created in database
  - Test: test_like_toggle_removes_like_if_exists
    - Create: Reader with existing like, login
    - Access: POST to like-toggle
    - Assert: Status 200, Like deleted
  - Test: test_like_toggle_user_cannot_like_own_article
    - Create: Writer with article, login
    - Access: POST to like-toggle for own article
    - Assert: Status 403

### Comment Create View Tests

- [ ] T015 Create CommentCreateView tests in `engagement/tests/test_views.py`
  - Test: test_comment_create_view_creates_comment
    - Create: Reader, article, login
    - Access: POST to comment-create with text
    - Assert: Status 302, Comment created
  - Test: test_comment_create_view_updates_existing_comment
    - Create: Reader with existing comment, login
    - Access: POST with new text
    - Assert: Comment updated, not duplicated
  - Test: test_comment_create_view_user_cannot_comment_on_own_article
    - Create: Writer with article, login
    - Access: POST to comment-create
    - Assert: Status 403

### ReadLater Toggle View Tests

- [ ] T016 Create ReadLaterToggleView tests in `engagement/tests/test_views.py`
  - Test: test_read_later_toggle_adds_bookmark
    - Create: Reader, article, login
    - Access: POST to read-later-toggle
    - Assert: Status 200, ReadLater created
  - Test: test_read_later_toggle_removes_bookmark_if_exists
    - Create: Reader with bookmark, login
    - Access: POST to read-later-toggle
    - Assert: Status 200, ReadLater deleted
  - Test: test_read_later_toggle_user_cannot_bookmark_own_article
    - Create: Writer with article, login
    - Access: POST to read-later-toggle
    - Assert: Status 403

### Authentication View Tests

- [ ] T017 [P] Create authentication view tests in `accounts/tests/test_views.py`
  - Test: test_signup_creates_reader_user
    - Access: POST to signup with user data
    - Assert: Status 302, User created with role='reader'
  - Test: test_login_authenticates_user
    - Create: User, POST login credentials
    - Assert: Status 302, user is authenticated
  - Test: test_profile_detail_view_shows_user_info
    - Create: User, login, access profile
    - Assert: Status 200, user info in context

---

## Phase 4: Permission Tests

### ArticleOwnerMixin Tests

- [ ] T018 Create ArticleOwnerMixin tests in `content/tests/test_permissions.py`
  - Test: test_article_owner_mixin_allows_owner
    - Create: Article by writer1, login as writer1
    - Access: View requiring ArticleOwnerMixin
    - Assert: Status 200 (access granted)
  - Test: test_article_owner_mixin_blocks_non_owner
    - Create: Article by writer1, login as writer2
    - Access: View requiring ArticleOwnerMixin
    - Assert: Status 403 (access denied)

### Self-Engagement Prevention Tests

- [ ] T019 Create self-engagement prevention tests in `engagement/tests/test_permissions.py`
  - Test: test_user_cannot_like_own_article
    - Create: Writer, own article, login
    - Access: POST like-toggle for own article
    - Assert: Status 403
  - Test: test_user_cannot_comment_on_own_article
    - Create: Writer, own article, login
    - Access: POST comment-create for own article
    - Assert: Status 403
  - Test: test_user_cannot_bookmark_own_article
    - Create: Writer, own article, login
    - Access: POST read-later-toggle for own article
    - Assert: Status 403

### Role-Based Access Tests

- [ ] T020 [P] Create role-based access tests in `accounts/tests/test_permissions.py`
  - Test: test_reader_cannot_create_article
    - Create: Reader user, login
    - Access: POST to article-create
    - Assert: Status 403
  - Test: test_writer_can_create_article
    - Create: Writer user, login
    - Access: POST to article-create
    - Assert: Status 302 or 200 (success)
  - Test: test_non_admin_cannot_evaluate_articles
    - Create: Reader/Writer user, login
    - Access: POST to article-evaluate
    - Assert: Status 403
  - Test: test_admin_can_evaluate_articles
    - Create: Admin user, login
    - Access: POST to article-evaluate
    - Assert: Status 200 or 302 (success)

---

## Phase 5: Integration Tests

### Article Lifecycle Integration Tests

- [ ] T021 Create article lifecycle integration tests in `content/tests/test_integration.py` (NEW FILE)
  - Test: test_reader_signup_discover_and_engage_workflow
    - Setup: Create writer with published article
    - Act: Reader signup, login, find article, like, comment
    - Assert: Reader has like and comment in database
  - Test: test_writer_create_publish_workflow
    - Setup: Create writer user, login
    - Act: Create article, publish (status='published')
    - Assert: Article appears in public list
  - Test: test_admin_evaluate_approve_workflow
    - Setup: Create article in evaluation
    - Act: Admin approves article
    - Assert: Article.evaluation == 'approved'
  - Test: test_reader_subscribe_view_articles_workflow
    - Setup: Create bulletin with articles
    - Act: Reader subscribe to bulletin, view articles
    - Assert: Reader sees bulletin's articles

### Multi-User Engagement Integration Tests

- [ ] T022 [P] Create multi-user integration tests in `content/tests/test_integration.py`
  - Test: test_multiple_readers_engage_with_article
    - Setup: Create article
    - Act: Reader1 likes, Reader2 comments, Reader3 bookmarks
    - Assert: All engagements recorded correctly
  - Test: test_comment_thread_multiple_readers
    - Setup: Create article
    - Act: Reader1 comments, Reader2 comments, Reader1 updates
    - Assert: Two comments exist (not duplicates), updated text correct

---

## Phase 6: GUI Tests

### Enable and Verify GUI Tests

- [ ] T023 Enable GUI tests in `content/tests/test_gui.py`
  - Remove: @skip decorators from all test methods
  - Verify: All test methods have proper test_ prefix
  - Run: `python manage.py test content.tests.test_gui`
  - Assert: All tests pass without manual intervention

- [ ] T024 [P] Create/update page load tests in `content/tests/test_gui.py`
  - Test: test_homepage_loads_without_errors
    - Access: GET /
    - Assert: Status 200
  - Test: test_article_list_page_displays_articles
    - Setup: Create published articles
    - Access: GET article list URL
    - Assert: Status 200, articles in HTML
  - Test: test_article_detail_page_renders
    - Setup: Create article
    - Access: GET article detail URL
    - Assert: Status 200, article content visible

- [ ] T025 [P] Create/update form submission tests in `content/tests/test_gui.py`
  - Test: test_article_creation_form_submission
    - Setup: Login as writer
    - Access: GET article-create form
    - Assert: Form fields display
    - Act: POST with valid data
    - Assert: Status 302, article created
  - Test: test_comment_form_submission
    - Setup: Create article, login as reader
    - Act: POST comment form with text
    - Assert: Comment appears on page

- [ ] T026 [P] Create/update navigation tests in `content/tests/test_gui.py`
  - Test: test_navigation_links_work
    - Access: GET homepage
    - Assert: Navigation links present and valid
  - Test: test_article_detail_back_to_list
    - Setup: Create article
    - Access: Article detail page
    - Assert: Link back to list works

---

## Phase 7: Coverage Analysis and Reporting

### Coverage Configuration

- [ ] T027 Create .coveragerc configuration file
  - File: `.coveragerc` (if not exists)
  - Config: Include accounts/, content/, engagement/ apps
  - Config: Exclude migrations, __pycache__, tests
  - Config: Set precision to 2 decimal places

### Generate Coverage Reports

- [ ] T028 Run test suite with coverage tracking
  - Command: `coverage run --source='.' manage.py test`
  - Expected: All tests pass
  - Result: .coverage file generated

- [ ] T029 Generate coverage report
  - Command: `coverage report`
  - Output: Terminal report showing coverage percentages
  - Target: ≥85% overall on critical paths (accounts, content, engagement)

- [ ] T030 Generate HTML coverage report
  - Command: `coverage html`
  - Output: htmlcov/index.html with detailed coverage
  - Review: Identify uncovered lines in critical code

### Analyze Coverage Gaps

- [ ] T031 Identify coverage gaps in critical files
  - Files to review: accounts/models.py, accounts/views.py, content/models.py, content/views.py, engagement/models.py, engagement/views.py
  - Target: Each file ≥85% coverage
  - Document: List any files below target with reasoning

- [ ] T032 Write additional tests for gaps (if identified)
  - For each uncovered critical code path:
    - Write new test to cover the path
    - Ensure test has clear name and Arrange-Act-Assert structure
  - Re-run coverage after each test addition

### Final Coverage Verification

- [ ] T033 Verify coverage target achieved
  - Command: `coverage report`
  - Assert: ≥85% coverage on critical paths
  - Assert: accounts/models.py ≥85%
  - Assert: accounts/views.py ≥85%
  - Assert: content/models.py ≥90%
  - Assert: content/views.py ≥85%
  - Assert: engagement/models.py ≥85%
  - Assert: engagement/views.py ≥85%

---

## Verification Checklist

### All Tests Passing

- [ ] T034 Run full test suite final verification
  - Command: `python manage.py test`
  - Assert: 100% of tests pass
  - Assert: No skipped tests (except intentional)
  - Assert: No failures or errors

### Test Quality Standards

- [ ] T035 Verify test naming conventions
  - Pattern: test_[actor]_[action]_[expected_outcome]
  - Examples: test_reader_cannot_like_own_article, test_writer_can_create_article
  - Assert: All tests follow naming pattern

- [ ] T036 Verify test independence
  - Requirement: Each test creates own fixtures
  - Requirement: No shared state between tests
  - Requirement: Tests can run in any order
  - Command: `python manage.py test --shuffle`
  - Assert: All tests pass in random order

### Documentation and Reporting

- [ ] T037 Document coverage results
  - File: `coverage_report.txt` (optional)
  - Content: Coverage percentages for each module
  - Content: Summary of test count by type (unit, integration, GUI)
  - Content: Notes on any intentional coverage gaps with justification

- [ ] T038 Generate final summary report
  - Summary: Total tests (expected: 150+)
  - Summary: Total coverage (expected: ≥85%)
  - Summary: Critical path coverage (models, views, forms)
  - Summary: Test execution time
  - Summary: Any gaps or concerns

---

## Success Criteria (Acceptance)

- [ ] **SC-001**: Test coverage overall is ≥85% on critical paths ✅
- [ ] **SC-002**: 100% of article view tests pass ✅
- [ ] **SC-003**: 100% of engagement view tests pass ✅
- [ ] **SC-004**: 100% of integration tests pass ✅
- [ ] **SC-005**: At least 5 integration tests exist and pass ✅
- [ ] **SC-006**: GUI tests run without @skip and pass 100% ✅
- [ ] **SC-007**: All permission tests pass ✅
- [ ] **SC-008**: Coverage report shows no critical gaps ✅
- [ ] **SC-009**: Test suite completes in <30 seconds ✅
- [ ] **SC-010**: All tests independent, can run in any order ✅

---

## Task Dependencies

### Dependency Graph

```
Phase 1 (Model Tests) - FOUNDATION
├── T001: Profile model tests
├── T002: Article model tests
├── T003: Like model tests (parallel)
├── T004: Comment model tests (parallel)
├── T005: ReadLater model tests (parallel)
└── T006: Bulletin model tests (parallel)
    └── (All Phase 1 must complete before Phase 2)

Phase 2 (Form Tests) - PARALLEL
├── T007: ArticleForm tests
├── T008: CommentForm tests (parallel)
└── T009: SignUpForm tests (parallel)
    └── (All Phase 2 must complete before Phase 3)

Phase 3 (View Tests) - PARALLEL
├── T010: ArticleCreateView tests
├── T011: ArticleUpdateView tests
├── T012: ArticleDeleteView tests
├── T013: ArticleDetailView tests (parallel)
├── T014: LikeToggleView tests
├── T015: CommentCreateView tests
├── T016: ReadLaterToggleView tests
└── T017: Auth view tests (parallel)
    └── (All Phase 3 must complete before Phase 4)

Phase 4 (Permission Tests) - PARALLEL
├── T018: ArticleOwnerMixin tests
├── T019: Self-engagement prevention tests
└── T020: Role-based access tests (parallel)
    └── (All Phase 4 must complete before Phase 5)

Phase 5 (Integration Tests) - SEQUENTIAL
├── T021: Article lifecycle tests
└── T022: Multi-user engagement tests (parallel)
    └── (All Phase 5 must complete before Phase 6)

Phase 6 (GUI Tests) - PARALLEL
├── T023: Enable GUI tests
├── T024: Page load tests (parallel)
├── T025: Form submission tests (parallel)
└── T026: Navigation tests (parallel)
    └── (All Phase 6 must complete before Phase 7)

Phase 7 (Coverage Analysis) - SEQUENTIAL
├── T027: Coverage config
├── T028: Run tests with coverage
├── T029: Generate report
├── T030: Generate HTML report
├── T031: Identify gaps
├── T032: Write gap tests
├── T033: Verify coverage
├── T034: Final test run
├── T035: Verify naming
├── T036: Verify independence
├── T037: Document results
└── T038: Generate summary
```

### Parallel Execution Opportunities

**Parallel Block 1** (Model Tests):
- T003, T004, T005, T006 can run in parallel

**Parallel Block 2** (Form Tests):
- T008, T009 can run in parallel with T007

**Parallel Block 3** (View Tests):
- T013, T014, T015, T016, T017 can run in parallel with T010, T011, T012

**Parallel Block 4** (Permission Tests):
- T019, T020 can run in parallel with T018

**Parallel Block 5** (GUI Tests):
- T024, T025, T026 can run in parallel with T023

---

**Version**: 1.0.0 | **Status**: Ready for Implementation
