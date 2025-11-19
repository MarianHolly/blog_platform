# Blog Platform Constitution

**Project**: Blog Platform (Django CMS with Role-Based Permissions)
**Scope**: Code quality standards, development discipline, and professional practices for portfolio showcase

## Core Principles

### I. Code Quality & Clarity

Every line of code is read far more often than it is written. Code MUST prioritize clarity and
maintainability over brevity.

**Non-Negotiable Requirements**:
- Variable/function names MUST be descriptive and intent-revealing (e.g., `get_published_articles()` not `get_posts()`)
- Functions MUST have a single, well-defined responsibility
- Maximum function length: 30 lines; if longer, break into smaller functions
- Comments MUST explain *why*, not *what* the code does (the code explains what)
- No magic numbers; extract to named constants with clear purpose
- Avoid nested conditionals deeper than 2 levels; use early returns and guards
- Complex logic MUST be extracted into named, testable helper functions

**Rationale**: Clarity demonstrates professionalism. Readable code is maintainable code, reduces bugs,
and enables team collaboration. Clear code is the hallmark of mid-level developers who understand
that code is communication.

---

### II. Test-Driven Development (TDD)

TDD is mandatory for all new features and bug fixes. Tests MUST be written before implementation
and MUST fail before code is written.

**Non-Negotiable Requirements**:
- Write test first → Test MUST fail (Red) → Implement code (Green) → Refactor (Refactor)
- Tests MUST be part of the implementation contract, not an afterthought
- No feature ships without passing tests
- All tests MUST be committed alongside code; never skip test coverage
- User stories and acceptance criteria MUST have corresponding test cases

**Rationale**: TDD ensures code correctness, provides living documentation through tests,
and gives confidence in refactoring. This discipline separates junior from mid-level developers.

---

### III. Testing Standards & Coverage

Tests are the only executable specification. All tests MUST meet strict quality standards.

**Non-Negotiable Requirements**:
- Unit tests: Test a single function/method in isolation; use mocks for dependencies
- Integration tests: Test feature workflows across components (e.g., user story completion)
- Contract tests (optional): Document API expectations for critical endpoints
- Each test MUST have clear Arrange-Act-Assert structure
- Test names MUST describe the scenario being tested (e.g., `test_reader_cannot_like_own_article()`)
- No interdependent tests; each test MUST be independently executable
- Coverage target: ≥85% for critical paths (models, business logic, views); ≥70% overall
- Flaky tests (non-deterministic results) MUST be fixed immediately; do not skip
- Test assertions MUST be specific; avoid generic assertions like `assertEqual(result, True)`

**Rationale**: High-quality tests provide confidence, catch regressions early, and serve as
documentation. Clear test standards ensure consistency and prevent technical debt.

---

### IV. Readable Minimalistic Design

Systems MUST be simple by default. Complexity MUST be justified and documented.

**Non-Negotiable Requirements**:
- YAGNI (You Aren't Gonna Need It): Do not build features or abstractions preemptively
- Avoid over-engineering; start with simplest design that solves the problem
- Each design pattern, utility class, or abstraction MUST solve a real, current problem
- If complexity is justified, document in a comment explaining *why* it exists
- Prefer composition over inheritance; avoid deep class hierarchies (max 2 levels)
- Remove dead code, unused imports, and unused parameters immediately
- Minimize external dependencies; add only libraries that solve critical problems
- UI/UX MUST be intuitive; prefer familiar patterns over novelty

**Rationale**: Simple code is easier to understand, test, and maintain. It reduces cognitive
load and makes onboarding faster. Minimalism shows discipline and maturity in decision-making.

---

### V. Consistency & Coherent UX

The platform MUST feel cohesive. All code, UI, and workflows MUST follow consistent patterns.

**Non-Negotiable Requirements**:
- Follow Django conventions: models → forms → views → templates → URLs
- Use consistent naming across the codebase (e.g., all article list views named `ArticleListView`)
- All templates MUST share consistent CSS classes (Tailwind utility convention)
- All API responses MUST follow the same structure (consistent error format, response envelope if used)
- All forms MUST have the same validation behavior and error message style
- Permission checks MUST use mixins consistently (ReaderRequiredMixin, WriterRequiredMixin, etc.)
- All timestamps MUST be timezone-aware and stored in UTC
- All URLs MUST follow REST conventions: resources as nouns, HTTP methods as verbs
- UI patterns MUST be consistent: buttons, form layouts, modals, alerts all follow same design

**Rationale**: Consistency reduces cognitive load for users and developers. It demonstrates
professionalism and makes the platform feel polished. Coherent UX builds trust; inconsistency
creates frustration and is a sign of unmaintained code.

---

## Quality Standards

### Code Review Requirements

All code MUST pass review before merge:
- At least one other developer reviews (self-review acceptable for solo projects, but not preferred)
- Reviewer MUST verify: TDD compliance, test coverage ≥ threshold, naming clarity, no dead code
- Feedback MUST reference specific principles from this constitution
- All comments MUST be resolved before merge

### Complexity Justification

If any code violates these principles (e.g., function > 30 lines, coverage < threshold),
the violation MUST be explicitly documented with rationale. Examples:
- **Why**: Complex regex for article slug validation; no simpler alternative exists
- **Justified**: Yes, document as comment in code
- **Accepted Risk**: Slightly lower test coverage (82% vs 85%) due to integration test complexity

## Development Workflow

### Feature Implementation Workflow

1. **Test-First**: Write test cases from spec (test MUST fail)
2. **Implementation**: Write code to pass tests (green)
3. **Refactor**: Improve code clarity while keeping tests passing
4. **Code Review**: Verify compliance with constitution principles
5. **Merge**: All checks pass, tests pass, coverage acceptable

### Commit Standards

- Commits MUST be atomic (one logical change per commit)
- Commit messages MUST describe *why*, not just *what*
- Commit messages MUST reference user story/issue if applicable
- No `print()` debugging or commented-out code in commits

### Definition of Done (User Story)

A user story is ONLY "done" when:
- ✅ All acceptance criteria from spec are tested and passing
- ✅ Test coverage meets or exceeds threshold (≥85% for new code)
- ✅ All tests are passing (unit, integration, contract if applicable)
- ✅ Code review approval obtained
- ✅ Code merged to main/dev branch
- ✅ No outstanding TODOs or FIXMEs in code (or explicitly documented in principle violation)

## Governance

### Constitution Authority

This constitution supersedes all other coding guidelines, style guides, and informal practices.
All decisions about code, testing, and architecture MUST be evaluated against these principles.

### Amendments

Amendments to this constitution require:
1. Clear rationale documenting why the principle must change
2. Impact assessment: which existing code/practices are affected?
3. Migration plan: how will existing code transition to new principle?
4. Version bump (MAJOR for removals, MINOR for additions, PATCH for clarifications)
5. Update all dependent templates (spec-template.md, tasks-template.md, plan-template.md)
6. Commit message: `docs: amend constitution to vX.Y.Z (principle additions/changes)`

### Compliance Verification

- **PR Reviews**: Reviewers MUST reference constitution principles in feedback
- **Continuous Practice**: These principles apply to ALL code, not just feature branches
- **Technical Decisions**: When faced with multiple approaches, choose the one that best
  aligns with these principles. Document trade-offs if a principle must be violated.
- **Portfolio Value**: This constitution demonstrates professional development practices;
  adherence to it proves mid-level (or higher) capability

### Portfolio Context

This project serves as a portfolio showcase for a Python/Django developer. Adherence to these
principles demonstrates:
- **Technical Maturity**: Understanding TDD, clean code, and testing discipline
- **Professional Standards**: Consistency, clarity, and thoughtful design decisions
- **Production Mindset**: Code is written for teams and for the future, not just to "make it work"
- **Communication Skills**: Code clarity and commit messages show ability to express intent

---

**Version**: 2.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
