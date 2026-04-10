"""
Centralized constants for the Blog Platform application.

This module defines all role, status, evaluation, and visibility constants
to provide a single source of truth and prevent magic strings throughout
the codebase.

Using constants instead of magic strings provides:
- Type safety and IDE autocomplete
- Easy validation against allowed values
- Single point of change if values need to be updated
- Consistency across views, models, forms, and templates
"""

# ============================================================================
# PROFILE ROLES
# ============================================================================
"""User role choices for Profile model."""

ROLE_READER = 'reader'
ROLE_WRITER = 'writer'
ROLE_ADMIN = 'admin'

ROLE_CHOICES = [
    (ROLE_READER, 'Reader'),
    (ROLE_WRITER, 'Writer'),
    (ROLE_ADMIN, 'Administrator'),
]

ROLE_DISPLAY = {
    ROLE_READER: 'Reader',
    ROLE_WRITER: 'Writer',
    ROLE_ADMIN: 'Administrator',
}


# ============================================================================
# ARTICLE STATUS
# ============================================================================
"""Publication status for articles."""

STATUS_DRAFT = 'draft'
STATUS_PUBLISHED = 'published'

STATUS_CHOICES = [
    (STATUS_DRAFT, 'Draft'),
    (STATUS_PUBLISHED, 'Published'),
]

STATUS_DISPLAY = {
    STATUS_DRAFT: 'Draft',
    STATUS_PUBLISHED: 'Published',
}


# ============================================================================
# ARTICLE VISIBILITY
# ============================================================================
"""Visibility/privacy setting for articles."""

VISIBILITY_PUBLIC = 'public'
VISIBILITY_PRIVATE = 'private'

VISIBILITY_CHOICES = [
    (VISIBILITY_PUBLIC, 'Public'),
    (VISIBILITY_PRIVATE, 'Private'),
]

VISIBILITY_DISPLAY = {
    VISIBILITY_PUBLIC: 'Public',
    VISIBILITY_PRIVATE: 'Private',
}


# ============================================================================
# ARTICLE EVALUATION (MODERATION)
# ============================================================================
"""Content moderation/evaluation status for articles."""

EVALUATION_PENDING = 'pending'
EVALUATION_UNDER_REVIEW = 'under_review'
EVALUATION_APPROVED = 'approved'
EVALUATION_REJECTED = 'rejected'

EVALUATION_CHOICES = [
    (EVALUATION_PENDING, 'Pending Review'),
    (EVALUATION_UNDER_REVIEW, 'Under Review'),
    (EVALUATION_APPROVED, 'Approved'),
    (EVALUATION_REJECTED, 'Rejected'),
]

EVALUATION_DISPLAY = {
    EVALUATION_PENDING: 'Pending Review',
    EVALUATION_UNDER_REVIEW: 'Under Review',
    EVALUATION_APPROVED: 'Approved',
    EVALUATION_REJECTED: 'Rejected',
}

# Evaluation states that allow article visibility to readers
APPROVED_EVALUATIONS = {EVALUATION_APPROVED}

# Evaluation states that hide article from readers
REJECTED_EVALUATIONS = {EVALUATION_REJECTED}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_role_display(role: str) -> str:
    """Get human-readable display name for a role."""
    return ROLE_DISPLAY.get(role, 'Unknown')


def get_status_display(status: str) -> str:
    """Get human-readable display name for an article status."""
    return STATUS_DISPLAY.get(status, 'Unknown')


def get_visibility_display(visibility: str) -> str:
    """Get human-readable display name for visibility setting."""
    return VISIBILITY_DISPLAY.get(visibility, 'Unknown')


def get_evaluation_display(evaluation: str) -> str:
    """Get human-readable display name for evaluation status."""
    return EVALUATION_DISPLAY.get(evaluation, 'Unknown')


def is_valid_role(role: str) -> bool:
    """Check if a role value is valid."""
    return role in {choice[0] for choice in ROLE_CHOICES}


def is_valid_status(status: str) -> bool:
    """Check if a status value is valid."""
    return status in {choice[0] for choice in STATUS_CHOICES}


def is_valid_visibility(visibility: str) -> bool:
    """Check if a visibility value is valid."""
    return visibility in {choice[0] for choice in VISIBILITY_CHOICES}


def is_valid_evaluation(evaluation: str) -> bool:
    """Check if an evaluation value is valid."""
    return evaluation in {choice[0] for choice in EVALUATION_CHOICES}
