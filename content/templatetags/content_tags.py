from django import template
from content.models import Article

register = template.Library()


# Status constants
@register.simple_tag
def draft_status():
    """Return the draft status constant."""
    return 'draft'


@register.simple_tag
def published_status():
    """Return the published status constant."""
    return 'published'


# Evaluation constants
@register.simple_tag
def pending_evaluation():
    """Return the pending evaluation constant."""
    return 'pending'


@register.simple_tag
def under_review_evaluation():
    """Return the under_review evaluation constant."""
    return 'under_review'


@register.simple_tag
def approved_evaluation():
    """Return the approved evaluation constant."""
    return 'approved'


@register.simple_tag
def rejected_evaluation():
    """Return the rejected evaluation constant."""
    return 'rejected'


# Visibility constants
@register.simple_tag
def public_visibility():
    """Return the public visibility constant."""
    return 'public'


@register.simple_tag
def private_visibility():
    """Return the private visibility constant."""
    return 'private'


# Article property filters
@register.filter
def is_draft(article):
    """Check if article is in draft status."""
    if not article:
        return False
    return article.is_draft


@register.filter
def is_approved(article):
    """Check if article evaluation is approved."""
    if not article:
        return False
    return article.is_approved


@register.filter
def is_rejected(article):
    """Check if article evaluation is rejected."""
    if not article:
        return False
    return article.is_rejected


@register.filter
def is_published_public(article):
    """Check if article is published and public."""
    if not article:
        return False
    return article.is_published_public


@register.filter
def is_published_private(article):
    """Check if article is published and private."""
    if not article:
        return False
    return article.is_published_private
