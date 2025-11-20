# Implementation Plan: Critical Fixes and Code Quality

**Branch**: `upgrade/1-project-analysis` | **Date**: 2025-11-20 | **Spec**: `1-code-quality/spec.md`
**Input**: Feature specification from `1-code-quality/spec.md`

## Summary

Fix 6 critical bugs and enforce code quality standards through database constraints, permission checks, and consistent exception handling. Replace magic strings with Django choice constants and add comprehensive docstrings to all views. Implement unique constraints on engagement models (Like, Comment, ReadLater) and bulletin-level article title uniqueness. Fix Article title uniqueness constraint, ArticleUpdateView security issue, ArticleDeleteView URL bug, and Profile role property logic. Enable caching on homepage queries and standardize view documentation.

## Technical Context

**Language/Version**: Python 3.11+ | Django 5.2
**Primary Dependencies**: Django, PostgreSQL, Django-Bleach (sanitization), Django-CKEditor5, Celery (task queue), Redis (cache/sessions)
**Storage**: PostgreSQL (primary), Cloudinary (media uploads)
**Testing**: Django TestCase, pytest-django, Selenium (GUI tests), coverage
**Target Platform**: Web application (Linux server/Render deployment)
**Project Type**: Django monolith (single codebase with 5 apps: accounts, content, engagement, blog_platform, templates)
**Performance Goals**: Homepage cache hit rate > 80%, <200ms p95 for cached requests
**Constraints**: Redis fallback to database sessions if unavailable, cache invalidation on content changes
**Scale/Scope**: ~5 Django apps, ~15-20 views, ~40+ model fields, 100+ test cases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Clarity
- ✅ **Descriptive naming**: All fixes use clear names (ArticleOwnerMixin, is_reader property, unique_together constraints)
- ✅ **Single responsibility**: Each model/view change addresses one concern
- ✅ **Magic strings/numbers eliminated**: Replacing with Django choice constants (Article.STATUS_CHOICES, Profile.ROLE_CHOICES)
- ✅ **Docstrings required**: All views MUST have comprehensive docstrings explaining permissions and behavior
- ✅ **Function length**: No changes exceed 30 lines
- **GATE PASS**: Code quality improvements align with constitution

### Principle II: Test-Driven Development
- ✅ **All requirements have test acceptance criteria** defined in spec.md
- ✅ **Database constraint tests** verify unique_together behavior
- ✅ **Permission tests** verify ArticleOwnerMixin enforcement
- ✅ **Exception handling tests** verify specific exception types caught
- **GATE PASS**: Feature spec includes test scenarios for all 12 functional requirements

### Principle III: Testing Standards & Coverage
- ✅ **Target coverage**: Existing tests at ~70%; new changes aim for ≥85% on critical paths
- ✅ **Unit tests**: Constraint behavior, property logic (is_reader/is_writer/is_admin)
- ✅ **Integration tests**: Full workflows (article creation with constraints, deletion redirect)
- ✅ **Test naming**: Clear scenario descriptions (test_reader_cannot_like_own_article pattern)
- **GATE PASS**: Testing strategy aligns with constitution

### Principle IV: Readable Minimalistic Design
- ✅ **YAGNI**: All changes are justified by critical bugs or security issues, not future-proofing
- ✅ **Simplicity**: Database constraints (unique_together) are simpler than application-level checks
- ✅ **Dead code removal**: Cache code in HomePageView will be fixed (not removed entirely)
- ✅ **Minimal dependencies**: No new external libraries required
- **GATE PASS**: Design is minimal and justified

### Principle V: Consistency & Coherent UX
- ✅ **Django conventions**: All changes follow Django patterns (CBV, ModelForm, mixins)
- ✅ **Consistent naming**: All engagement models use same pattern (user, article, unique_together)
- ✅ **Error handling**: All bare except clauses replaced with specific exception types
- ✅ **Docstring style**: All view docstrings follow Google style guide
- **GATE PASS**: Changes maintain consistency with existing codebase

**Overall Constitution Compliance**: ✅ PASS - All principles satisfied, no violations requiring justification

## Project Structure

### Documentation (this feature)

```text
.specify/specs/1-code-quality/
├── spec.md                    # Feature specification
├── plan.md                    # This file
├── checklists/requirements.md # Quality validation
└── tasks.md                   # Phase 2 (to be generated)
```

### Source Code (repository root)

```text
Django Monolith

accounts/
├── models.py                  # Profile.is_reader property fix
├── views.py                   # Add docstrings
├── mixins.py                  # Permission mixins (existing)
├── forms.py                   # SignUpForm (no changes)
└── tests/

content/
├── models.py                  # Article title unique constraint fix
├── views.py                   # ArticleDeleteView redirect fix, ArticleUpdateView security, docstrings
├── mixins.py                  # ArticleOwnerMixin (add to ArticleUpdateView)
├── forms.py                   # ArticleForm content field validation fix
└── tests/

engagement/
├── models.py                  # Like, Comment, ReadLater unique_together constraints
├── views.py                   # Existing toggle views (no changes)
├── forms.py                   # CommentModelForm (existing)
└── tests/

blog_platform/
├── settings.py                # Existing (no changes)
├── urls.py                    # Existing (no changes)
├── ckeditor_config.py         # Existing (no changes)
└── wsgi.py

templates/                      # Existing (no changes)
static/                         # Existing (no changes)
```

**Structure Decision**: Existing Django monolith structure is appropriate. All changes are within existing apps following established patterns (models, views, forms, tests). No new apps or files needed. All changes are surgical fixes to specific files identified in bug audit.

## Complexity Tracking

> No Constitution violations requiring justification. All changes are justified by critical bugs or security issues, not architectural preferences.

## Implementation Tasks

### Phase 1: Database Constraints (1 hour)

**Task 1.1**: Fix Article title uniqueness
- **File**: `content/models.py`
- **Change**: Remove `unique=True` from title field, add `unique_together = ('bulletin', 'title')` to Meta
- **Tests**: Create test_article_title_uniqueness.py
  - Same title in different bulletins succeeds
  - Same title in same bulletin fails with IntegrityError
- **Migration**: `python manage.py makemigrations`

**Task 1.2**: Add unique constraint to Like model
- **File**: `engagement/models.py`
- **Change**: Add `unique_together = ('user', 'article')` to Meta
- **Tests**: Verify duplicate like raises IntegrityError
- **Migration**: `python manage.py makemigrations`

**Task 1.3**: Add unique constraint to Comment model
- **File**: `engagement/models.py`
- **Change**: Add `unique_together = ('user', 'article')` to Meta
- **Tests**: Verify duplicate comment raises IntegrityError
- **Migration**: `python manage.py makemigrations`

**Task 1.4**: Add unique constraint to ReadLater model
- **File**: `engagement/models.py`
- **Change**: Add `unique_together = ('user', 'article')` to Meta
- **Tests**: Verify duplicate read-later raises IntegrityError
- **Migration**: `python manage.py makemigrations`

**Task 1.5**: Apply all migrations
- **Command**: `python manage.py migrate`
- **Verify**: `python manage.py sqlmigrate content` (check new constraints)

---

### Phase 2: Bug Fixes (1 hour)

**Task 2.1**: Fix Profile.is_reader property
- **File**: `accounts/models.py`
- **Current**: Returns True always
- **Fix**: Return `self.role == 'reader'`
- **Tests**:
  - Reader profile: is_reader=True, is_writer=False, is_admin=False
  - Writer profile: is_reader=False, is_writer=True, is_admin=False
  - Admin profile: is_reader=False, is_writer=False, is_admin=True

**Task 2.2**: Fix ArticleDeleteView redirect URL bug
- **File**: `content/views.py:ArticleDeleteView`
- **Current**: Uses `user.username` (non-existent attribute)
- **Fix**: Use `self.object.bulletin.owner.user.username`
- **Tests**: Deleting article redirects to bulletin owner's profile

**Task 2.3**: Fix ArticleForm content field validation
- **File**: `content/forms.py:ArticleForm`
- **Current**: `required=False` but validates as required
- **Fix**: Change to `required=True` in field definition
- **Tests**: Creating article without content fails validation

**Task 2.4**: Add ArticleOwnerMixin to ArticleUpdateView
- **File**: `content/views.py:ArticleUpdateView`
- **Change**: Add `ArticleOwnerMixin` to class inheritance
- **Tests**:
  - Article owner can edit article
  - Non-owner receives 403 Forbidden

---

### Phase 3: Code Quality Standards (1.5 hours)

**Task 3.1**: Replace magic strings with choice constants
- **Files**: All view files, template references
- **Changes**:
  - Article status: Use `Article.STATUS_CHOICES` instead of 'draft', 'published'
  - Profile role: Use `Profile.ROLE_CHOICES` instead of 'reader', 'writer', 'admin'
  - Article evaluation: Use `Article.EVALUATION_CHOICES` instead of 'pending', 'under_review', 'approved', 'rejected'
- **Tests**: Verify no hardcoded strings exist (grep search)
- **Locations**:
  - `accounts/models.py`: Profile.role choices
  - `content/models.py`: Article.status, Article.evaluation, Article.visibility choices
  - All view files and templates using these values

**Task 3.2**: Add docstrings to all view classes
- **File**: `accounts/views.py`, `content/views.py`, `engagement/views.py`
- **Format**: Google style docstring with Permissions, Query Optimization, Returns sections
- **Views requiring docstrings**:
  - accounts: LoginView, SignUpView, ProfileDetailView, PromoteToWriterView, PromoteToAdminView
  - content: ArticleCreateView, ArticleUpdateView, ArticleDeleteView, ArticleDetailView, ArticleListView, BulletinDetailView, HomePageView, ArticleSearchView, ArticleEvaluationView, SubscriptionToggleView, VisibilityToggleView
  - engagement: LikeToggleView, ReadLaterToggleView, CommentCreateView
- **Example**:
```python
def get_queryset(self):
    """Prefetch related objects for efficient querying.

    Permissions:
    - Any authenticated user can view articles
    - Only writers can create/edit their own articles
    - Only admins can evaluate articles

    Query Optimization:
    - select_related('bulletin__owner'): Fetch author in single query
    - prefetch_related('comments', 'likes'): Optimize engagement counts

    Returns:
    - Queryset of published articles only
    - Ordered by creation date (newest first)
    """
```

---

### Phase 4: Exception Handling (0.5 hours)

**Task 4.1**: Fix bare except clauses
- **Search**: `grep -r "except:" .` (find all bare except clauses)
- **Files**: All Python files
- **Fixes**:
  - `except:` → `except Exception as e:` (general case)
  - Specific cases: `except IntegrityError:`, `except ObjectDoesNotExist:`, `except ValidationError:`
- **Tests**: Verify specific exception types are caught

---

### Phase 5: Caching (0.5 hours)

**Task 5.1**: Enable cache in HomePageView
- **File**: `content/views.py:HomePageView`
- **Current**: Cache code exists but not used
- **Fix**:
  - Uncomment/enable `@cache_page(60)` decorator
  - Or manually use `cache.get('popular_bulletins')` in get_queryset()
- **Tests**:
  - First page load: Database queried, result cached
  - Second load within 60s: Cache used (no database query)
  - Verify cache hit via logging or timing

---

### Phase 6: Testing & Verification (1 hour)

**Task 6.1**: Create/update tests for all changes
- **Files**: All test files in accounts/tests/, content/tests/, engagement/tests/
- **Test coverage**: ≥85% on critical paths
- **Run**: `python manage.py test` (all tests pass)

**Task 6.2**: Generate coverage report
- **Command**: `coverage run --source='.' manage.py test && coverage report`
- **Target**: ≥85% on critical paths

**Task 6.3**: Code review checklist
- ✅ All 12 functional requirements implemented
- ✅ All tests passing (100% pass rate)
- ✅ No bare except clauses remain
- ✅ All views have docstrings
- ✅ No magic strings in code
- ✅ Database constraints verified
- ✅ Coverage ≥85% on critical paths

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 12 functional requirements implemented and tested ✅
- **SC-002**: Test suite passes 100% (no failing tests) ✅
- **SC-003**: All ArticleDeleteView deletions redirect correctly (0% error rate) ✅
- **SC-004**: ArticleUpdateView rejects non-owner updates (100% security coverage) ✅
- **SC-005**: Database constraints prevent 100% of duplicate engagement entries ✅
- **SC-006**: No hardcoded magic strings in code (100% replaced with constants) ✅
- **SC-007**: All view classes (8+) have clear, complete docstrings ✅
- **SC-008**: Homepage cache hit rate measurably improves (second load faster) ✅
- **SC-009**: Code review identifies zero bare exception clauses ✅
- **SC-010**: New developer can understand any view's purpose from docstring alone ✅

---

## Assumptions

- Article deletion is a standard Django DeleteView operation
- Bulletin-owner relationship is already properly set up (confirmed in data model review)
- Django choice constants are the standard pattern for this codebase
- View docstrings should follow Google style guide
- Cache duration (60 seconds) is acceptable for homepage data freshness
- Developer has access to local Django development environment for testing
- Migration rollback is possible if issues discovered during testing

---

**Version**: 1.0.0 | **Status**: Ready for Implementation | **Next**: Run `/speckit.tasks` to generate task list
