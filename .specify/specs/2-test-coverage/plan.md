# Implementation Plan: Comprehensive Test Coverage and Integration Tests

**Branch**: `upgrade/1-project-analysis` | **Date**: 2025-11-20 | **Spec**: `2-test-coverage/spec.md`
**Input**: Feature specification from `2-test-coverage/spec.md`

## Summary

Add comprehensive test coverage to achieve ≥85% on critical paths (models, views, business logic). Implement unit tests for all Article and engagement views, integration tests covering complete user journeys, and form validation tests. Enable GUI tests without @skip decorators and verify all permission checks, self-engagement prevention, and property logic. Existing tests at ~65-70%; target is ≥85% on critical code paths.

## Technical Context

**Language/Version**: Python 3.11+ | Django 5.2
**Primary Dependencies**: Django, Django TestCase, pytest-django, coverage (code coverage analysis)
**Storage**: PostgreSQL (test database created per TestCase)
**Testing**: Django TestCase (transaction rollback between tests), Coverage tool (coverage reports)
**Target Platform**: Web application (Linux server/Render deployment)
**Project Type**: Django monolith with 5 apps requiring comprehensive testing
**Performance Goals**: Test suite completes in <30 seconds, coverage reports generated in <5 seconds
**Constraints**: Tests must be independent and runnable in any order, database cleanup between tests
**Scale/Scope**: 100+ existing tests, targeting 150+ total tests; 40+ model fields, 15-20 views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Clarity
- ✅ **Descriptive test names**: Test names describe scenarios (e.g., `test_reader_cannot_like_own_article`)
- ✅ **Single responsibility**: Each test verifies one behavior
- ✅ **Clear test structure**: Arrange-Act-Assert pattern throughout
- ✅ **No magic values**: Test fixtures use meaningful data
- **GATE PASS**: Test code quality aligns with constitution

### Principle II: Test-Driven Development
- ✅ **Tests are executable specification**: Each requirement has corresponding test
- ✅ **Tests written for all acceptance criteria** from spec.md
- ✅ **Tests verify functionality before implementation** (guides development)
- **GATE PASS**: Feature spec provides comprehensive test scenarios

### Principle III: Testing Standards & Coverage
- ✅ **Target coverage**: ≥85% on critical paths (models, views, business logic)
- ✅ **Unit tests**: Models, form validation, property logic
- ✅ **Integration tests**: User journeys across multiple views
- ✅ **Independent tests**: Each test creates own fixtures, no test interdependencies
- ✅ **Test naming convention**: Clear scenario descriptions
- **GATE PASS**: Testing strategy aligns with constitution coverage requirements

### Principle IV: Readable Minimalistic Design
- ✅ **YAGNI**: Tests only cover documented behavior, no speculative test cases
- ✅ **Simplicity**: Use Django TestCase (built-in, simple, no heavy mocking)
- ✅ **No over-testing**: Mock external services (Cloudinary) but test business logic
- ✅ **Minimal test data**: Fixtures are simple, focused
- **GATE PASS**: Test design is minimal and purposeful

### Principle V: Consistency & Coherent UX
- ✅ **Consistent test patterns**: All model tests follow same structure
- ✅ **Consistent view test patterns**: All view tests follow same permission/context checks
- ✅ **Consistent naming**: Test methods follow same naming convention
- ✅ **Django conventions**: Use Django TestCase, fixtures, factories where appropriate
- **GATE PASS**: Tests maintain consistency with codebase patterns

**Overall Constitution Compliance**: ✅ PASS - All principles satisfied, testing strategy is comprehensive and consistent

## Project Structure

### Documentation (this feature)

```text
.specify/specs/2-test-coverage/
├── spec.md                    # Feature specification
├── plan.md                    # This file
├── checklists/requirements.md # Quality validation
└── tasks.md                   # Phase 2 (to be generated)
```

### Source Code (test structure)

```text
Django Test Suite

accounts/tests/
├── test_models.py             # Profile property tests
├── test_views.py              # Auth view tests
├── test_forms.py              # SignUpForm validation tests
├── test_permissions.py        # Permission mixin tests
└── test_integration.py        # User journey tests (if needed)

content/tests/
├── test_models.py             # Article, Bulletin model tests
├── test_views.py              # CRUD view tests (Create, Update, Delete, Detail)
├── test_forms.py              # ArticleForm validation tests
├── test_search.py             # ArticleSearch view tests
├── test_permissions.py        # ArticleOwnerMixin enforcement tests
├── test_integration.py        # Complete user journeys (NEW)
└── test_gui.py                # GUI tests (enable, remove @skip)

engagement/tests/
├── test_models.py             # Like, Comment, ReadLater model tests
├── test_views.py              # Toggle view tests
├── test_forms.py              # CommentModelForm validation tests
└── test_permissions.py        # Self-engagement prevention tests

Coverage Configuration:
├── .coveragerc               # Coverage tool configuration
└── coverage_report.html      # Generated coverage report
```

**Structure Decision**: Extend existing test structure with new test files organized by concern:
- Model tests: Fields, properties, validation, constraints
- View tests: Permission checks, status codes, context data, redirects
- Form tests: Validation, error messages, save behavior
- Integration tests: Multi-step user workflows
- GUI tests: Page rendering, form submission, navigation

No new test framework needed; use existing Django TestCase infrastructure.

## Complexity Tracking

> No Constitution violations requiring justification. Test coverage improvements are justified by quality standards and bug prevention, not overengineering.

## Implementation Tasks

### Phase 1: Model Tests (1.5 hours)

**Task 1.1**: Article Model Tests
- **File**: `content/tests/test_models.py`
- **Tests**:
  - test_article_creation_sets_default_status_draft
  - test_article_creation_sets_default_visibility_private
  - test_article_is_draft_property_returns_true_when_status_draft
  - test_article_is_published_property_returns_true_when_status_published
  - test_article_title_unique_per_bulletin (same title allowed in different bulletins)
  - test_article_title_not_unique_per_bulletin (same title fails in same bulletin)
  - test_article_save_sanitizes_content_html
  - test_article_get_absolute_url_returns_correct_path

**Task 1.2**: Profile Model Tests
- **File**: `accounts/tests/test_models.py`
- **Tests**:
  - test_reader_profile_is_reader_returns_true
  - test_reader_profile_is_writer_returns_false
  - test_reader_profile_is_admin_returns_false
  - test_writer_profile_is_writer_returns_true
  - test_writer_profile_has_bulletin
  - test_admin_profile_is_admin_returns_true

**Task 1.3**: Engagement Model Tests
- **File**: `engagement/tests/test_models.py`
- **Tests**:
  - test_like_creation_sets_timestamp
  - test_like_unique_constraint_prevents_duplicate_likes
  - test_comment_creation_stores_text
  - test_comment_unique_constraint_prevents_duplicate_comments
  - test_read_later_creation_sets_timestamp
  - test_read_later_unique_constraint_prevents_duplicate_bookmarks

---

### Phase 2: View Tests (2.5 hours)

**Task 2.1**: Article CRUD View Tests
- **File**: `content/tests/test_views.py`
- **Tests**:
  - test_article_create_view_requires_writer_role
  - test_article_create_view_creates_article_as_draft
  - test_article_create_view_sets_visibility_to_private
  - test_article_update_view_requires_article_owner
  - test_article_update_view_owner_can_edit_article
  - test_article_update_view_non_owner_receives_403
  - test_article_delete_view_owner_can_delete
  - test_article_delete_view_deletes_and_redirects_to_bulletin
  - test_article_detail_view_renders_article_content
  - test_article_detail_view_shows_engagement_counts

**Task 2.2**: Engagement View Tests
- **File**: `engagement/tests/test_views.py`
- **Tests**:
  - test_like_toggle_view_adds_like
  - test_like_toggle_view_removes_like_if_exists
  - test_like_toggle_view_prevents_self_like_returns_403
  - test_read_later_toggle_view_adds_bookmark
  - test_read_later_toggle_view_removes_bookmark_if_exists
  - test_read_later_toggle_view_prevents_self_bookmark_returns_403
  - test_comment_create_view_creates_comment
  - test_comment_update_view_updates_existing_comment

**Task 2.3**: Authentication View Tests
- **File**: `accounts/tests/test_views.py`
- **Tests**:
  - test_signup_view_creates_user_as_reader
  - test_signup_view_creates_profile_with_reader_role
  - test_login_view_authenticates_user
  - test_profile_detail_view_shows_user_info
  - test_promote_to_writer_view_requires_admin
  - test_promote_to_writer_view_changes_role

---

### Phase 3: Form Tests (1 hour)

**Task 3.1**: ArticleForm Tests
- **File**: `content/tests/test_forms.py`
- **Tests**:
  - test_article_form_requires_title
  - test_article_form_requires_content
  - test_article_form_accepts_valid_data
  - test_article_form_rejects_missing_title
  - test_article_form_rejects_missing_content
  - test_article_form_sanitizes_html_content

**Task 3.2**: CommentForm Tests
- **File**: `engagement/tests/test_forms.py`
- **Tests**:
  - test_comment_form_requires_text
  - test_comment_form_accepts_valid_data
  - test_comment_form_saves_comment_to_database

**Task 3.3**: SignUpForm Tests
- **File**: `accounts/tests/test_forms.py`
- **Tests**:
  - test_signup_form_requires_username
  - test_signup_form_requires_email
  - test_signup_form_requires_password
  - test_signup_form_password_confirmation_matches

---

### Phase 4: Integration Tests (1.5 hours)

**Task 4.1**: User Journey Tests
- **File**: `content/tests/test_integration.py` (NEW)
- **Tests**:
  - test_reader_signup_and_discover_articles_workflow
  - test_writer_create_and_publish_article_workflow
  - test_reader_like_and_comment_on_article_workflow
  - test_reader_subscribe_to_bulletin_and_view_articles
  - test_admin_evaluate_and_approve_article_workflow

Each integration test follows this pattern:
```python
def test_reader_like_and_comment_workflow(self):
    """Test complete reader engagement workflow."""
    # Setup: Create user, article
    reader = User.objects.create_user('reader', password='pass')
    writer = User.objects.create_user('writer', password='pass')
    writer.profile.role = 'writer'
    writer.profile.save()

    # Create article
    article = Article.objects.create(
        bulletin=writer.profile.bulletin,
        title='Test Article',
        content='<p>Content</p>',
        status='published'
    )

    # Act: Reader likes article
    self.client.login(username='reader', password='pass')
    response = self.client.post(reverse('like-toggle', args=[article.id]))

    # Assert: Like created
    self.assertTrue(Like.objects.filter(user=reader, article=article).exists())

    # Act: Reader comments on article
    response = self.client.post(
        reverse('comment-create', args=[article.id]),
        {'text': 'Great article!'}
    )

    # Assert: Comment created
    self.assertTrue(Comment.objects.filter(user=reader, article=article).exists())
```

---

### Phase 5: Permission Tests (1 hour)

**Task 5.1**: ArticleOwnerMixin Tests
- **File**: `content/tests/test_permissions.py`
- **Tests**:
  - test_article_owner_can_edit_own_article
  - test_non_owner_cannot_edit_article_receives_403
  - test_non_owner_cannot_delete_article_receives_403

**Task 5.2**: Self-Engagement Prevention Tests
- **File**: `engagement/tests/test_permissions.py`
- **Tests**:
  - test_user_cannot_like_own_article_returns_403
  - test_user_cannot_comment_on_own_article_returns_403
  - test_user_cannot_bookmark_own_article_returns_403

**Task 5.3**: Role-Based Access Tests
- **File**: `accounts/tests/test_permissions.py`
- **Tests**:
  - test_reader_cannot_create_article_returns_403
  - test_writer_can_create_article_returns_200
  - test_admin_can_evaluate_articles_returns_200
  - test_non_admin_cannot_evaluate_articles_returns_403

---

### Phase 6: GUI Tests (0.5 hours)

**Task 6.1**: Enable GUI Tests
- **File**: `content/tests/test_gui.py`
- **Changes**: Remove @skip decorators
- **Tests**:
  - test_homepage_loads_without_errors
  - test_article_list_displays_articles
  - test_article_detail_renders_content
  - test_create_article_form_displays
  - test_article_creation_form_submission

---

### Phase 7: Coverage Analysis & Reporting (1 hour)

**Task 7.1**: Generate Coverage Report
- **Command**: `coverage run --source='.' manage.py test && coverage report`
- **Target**: ≥85% on critical paths

**Task 7.2**: Identify Coverage Gaps
- **Report**: `coverage html` generates htmlcov/index.html
- **Review**: Identify uncovered lines in critical code paths
- **Action**: Write additional tests for gaps

**Task 7.3**: Run Full Test Suite
- **Command**: `python manage.py test`
- **Target**: 100% tests passing

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Test coverage overall is ≥85% on critical paths (models, views, business logic) ✅
- **SC-002**: 100% of article view tests pass (ArticleCreateView, UpdateView, DeleteView, DetailView) ✅
- **SC-003**: 100% of engagement view tests pass (LikeToggleView, ReadLaterToggleView, CommentForm tests) ✅
- **SC-004**: 100% of integration tests pass (complete user journey tests) ✅
- **SC-005**: At least 5 major user journey integration tests exist and pass ✅
- **SC-006**: GUI tests run without @skip decorator and pass 100% ✅
- **SC-007**: All permission-related tests pass (403 checks, 200 success checks) ✅
- **SC-008**: Coverage report shows no warnings or critical gaps in coverage ✅
- **SC-009**: Test execution time is reasonable (test suite completes in <30 seconds) ✅
- **SC-010**: All tests are independent and can run in any order without interference ✅

---

## Test Development Workflow

1. **Write tests first** (before code changes)
2. **Tests fail** (red phase - expected behavior)
3. **Implement code** to pass tests (green phase)
4. **Refactor** while keeping tests passing
5. **Measure coverage** - identify gaps
6. **Write additional tests** for uncovered paths
7. **Verify all tests pass** - run full suite
8. **Generate coverage report** - document coverage level

---

## Assumptions

- Django's TestCase class is the appropriate testing framework (built-in, handles transactions)
- Test database can be created and destroyed between test runs
- Coverage target of 85% is achievable without excessive mocking
- GUI tests should use Django TestCase + Client (not Selenium)
- Tests can be run locally and in CI/CD pipeline with same environment
- Fixtures and test data can be created in setUpTestData for efficiency
- Performance benchmarks are set reasonably for test environment (not production-grade)
- External services (Cloudinary) should be mocked, not tested

---

**Version**: 1.0.0 | **Status**: Ready for Implementation | **Next**: Run `/speckit.tasks` to generate task list
