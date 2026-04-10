"""
Content sanitization utilities for the Blog Platform.

This module provides centralized HTML sanitization to prevent XSS attacks.
All user-generated HTML content should be sanitized through these functions
to ensure consistent security policy across the application.

Usage:
    from core.sanitization import sanitize_html

    content = sanitize_html(user_input)
"""

from bleach import clean


# ============================================================================
# Sanitization Configuration
# ============================================================================

# Allowed HTML tags for rich text content (CKEditor5 output)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'a', 'img', 'blockquote', 'code', 'pre', 'hr',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'div', 'span', 'figure', 'figcaption'
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    '*': ['class', 'style'],
    'table': ['border', 'cellpadding', 'cellspacing'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}


# ============================================================================
# Sanitization Functions
# ============================================================================

def sanitize_html(content: str, tags: list = None, attributes: dict = None, strip: bool = True) -> str:
    """Sanitize HTML content to prevent XSS attacks.

    This function uses the bleach library to remove potentially dangerous HTML
    and only allow specific safe tags and attributes defined in the configuration.

    Args:
        content: Raw HTML string to sanitize
        tags: List of allowed HTML tags (defaults to ALLOWED_TAGS)
        attributes: Dict of allowed attributes per tag (defaults to ALLOWED_ATTRIBUTES)
        strip: If True, removes disallowed tags; if False, escapes them

    Returns:
        Sanitized HTML string safe to display in templates

    Example:
        >>> dirty = '<p>Safe</p><script>alert("XSS")</script>'
        >>> clean_html = sanitize_html(dirty)
        >>> print(clean_html)
        '<p>Safe</p>&lt;script&gt;alert("XSS")&lt;/script&gt;'
    """
    if not content:
        return content

    if tags is None:
        tags = ALLOWED_TAGS
    if attributes is None:
        attributes = ALLOWED_ATTRIBUTES

    return clean(content, tags=tags, attributes=attributes, strip=strip)


def sanitize_article_content(content: str) -> str:
    """Sanitize article content from CKEditor with rich text formatting.

    This is the standard sanitization for Article.content field which may
    contain formatted text from the CKEditor5 WYSIWYG editor.

    Args:
        content: Raw HTML from CKEditor

    Returns:
        Sanitized HTML safe for display
    """
    return sanitize_html(content)
