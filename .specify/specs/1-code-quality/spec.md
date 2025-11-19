# Feature Specification: Critical Fixes and Code Quality

**Feature Branch**: `1-code-quality`
**Created**: 2025-11-19
**Status**: In Review
**Input**: Code audit findings from CODE_AUDIT_REPORT.md

## User Scenarios & Testing

### User Story 1 - Developer Experiences Fewer Silent Failures (Priority: P1)

When developers modify code and run tests, they should get clear error messages instead of silent failures. This improves debugging experience and catches problems early.

**Why this priority**: Critical for code maintainability and developer productivity. Silent failures mask bugs.

**Independent Test**: Can be verified by: (1) Attempting to save invalid article forms and checking error messages appear in logs, (2) Running test suite and verifying all exceptions are properly caught and logged, (3) Checking that no "bare except" patterns exist in codebase.

**Acceptance Scenarios**:

1. **Given** a developer saves an article with an exception in content sanitization, **When** the form processes, **Then** specific exception type is caught and logged with full context (not silently ignored)
2. **Given** a developer reviews codebase, **When** searching for exception handling, **Then** no bare `except:` clauses exist (all exceptions are specific)
3. **Given** tests run, **When** an unexpected error occurs, **Then** the error is logged and visible in test output (not hidden)

---

### User Story 2 - Code is More Readable and Self-Documenting (Priority: P1)

Developers reading the codebase should understand the purpose and constraints of each view without needing external documentation.

**Why this priority**: Critical for onboarding and maintenance. Code clarity is a sign of professionalism.

**Independent Test**: Can be verified by: (1) All view classes have docstrings explaining permissions and behavior, (2) Magic strings (status values, roles) are replaced with named constants, (3) New developer can understand view purpose from docstring alone.

**Acceptance Scenarios**:

1. **Given** a developer opens `ArticleDetailView`, **When** they read the class docstring, **Then** they understand: which users can view articles, what query optimizations are used, and whether articles are cached
2. **Given** a developer searches for "draft" in code, **When** they look at results, **Then** all results reference `Article.STATUS_CHOICES` or `Article.is_draft` property (not magic string)
3. **Given** code review comments ask "why use this pattern", **When** developer points to docstring or inline comment, **Then** rationale is clear

---

### User Story 3 - Database Constraints Prevent Invalid Data (Priority: P1)

Users' engagement (likes, comments, bookmarks) should follow business rules at the database level, preventing duplicate entries even if application code is bypassed.

**Why this priority**: Critical for data integrity. Prevents hard-to-debug inconsistencies.

**Independent Test**: Can be verified by: (1) Running migration and checking unique constraints exist in database schema, (2) Attempting to create duplicate like/comment via direct database query and observing constraint violation, (3) Test suite includes tests that verify constraint behavior.

**Acceptance Scenarios**:

1. **Given** a user has already liked an article, **When** database constraint is checked, **Then** `UNIQUE(user_id, article_id)` constraint prevents duplicate like entry
2. **Given** a user has already commented on an article, **When** attempting to insert second comment for same user/article, **Then** database raises IntegrityError due to unique constraint
3. **Given** migration is applied, **When** database schema is inspected, **Then** Like, ReadLater, and Comment models all have unique_together constraints

---

### User Story 4 - Article Title Uniqueness Allows Cross-Bulletin Reuse (Priority: P2)

Writers should be able to use the same article title across different bulletins (their own or other writers' bulletins), as long as titles are unique within each bulletin.

**Why this priority**: High importance for usability. Prevents writers from being locked out of good titles.

**Independent Test**: Can be verified by: (1) Creating two articles with same title in different bulletins succeeds, (2) Creating two articles with same title in same bulletin fails, (3) Database constraints enforce per-bulletin uniqueness.

**Acceptance Scenarios**:

1. **Given** Writer A has article titled "Technology in 2025", **When** Writer B creates article with same title in their bulletin, **Then** article creation succeeds
2. **Given** Writer A has article titled "Technology in 2025" in their bulletin, **When** Writer A tries to create another article with same title in same bulletin, **Then** article creation fails with constraint violation
3. **Given** old global unique constraint is removed, **When** migration is applied, **Then** new `unique_together('bulletin', 'title')` constraint is in place

---

### User Story 5 - Cache Actually Improves Performance (Priority: P2)

The homepage should use cached data for expensive queries, reducing database load and improving load time.

**Why this priority**: Important for performance. Dead cache code provides no benefit.

**Independent Test**: Can be verified by: (1) Homepage loads, cache key is checked first, (2) Database is not queried if cache hit occurs, (3) Performance improves between first load (cache miss) and second load (cache hit).

**Acceptance Scenarios**:

1. **Given** homepage is loaded first time, **When** cache is empty, **Then** database is queried and popular bulletins are retrieved, cached result is stored
2. **Given** homepage is loaded second time within cache duration, **When** cache is checked, **Then** cached result is used and database is NOT queried
3. **Given** cache is inspected during request, **When** monitoring tools check, **Then** cache hit is recorded (cache is actually being used)

---

### User Story 6 - Security: Writers Cannot Edit Others' Articles (Priority: P1)

A writer should only be able to edit articles in their own bulletin. This is enforced at the view level with proper ownership verification.

**Why this priority**: Critical security issue. Prevents cross-bulletin content modification.

**Independent Test**: Can be verified by: (1) Writer A can edit own article (success), (2) Writer B cannot edit Writer A's article (403 Forbidden), (3) View has ArticleOwnerMixin to enforce this check.

**Acceptance Scenarios**:

1. **Given** Writer A owns an article, **When** Writer A accesses article edit view, **Then** form is displayed and article can be edited
2. **Given** Writer B does NOT own an article, **When** Writer B attempts to access article edit view via URL, **Then** 403 Forbidden response is returned
3. **Given** view is inspected, **When** ArticleOwnerMixin is checked, **Then** mixin is applied before other processing

---

### User Story 7 - Form Validation is Clear and Consistent (Priority: P2)

Article content field should have clear validation rules. If field is required, UI should indicate it clearly.

**Why this priority**: Medium importance for UX. Prevents confusion about what's mandatory.

**Independent Test**: Can be verified by: (1) ArticleForm marks content as required, (2) Creating article without content fails with validation error, (3) No contradictory required/validation signals.

**Acceptance Scenarios**:

1. **Given** ArticleForm is initialized, **When** content field is inspected, **Then** `required=True` is set
2. **Given** user submits article form without content, **When** form is validated, **Then** validation error is raised indicating content is required
3. **Given** form is rendered in template, **When** user views form, **Then** visual indicators (asterisk, aria-required) show content is mandatory

---

### User Story 8 - Profile Properties Accurately Reflect User Role (Priority: P2)

Profile model properties should correctly identify user roles without logic errors.

**Why this priority**: Medium importance. Properties are used for role checking; inaccuracy causes bugs.

**Independent Test**: Can be verified by: (1) Reader profile has `is_reader=True`, `is_writer=False`, `is_admin=False`, (2) Writer profile has `is_reader=False`, `is_writer=True`, `is_admin=False`, (3) Admin profile has `is_reader=False`, `is_writer=False`, `is_admin=True`.

**Acceptance Scenarios**:

1. **Given** a profile with role='reader', **When** `is_reader` property is accessed, **Then** it returns True
2. **Given** a profile with role='writer', **When** `is_writer` property is accessed, **Then** it returns True
3. **Given** a profile with role='admin', **When** `is_admin` property is accessed, **Then** it returns True

---

### Edge Cases

- What happens when article is deleted and URL redirect tries to access deleted bulletin owner? (Fixed: use bulletin relationship, not non-existent user relationship)
- What happens if two requests try to create same like simultaneously? (Fixed: database unique constraint prevents duplicates)
- What happens if article title is updated to match existing title in same bulletin? (Handled: unique_together constraint prevents this)
- What happens if developer creates bare except clause again in future? (Mitigated: code review checks will catch this against constitution)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST fix ArticleDeleteView URL reverse bug (use `bulletin.owner.username` instead of `user.username`)
- **FR-002**: System MUST prevent writers from editing articles in other bulletins (add ArticleOwnerMixin to ArticleUpdateView)
- **FR-003**: System MUST catch all exceptions explicitly; no bare `except:` clauses allowed (replace with specific exception types)
- **FR-004**: System MUST enforce database constraints preventing duplicate likes (add `unique_together = ('user', 'article')` to Like model)
- **FR-005**: System MUST enforce database constraints preventing duplicate read-later entries (add `unique_together = ('user', 'article')` to ReadLater model)
- **FR-006**: System MUST enforce database constraints preventing duplicate comments (add `unique_together = ('user', 'article')` to Comment model)
- **FR-007**: System MUST make article titles unique per-bulletin, not globally (change from `unique=True` to `unique_together = ('bulletin', 'title')`)
- **FR-008**: System MUST use cached values for popular bulletins and recent writers instead of querying database every time (fix HomePageView cache logic)
- **FR-009**: System MUST replace all magic strings (status values, roles, evaluation states) with Django choice constants
- **FR-010**: System MUST add comprehensive docstrings to all view classes explaining permissions, behavior, and query optimizations
- **FR-011**: System MUST fix ArticleForm content field validation (either remove `required=False` or remove validation)
- **FR-012**: System MUST fix Profile.is_reader property (return correct boolean based on role, not always True)

### Key Entities

- **Article**: Models published content with status (draft/published), evaluation state (pending/under_review/approved/rejected), visibility (public/private)
- **Bulletin**: Writing space for each writer; articles belong to bulletins
- **Like**: User engagement with articles; must be unique per user per article
- **Comment**: User feedback on articles; must be unique per user per article
- **ReadLater**: User bookmarking; must be unique per user per article
- **Profile**: User role information (reader/writer/admin)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 12 functional requirements are implemented and verified by test cases
- **SC-002**: Test suite passes 100% (no failing tests due to changes)
- **SC-003**: All ArticleDeleteView deletions complete successfully (0% error rate)
- **SC-004**: ArticleUpdateView rejects non-owner updates (100% security coverage)
- **SC-005**: Database constraints prevent 100% of duplicate engagement entries
- **SC-006**: Magic string replacement covers 100% of status/role/evaluation hardcoded values
- **SC-007**: All view classes (8+) have clear, complete docstrings
- **SC-008**: Homepage cache hit rate measurably improves (second load faster than first)
- **SC-009**: Code review identifies zero bare exception clauses
- **SC-010**: New developer can understand any view's purpose from docstring alone

---

## Assumptions

- Article deletion is a standard Django DeleteView operation
- Bulletin-owner relationship is already properly set up (confirmed in data model review)
- Django choice constants are the standard pattern for this codebase
- View docstrings should follow Google or NumPy style guide
- Cache duration (60 seconds) is acceptable for homepage data freshness
- Developer has access to local Django development environment for testing
- Migration rollback is possible if issues discovered during testing

---

**Version**: 1.0.0 | **Status**: Ready for Planning
