"""
Cache utilities and TTL constants for the Blog Platform application.

This module provides centralized cache timeout values to ensure consistency
across the application. TTL values are defined in seconds and should be used
throughout views and services.

Usage:
    from core.cache import CACHE_TTL_HOMEPAGE, CACHE_TTL_ARTICLE_LIST

    @method_decorator(cache_page(CACHE_TTL_HOMEPAGE), name='dispatch')
    class HomePageView(ListView):
        pass
"""

# ============================================================================
# Cache TTL Constants (all values in seconds)
# ============================================================================

# Page-level cache timeouts
CACHE_TTL_HOMEPAGE = 60 * 1  # 1 minute - HomePage is frequently updated with new articles
CACHE_TTL_ARTICLE_LIST = 60 * 5  # 5 minutes - Article lists are stable within 5 minutes
CACHE_TTL_BULLETIN_DETAIL = 60 * 10  # 10 minutes - Bulletin articles are stable

# Data cache timeouts for expensive queries
CACHE_TTL_POPULAR_BULLETINS = 60 * 2  # 2 minutes - Popular writer bulletins
CACHE_TTL_RECENT_WRITERS = 60 * 2  # 2 minutes - Recent writers list
CACHE_TTL_ARTICLE_METRICS = 60 * 5  # 5 minutes - Article counts, likes, comments
CACHE_TTL_USER_STATS = 60 * 10  # 10 minutes - User statistics (likes given, comments posted)

# Search and aggregation cache timeouts
CACHE_TTL_SEARCH_RESULTS = 60 * 3  # 3 minutes - Search results are volatile
CACHE_TTL_AGGREGATIONS = 60 * 15  # 15 minutes - Aggregation queries are expensive

# Short cache for dynamic content
CACHE_TTL_SHORT = 60 * 1  # 1 minute - For frequently changing data
CACHE_TTL_MEDIUM = 60 * 5  # 5 minutes - For moderately dynamic data
CACHE_TTL_LONG = 60 * 30  # 30 minutes - For stable, expensive queries


# ============================================================================
# Cache Key Builders
# ============================================================================

def get_cache_key(prefix: str, identifier: str) -> str:
    """Build a consistent cache key from prefix and identifier.

    Args:
        prefix: Category of cached data (e.g., 'popular_bulletins', 'user_stats')
        identifier: Specific identifier (e.g., user_id, article_id)

    Returns:
        Formatted cache key string

    Example:
        key = get_cache_key('user_stats', '123')  # Returns: 'user_stats_123'
    """
    return f"{prefix}_{identifier}"


def get_article_cache_key(article_id: int) -> str:
    """Get cache key for article data."""
    return get_cache_key('article', str(article_id))


def get_user_cache_key(user_id: int) -> str:
    """Get cache key for user statistics."""
    return get_cache_key('user_stats', str(user_id))


def get_bulletin_cache_key(bulletin_id: int) -> str:
    """Get cache key for bulletin data."""
    return get_cache_key('bulletin', str(bulletin_id))
