# Blog Platform - Improvement Implementation Checklist

**Created**: 2025-11-19
**Constitution Version**: 2.0.0
**Target Grade**: A (95/100) from current B+ (85/100)

---

## Phase 1: Critical Fixes (Week 1) ⚠️ MUST DO
**Effort**: 3-4 hours | **Impact**: Security & Data Integrity

### 1. Fix ArticleDeleteView URL Reverse Bug
- [ ] Open `content/views.py` line 176
- [ ] Change: `self.object.user.username` → `self.object.bulletin.owner.username`
- [ ] Test: Try deleting an article, verify redirect works
- [ ] Commit: `fix: correct ArticleDeleteView URL reverse for bulletin owner`

**Estimated Time**: 5 min

---

### 2. Add ArticleOwnerMixin to ArticleUpdateView
- [ ] Open `content/views.py` line 155
- [ ] Add `ArticleOwnerMixin` to class inheritance: `class ArticleUpdateView(ArticleOwnerMixin, WriterRequiredMixin, UpdateView):`
- [ ] Test: Try editing another user's article (should get 403)
- [ ] Run: `python manage.py test content.tests`
- [ ] Commit: `fix: add ownership verification to ArticleUpdateView`

**Estimated Time**: 5 min

---

### 3. Replace Bare Except Clauses
- [ ] Open `content/forms.py` lines 42 and 94
- [ ] Replace both bare `except:` blocks with specific exception handling
- [ ] Add import: `from django.core.exceptions import ValidationError`
- [ ] Add import: `import logging` and `logger = logging.getLogger(__name__)`
- [ ] Replace bare except at line 42:
  ```python
  try:
      self.instance.save()
  except ValidationError as e:
      self.add_error(None, str(e))
  except Exception as e:
      logger.error(f"Failed to save instance: {e}", exc_info=True)
      self.add_error(None, "Failed to save. Please try again.")
  ```
- [ ] Replace bare except at line 94 with same pattern
- [ ] Test: `python manage.py test content.tests`
- [ ] Commit: `fix: replace bare except clauses with specific exception handling`

**Estimated Time**: 15 min

---

### 4. Add Unique Constraints to Engagement Models
- [ ] Open `engagement/models.py`
- [ ] Add `unique_together` to Like model:
  ```python
  class Meta:
      unique_together = ('user', 'article')
  ```
- [ ] Add `unique_together` to ReadLater model:
  ```python
  class Meta:
      unique_together = ('user', 'article')
  ```
- [ ] Add `unique_together` to Comment model:
  ```python
  class Meta:
      unique_together = ('user', 'article')
  ```
- [ ] Create migration: `python manage.py makemigrations engagement`
- [ ] Review migration file
- [ ] Apply migration: `python manage.py migrate`
- [ ] Test: `python manage.py test engagement.tests`
- [ ] Commit: `fix: add unique constraints to Like, ReadLater, and Comment models`

**Estimated Time**: 30 min

---

### 5. Fix HomePageView Cache Logic
- [ ] Open `content/views.py` lines 39-50
- [ ] Restructure to actually use cached values:
  ```python
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)

      # Try cache first
      popular_bulletins = cache.get('popular_bulletins')
      if popular_bulletins is None:
          popular_bulletins = Bulletin.objects.filter(
              articles__visibility='public'
          ).annotate(
              article_count=Count('articles')
          ).order_by('-article_count')[:10]
          cache.set('popular_bulletins', popular_bulletins, 60)

      recent_writers = cache.get('recent_writers')
      if recent_writers is None:
          recent_writers = Profile.objects.filter(
              role='writer'
          ).order_by('-created_at')[:10]
          cache.set('recent_writers', recent_writers, 60)

      context['popular_bulletins'] = popular_bulletins
      context['recent_writers'] = recent_writers
      return context
  ```
- [ ] Test: Visit homepage, check cache is being used (Django debug toolbar or logs)
- [ ] Commit: `perf: fix HomePageView cache logic to actually use cached values`

**Estimated Time**: 20 min

---

## Phase 2: Code Quality (Week 2) ✅ SHOULD DO
**Effort**: 6-8 hours | **Impact**: Professionalism & Clarity

### 6. Replace Magic Strings with Django Choices
- [ ] Open `content/models.py`
- [ ] Add choice constants at top of Article model:
  ```python
  class Article(models.Model):
      STATUS_CHOICES = [
          ('draft', 'Draft'),
          ('published', 'Published'),
      ]
      EVALUATION_CHOICES = [
          ('pending', 'Pending Evaluation'),
          ('under_review', 'Under Review'),
          ('approved', 'Approved'),
          ('rejected', 'Rejected'),
      ]
      VISIBILITY_CHOICES = [
          ('public', 'Public'),
          ('private', 'Private'),
      ]

      status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
      # ... (repeat for evaluation and visibility)
  ```
- [ ] Open `accounts/models.py`
- [ ] Add choice constants to Profile model:
  ```python
  class Profile(models.Model):
      ROLE_CHOICES = [
          ('reader', 'Reader'),
          ('writer', 'Writer'),
          ('admin', 'Administrator'),
      ]
      role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
  ```
- [ ] Search and replace all hardcoded strings:
  - `'draft'` → use `Article.STATUS_CHOICES[0][0]` or create properties
  - `'published'` → use properties/constants
  - Similar for roles, evaluation states
- [ ] Create properties for readability:
  ```python
  @property
  def is_draft(self):
      return self.status == 'draft'

  @property
  def is_published(self):
      return self.status == 'published'
  ```
- [ ] Update views to use new constants
- [ ] Update tests to use new constants
- [ ] Test: `python manage.py test`
- [ ] Commit: `refactor: replace magic strings with Django choice constants`

**Estimated Time**: 2-3 hours

---

### 7. Add View Docstrings
- [ ] Open `content/views.py`
- [ ] Add docstring to every view class following this pattern:
  ```python
  class ArticleDetailView(DetailView):
      """
      Display a single article with engagement options.

      Permissions: Published articles visible to all readers (if public or subscribed).
      Draft articles visible only to writer and admins.

      Query optimization: Uses select_related() and prefetch_related().
      """
  ```
- [ ] Repeat for all views in `accounts/views.py` and `engagement/views.py`
- [ ] Check: `python manage.py check`
- [ ] Commit: `docs: add comprehensive docstrings to all view classes`

**Estimated Time**: 45 min

---

### 8. Fix ArticleForm Content Field Validation
- [ ] Open `content/forms.py`
- [ ] Line 36: Change `self.fields['content'].required = False` → `True`
- [ ] Lines 50-60: Remove or update clean_content() method (it's now redundant)
- [ ] Update test to verify content is required
- [ ] Test: `python manage.py test content.tests.test_forms`
- [ ] Commit: `fix: clarify ArticleForm content field as required`

**Estimated Time**: 10 min

---

### 9. Fix Article Title Uniqueness Constraint
- [ ] Open `content/models.py` line 52
- [ ] Remove global `unique=True` from title field:
  ```python
  title = models.CharField(max_length=255)  # Remove unique=True
  ```
- [ ] Add `unique_together` to Meta class:
  ```python
  class Meta:
      unique_together = ('bulletin', 'title')
  ```
- [ ] Create migration: `python manage.py makemigrations`
- [ ] Review and apply: `python manage.py migrate`
- [ ] Update test that checks title uniqueness
- [ ] Test: `python manage.py test content.tests.test_models`
- [ ] Commit: `fix: change Article title uniqueness to per-bulletin instead of global`

**Estimated Time**: 30 min

---

### 10. Fix Profile.is_reader Property
- [ ] Open `accounts/models.py` line 40
- [ ] Fix property:
  ```python
  @property
  def is_reader(self):
      return self.role == 'reader'

  @property
  def is_writer(self):
      return self.role == 'writer'

  @property
  def is_admin(self):
      return self.role == 'admin'
  ```
- [ ] Test: `python manage.py test accounts.tests`
- [ ] Commit: `fix: correct Profile role checking properties`

**Estimated Time**: 5 min

---

## Phase 3: Testing Expansion (Week 3) 🎯 SHOULD DO
**Effort**: 5-6 hours | **Impact**: TDD Discipline & Coverage

### 11. Create Comprehensive View Tests
- [ ] Create file: `content/tests/test_views.py`
- [ ] Add ArticleCreateViewTest class with tests for:
  - [ ] test_writer_can_create_article
  - [ ] test_reader_cannot_create_article
  - [ ] test_article_defaults_draft_private
  - [ ] test_article_content_sanitized
  - [ ] test_invalid_form_shows_errors
- [ ] Add ArticleUpdateViewTest class with tests for:
  - [ ] test_owner_can_update_article
  - [ ] test_non_owner_cannot_update_article
  - [ ] test_update_changes_slug
  - [ ] test_admin_can_evaluate_article
- [ ] Add ArticleDeleteViewTest class
- [ ] Create `engagement/tests/test_views.py`
- [ ] Add LikeToggleViewTest class
- [ ] Add ReadLaterToggleViewTest class
- [ ] Run tests: `python manage.py test`
- [ ] Check coverage: `coverage run --source='.' manage.py test && coverage report`
- [ ] Target: ≥85% on critical paths
- [ ] Commit: `test: add comprehensive view tests for articles and engagement`

**Estimated Time**: 3-4 hours

---

### 12. Create Integration Tests
- [ ] Create file: `content/tests/test_integration.py`
- [ ] Add UserJourneyTest class with tests for:
  - [ ] test_reader_to_subscriber_journey (find → subscribe → read → comment)
  - [ ] test_writer_article_publication_journey (create → draft → publish → evaluate)
  - [ ] test_admin_moderation_workflow (review → approve/reject)
  - [ ] test_engagement_complete_workflow (like → comment → bookmark)
- [ ] Each test should be independent and verify complete user flow
- [ ] Run tests: `python manage.py test content.tests.test_integration`
- [ ] Verify coverage: `coverage report`
- [ ] Commit: `test: add integration tests for user workflows`

**Estimated Time**: 2-3 hours

---

### 13. Enable GUI Tests
- [ ] Open `content/tests/test_gui.py`
- [ ] Remove `@skip` decorators from test methods
- [ ] Update tests to use Django TestCase with Client (not Selenium)
- [ ] OR: Set up Selenium properly with headless browser
- [ ] Create test configuration in `pytest.ini` or Django test settings
- [ ] Run: `python manage.py test content.tests.test_gui`
- [ ] Verify tests pass
- [ ] Commit: `test: enable GUI tests and refactor for proper execution`

**Estimated Time**: 1-2 hours

---

## Phase 4: Professional Enhancements (Weeks 4-5) 🌟 CAN DO
**Effort**: 12-15 hours total | **Impact**: Portfolio Standout

### Choose 2-3 of the following:

#### Enhancement A: Add Signal-Based Automation (2-3 hours)
- [ ] Create `accounts/signals.py`
- [ ] Add post_save signal to auto-create Bulletin when user becomes writer
- [ ] Register signals in `accounts/apps.py`
- [ ] Write tests for signal behavior
- [ ] Commit: `feat: add signal-based bulletin auto-creation for new writers`

**Estimated Time**: 2-3 hours

---

#### Enhancement B: Add Logging Infrastructure (3-4 hours)
- [ ] Update `blog_platform/settings.py` with comprehensive LOGGING config
- [ ] Create `logs/` directory
- [ ] Replace all `print()` statements with `logger.info()`/`logger.debug()`
- [ ] Create logger in each app: `logger = logging.getLogger(__name__)`
- [ ] Test logging works: `python manage.py runserver`
- [ ] Verify logs written to file
- [ ] Commit: `feat: add structured logging infrastructure`

**Estimated Time**: 3-4 hours

---

#### Enhancement C: Add API Layer (DRF) (8-10 hours)
- [ ] Install: `pip install djangorestframework`
- [ ] Create `api/` app
- [ ] Create serializers for Article, Bulletin, Profile, Comment
- [ ] Create ViewSets for each model
- [ ] Create API URLs with DefaultRouter
- [ ] Add API documentation (DRF browsable API)
- [ ] Add authentication and permissions
- [ ] Write API tests
- [ ] Commit: `feat: add Django REST Framework API layer`

**Estimated Time**: 8-10 hours

---

#### Enhancement D: Admin Interface Customization (3-4 hours)
- [ ] Open `content/admin.py`
- [ ] Customize ArticleAdmin with list_display, list_filter, search_fields
- [ ] Customize BulletinAdmin with article/subscriber counts
- [ ] Customize Profile admin with role display and filters
- [ ] Add admin actions (bulk approve/reject articles)
- [ ] Test admin interface works
- [ ] Commit: `feat: customize Django admin interface for content management`

**Estimated Time**: 3-4 hours

---

#### Enhancement E: Performance Monitoring (4-5 hours)
- [ ] Create `blog_platform/middleware.py` with PerformanceLoggingMiddleware
- [ ] Install: `pip install django-debug-toolbar`
- [ ] Configure debug toolbar for development
- [ ] Add slow query detection
- [ ] Run performance tests
- [ ] Document optimization tips
- [ ] Commit: `feat: add performance monitoring middleware and debug tools`

**Estimated Time**: 4-5 hours

---

## Quick Reference: File Locations

```
blog_platform/
├── accounts/
│   ├── models.py          (Fix: is_reader, add ROLE_CHOICES)
│   ├── views.py           (Add docstrings)
│   └── tests.py           (Already good)
│
├── content/
│   ├── models.py          (Add CHOICE constants, fix title uniqueness)
│   ├── views.py           (Fix ArticleUpdateView, ArticleDeleteView, cache, add docstrings)
│   ├── forms.py           (Fix bare excepts, content field validation)
│   └── tests/
│       ├── test_models.py (Already exists)
│       ├── test_forms.py  (Already exists)
│       ├── test_views.py  (CREATE NEW - add view tests)
│       ├── test_integration.py  (CREATE NEW - add integration tests)
│       └── test_gui.py    (Enable existing tests)
│
├── engagement/
│   ├── models.py          (Add unique_together constraints)
│   ├── views.py           (Add docstrings)
│   └── tests/
│       ├── test_models.py (Already exists)
│       └── test_views.py  (CREATE NEW - add toggle view tests)
│
└── blog_platform/
    ├── settings.py        (Add LOGGING config if doing logging enhancement)
    ├── middleware.py      (CREATE NEW if adding performance monitoring)
    └── urls.py            (No changes needed)
```

---

## Commit Message Template

Use this template for all commits to show professional practice:

```
<type>: <subject>

<body>

Fixes: #<issue-number> (if applicable)
```

**Types**: fix, feat, refactor, test, docs, perf, style

**Example**:
```
fix: add ownership verification to ArticleUpdateView

Prevent writers from editing articles in other bulletins by adding
ArticleOwnerMixin to ArticleUpdateView. This was a security issue
where any writer could modify any article.

Fixes constitution violation: "Content Ownership" principle
```

---

## Testing Commands

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test content
python manage.py test engagement
python manage.py test accounts

# Run specific test file
python manage.py test content.tests.test_views

# Run specific test class
python manage.py test content.tests.test_models.ArticleModelTest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Opens htmlcov/index.html

# Run specific test with verbose output
python manage.py test content.tests.test_views -v 2
```

---

## Progress Tracking

### Phase 1: Critical Fixes
- [ ] Article delete URL bug (5 min)
- [ ] Article update ownership (5 min)
- [ ] Bare except clauses (15 min)
- [ ] Engagement unique constraints (30 min)
- [ ] Cache logic (20 min)
**Total Phase 1**: ~75 min (1.25 hours)

### Phase 2: Code Quality
- [ ] Magic strings → choices (2-3 hours)
- [ ] View docstrings (45 min)
- [ ] Form validation (10 min)
- [ ] Title uniqueness (30 min)
- [ ] is_reader property (5 min)
**Total Phase 2**: ~4 hours

### Phase 3: Testing
- [ ] View tests (3-4 hours)
- [ ] Integration tests (2-3 hours)
- [ ] Enable GUI tests (1-2 hours)
**Total Phase 3**: ~6-9 hours

### Phase 4: Enhancements (choose 2-3)
- [ ] Signals (2-3 hours)
- [ ] Logging (3-4 hours)
- [ ] API (8-10 hours)
- [ ] Admin (3-4 hours)
- [ ] Performance (4-5 hours)
**Total Phase 4**: 12-15 hours (pick what you want)

---

## Success Criteria

### Minimum (Grade B+ → A-)
- ✅ All Phase 1 critical fixes complete
- ✅ Phase 2 code quality complete
- ✅ Test coverage ≥85% on critical paths
- ✅ All tests passing

### Target (Grade A)
- ✅ All of Minimum
- ✅ All Phase 3 testing complete
- ✅ View and integration tests passing
- ✅ Complete documentation/docstrings

### Excellent (Grade A+)
- ✅ All of Target
- ✅ 1-2 Phase 4 enhancements complete
- ✅ API layer OR admin customization OR signals

---

**Start Date**: _________
**Target Completion**: Week 3 for A grade
**Actual Completion**: _________

Good luck! This checklist will take you from B+ to A in 3 weeks. 🚀
