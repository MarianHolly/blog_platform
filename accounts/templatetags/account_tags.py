from django import template
from accounts.models import Profile

register = template.Library()


@register.filter
def is_reader(user_profile):
    """Check if profile has reader role."""
    if not user_profile:
        return False
    return user_profile.is_reader


@register.filter
def is_writer(user_profile):
    """Check if profile has writer role."""
    if not user_profile:
        return False
    return user_profile.is_writer


@register.filter
def is_admin(user_profile):
    """Check if profile has admin role."""
    if not user_profile:
        return False
    return user_profile.is_admin


@register.simple_tag
def reader_role():
    """Return the reader role constant."""
    return 'reader'


@register.simple_tag
def writer_role():
    """Return the writer role constant."""
    return 'writer'


@register.simple_tag
def admin_role():
    """Return the admin role constant."""
    return 'admin'
