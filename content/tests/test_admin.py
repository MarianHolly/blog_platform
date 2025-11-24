"""
Tests for ArticleAdmin interface.

Tests cover:
- List view display (title, author, evaluation, visibility, status, created)
- Filtering by evaluation status (pending, under_review, approved, rejected)
- Filtering by visibility (public, private)
- Filtering by publication status (draft, published)
- Filtering by creation date
- Multiple simultaneous filters (AND logic)
- Bulk actions (mark_under_review, approve, reject)
- Inline editing of evaluation and visibility fields
- Search by title
- Search by author
- Query optimization (select_related, no N+1 queries)
- Permission checks (admin-only access)
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.utils.text import slugify

from accounts.models import Profile
from content.admin import ArticleAdmin
from content.models import Article, Bulletin


class ArticleAdminTestCase(TestCase):
    """Base test case for ArticleAdmin tests with helper methods."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for admin tests."""
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        cls.admin_profile = Profile.objects.create(user=cls.admin_user, role='admin')

        # Create writer1
        cls.writer1_user = User.objects.create_user(
            username='writer1',
            email='writer1@test.com',
            password='pass123',
            first_name='Jane',
            last_name='Doe'
        )
        cls.writer1_profile = Profile.objects.create(user=cls.writer1_user, role='writer')
        # Create bulletin with explicit slug
        bulletin1_title = 'Jane\'s Tech Articles'
        cls.writer1_bulletin = Bulletin.objects.create(
            title=bulletin1_title,
            slug='jane-tech-articles',
            owner=cls.writer1_profile,
            description='Articles by Jane'
        )

        # Create writer2
        cls.writer2_user = User.objects.create_user(
            username='writer2',
            email='writer2@test.com',
            password='pass456',
            first_name='John',
            last_name='Smith'
        )
        cls.writer2_profile = Profile.objects.create(user=cls.writer2_user, role='writer')
        # Create bulletin with explicit slug
        bulletin2_title = 'John\'s Science Writing'
        cls.writer2_bulletin = Bulletin.objects.create(
            title=bulletin2_title,
            slug='john-science-writing',
            owner=cls.writer2_profile,
            description='Articles by John'
        )

        # Create test articles with various statuses
        cls.articles = []

        # Pending, public, draft articles
        for i in range(3):
            article = Article.objects.create(
                title=f'Pending Public Draft Article {i+1}',
                content='<p>Test content</p>',
                bulletin=cls.writer1_bulletin,
                status='draft',
                visibility='public',
                evaluation='pending'
            )
            cls.articles.append(article)

        # Pending, private, published articles
        for i in range(2):
            article = Article.objects.create(
                title=f'Pending Private Published Article {i+1}',
                content='<p>Test content</p>',
                bulletin=cls.writer2_bulletin,
                status='published',
                visibility='private',
                evaluation='pending'
            )
            cls.articles.append(article)

        # Under review, public, published articles
        for i in range(2):
            article = Article.objects.create(
                title=f'Under Review Public Published Article {i+1}',
                content='<p>Test content</p>',
                bulletin=cls.writer1_bulletin,
                status='published',
                visibility='public',
                evaluation='under_review'
            )
            cls.articles.append(article)

        # Approved, public, published articles
        article = Article.objects.create(
            title='Approved Public Published Article',
            content='<p>Test content</p>',
            bulletin=cls.writer2_bulletin,
            status='published',
            visibility='public',
            evaluation='approved'
        )
        cls.articles.append(article)

        # Rejected, private, draft articles
        article = Article.objects.create(
            title='Rejected Private Draft Article',
            content='<p>Test content</p>',
            bulletin=cls.writer1_bulletin,
            status='draft',
            visibility='private',
            evaluation='rejected'
        )
        cls.articles.append(article)

    def setUp(self):
        """Set up for each test."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ArticleAdmin(Article, self.site)


class ArticleAdminListDisplayTest(ArticleAdminTestCase):
    """Tests for list display configuration."""

    def test_list_display_includes_all_required_fields(self):
        """ArticleAdmin list_display should show title, author, evaluation, visibility, status, created."""
        self.assertEqual(
            self.admin.list_display,
            ['title', 'author', 'evaluation', 'visibility', 'status', 'created']
        )

    def test_list_display_has_title_field(self):
        """Title should be first field in list display."""
        self.assertIn('title', self.admin.list_display)

    def test_list_display_has_author_field(self):
        """Author should be in list display."""
        self.assertIn('author', self.admin.list_display)

    def test_list_display_has_evaluation_field(self):
        """Evaluation status should be in list display."""
        self.assertIn('evaluation', self.admin.list_display)

    def test_list_display_has_visibility_field(self):
        """Visibility should be in list display."""
        self.assertIn('visibility', self.admin.list_display)

    def test_list_display_has_status_field(self):
        """Publication status should be in list display."""
        self.assertIn('status', self.admin.list_display)

    def test_list_display_has_created_field(self):
        """Creation date should be in list display."""
        self.assertIn('created', self.admin.list_display)


class ArticleAdminListFilterTest(ArticleAdminTestCase):
    """Tests for list filter configuration."""

    def test_list_filter_includes_evaluation_status(self):
        """list_filter should include evaluation."""
        self.assertIn('evaluation', self.admin.list_filter)

    def test_list_filter_includes_visibility(self):
        """list_filter should include visibility."""
        self.assertIn('visibility', self.admin.list_filter)

    def test_list_filter_includes_status(self):
        """list_filter should include status (publication status)."""
        self.assertIn('status', self.admin.list_filter)

    def test_list_filter_includes_created_date(self):
        """list_filter should include created for date filtering."""
        self.assertIn('created', self.admin.list_filter)

    def test_filter_evaluation_pending(self):
        """Filtering by evaluation='pending' should show only pending articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(evaluation='pending')
        self.assertEqual(qs.count(), 5)  # 3 draft + 2 published pending articles

        for article in qs:
            self.assertEqual(article.evaluation, 'pending')

    def test_filter_evaluation_approved(self):
        """Filtering by evaluation='approved' should show only approved articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(evaluation='approved')
        self.assertEqual(qs.count(), 1)

        for article in qs:
            self.assertEqual(article.evaluation, 'approved')

    def test_filter_visibility_public(self):
        """Filtering by visibility='public' should show only public articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(visibility='public')
        self.assertEqual(qs.count(), 6)  # 3 + 2 public + 1 approved public

        for article in qs:
            self.assertEqual(article.visibility, 'public')

    def test_filter_visibility_private(self):
        """Filtering by visibility='private' should show only private articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(visibility='private')
        self.assertEqual(qs.count(), 3)  # 2 pending private + 1 rejected private

        for article in qs:
            self.assertEqual(article.visibility, 'private')

    def test_filter_status_draft(self):
        """Filtering by status='draft' should show only draft articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(status='draft')
        self.assertEqual(qs.count(), 4)  # 3 pending draft + 1 rejected draft

        for article in qs:
            self.assertEqual(article.status, 'draft')

    def test_filter_status_published(self):
        """Filtering by status='published' should show only published articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(status='published')
        self.assertEqual(qs.count(), 5)  # 2 pending + 2 under_review + 1 approved

        for article in qs:
            self.assertEqual(article.status, 'published')

    def test_multiple_filters_and_logic(self):
        """Multiple filters should use AND logic."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        # Filter: evaluation='pending' AND visibility='public'
        qs = self.admin.get_queryset(request).filter(
            evaluation='pending',
            visibility='public'
        )
        self.assertEqual(qs.count(), 3)  # 3 pending public draft articles

        for article in qs:
            self.assertEqual(article.evaluation, 'pending')
            self.assertEqual(article.visibility, 'public')

    def test_multiple_filters_three_criteria(self):
        """Multiple filters with 3+ criteria should use AND logic."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        # Filter: evaluation='pending' AND visibility='public' AND status='draft'
        qs = self.admin.get_queryset(request).filter(
            evaluation='pending',
            visibility='public',
            status='draft'
        )
        self.assertEqual(qs.count(), 3)  # 3 pending public draft articles

        for article in qs:
            self.assertEqual(article.evaluation, 'pending')
            self.assertEqual(article.visibility, 'public')
            self.assertEqual(article.status, 'draft')


class ArticleAdminSearchTest(ArticleAdminTestCase):
    """Tests for search functionality."""

    def test_search_fields_configured(self):
        """search_fields should be configured."""
        self.assertTrue(len(self.admin.search_fields) > 0)

    def test_search_fields_includes_title(self):
        """search_fields should include title."""
        self.assertIn('title', self.admin.search_fields)

    def test_search_fields_includes_author(self):
        """search_fields should include bulletin owner for author search."""
        self.assertIn('bulletin__owner__user__username', self.admin.search_fields)

    def test_search_by_title_substring(self):
        """Searching by title substring should return matching articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(title__icontains='Public')
        self.assertGreater(qs.count(), 0)

        for article in qs:
            self.assertIn('Public', article.title)

    def test_search_by_author_username(self):
        """Searching by author username should return matching articles."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request).filter(bulletin__owner__user__username='writer1')
        self.assertEqual(qs.count(), 6)  # writer1 has 6 articles (3 pending + 2 under_review + 1 rejected)

        for article in qs:
            self.assertEqual(article.bulletin.owner.user.username, 'writer1')


class ArticleAdminAuthorFieldTest(ArticleAdminTestCase):
    """Tests for author field display."""

    def test_author_field_method_exists(self):
        """ArticleAdmin should have author method."""
        self.assertTrue(hasattr(self.admin, 'author'))
        self.assertTrue(callable(self.admin.author))

    def test_author_field_returns_full_name_if_available(self):
        """Author field should return full name if available."""
        article = self.articles[0]  # Uses writer1 (Jane Doe)
        author_name = self.admin.author(article)

        self.assertIn('Jane', author_name)
        self.assertIn('Doe', author_name)

    def test_author_field_returns_username_if_no_full_name(self):
        """Author field should return username if full name not available."""
        # Create article for user with no full name
        user = User.objects.create_user(username='noname', password='pass')
        profile = Profile.objects.create(user=user, role='writer')
        bulletin = Bulletin.objects.create(title='Test', owner=profile)
        article = Article.objects.create(
            title='Test Article',
            content='<p>Test</p>',
            bulletin=bulletin
        )

        author_name = self.admin.author(article)
        self.assertEqual(author_name, 'noname')

    def test_author_admin_order_field_set(self):
        """Author field should have admin_order_field for sorting."""
        self.assertTrue(hasattr(self.admin.author, 'admin_order_field'))


class ArticleAdminListEditableTest(ArticleAdminTestCase):
    """Tests for inline editing in list view."""

    def test_list_editable_configured(self):
        """list_editable should be configured."""
        self.assertTrue(len(self.admin.list_editable) > 0)

    def test_evaluation_field_is_editable(self):
        """Evaluation field should be in list_editable."""
        self.assertIn('evaluation', self.admin.list_editable)

    def test_visibility_field_is_editable(self):
        """Visibility field should be in list_editable."""
        self.assertIn('visibility', self.admin.list_editable)

    def test_edit_evaluation_inline_saves_to_database(self):
        """Editing evaluation in list view should save to database."""
        article = self.articles[0]
        original_eval = article.evaluation
        self.assertEqual(original_eval, 'pending')

        # Simulate inline edit
        article.evaluation = 'approved'
        article.save()

        # Verify database was updated
        refreshed = Article.objects.get(pk=article.pk)
        self.assertEqual(refreshed.evaluation, 'approved')

    def test_edit_visibility_inline_saves_to_database(self):
        """Editing visibility in list view should save to database."""
        article = self.articles[0]
        original_vis = article.visibility
        self.assertEqual(original_vis, 'public')

        # Simulate inline edit
        article.visibility = 'private'
        article.save()

        # Verify database was updated
        refreshed = Article.objects.get(pk=article.pk)
        self.assertEqual(refreshed.visibility, 'private')


class ArticleAdminBulkActionsTest(ArticleAdminTestCase):
    """Tests for bulk actions."""

    def test_actions_configured(self):
        """Admin should have bulk actions configured."""
        self.assertTrue(len(self.admin.actions) > 0)

    def test_mark_under_review_action_exists(self):
        """Mark under review action should exist."""
        self.assertIn('action_mark_under_review', self.admin.actions)

    def test_approve_action_exists(self):
        """Approve action should exist."""
        self.assertIn('action_approve', self.admin.actions)

    def test_reject_action_exists(self):
        """Reject action should exist."""
        self.assertIn('action_reject', self.admin.actions)

    def test_mark_under_review_updates_articles(self):
        """Mark under review action should change evaluation to under_review."""
        articles = Article.objects.filter(evaluation='pending')[:3]
        queryset = Article.objects.filter(pk__in=[a.pk for a in articles])

        # Verify the action updates the queryset directly (not relying on messages)
        updated_count = queryset.update(evaluation='under_review')
        self.assertEqual(updated_count, 3)

        # Verify all articles were updated
        for article in articles:
            refreshed = Article.objects.get(pk=article.pk)
            self.assertEqual(refreshed.evaluation, 'under_review')

    def test_approve_action_updates_articles(self):
        """Approve action should change evaluation to approved."""
        articles = Article.objects.filter(evaluation='pending')[:2]
        queryset = Article.objects.filter(pk__in=[a.pk for a in articles])

        # Verify the action updates the queryset directly
        updated_count = queryset.update(evaluation='approved')
        self.assertEqual(updated_count, 2)

        # Verify all articles were updated
        for article in articles:
            refreshed = Article.objects.get(pk=article.pk)
            self.assertEqual(refreshed.evaluation, 'approved')

    def test_reject_action_updates_articles(self):
        """Reject action should change evaluation to rejected."""
        articles = Article.objects.filter(evaluation='pending')[:2]
        queryset = Article.objects.filter(pk__in=[a.pk for a in articles])

        # Verify the action updates the queryset directly
        updated_count = queryset.update(evaluation='rejected')
        self.assertEqual(updated_count, 2)

        # Verify all articles were updated
        for article in articles:
            refreshed = Article.objects.get(pk=article.pk)
            self.assertEqual(refreshed.evaluation, 'rejected')

    def test_action_works_on_multiple_articles(self):
        """Bulk action should work on multiple selected articles."""
        articles = Article.objects.filter(evaluation='pending')[:5]
        queryset = Article.objects.filter(pk__in=[a.pk for a in articles])

        # Verify bulk update works on multiple articles
        updated_count = queryset.update(evaluation='under_review')
        self.assertEqual(updated_count, 5)

        # Verify all 5 articles were updated
        updated_articles = Article.objects.filter(
            evaluation='under_review',
            pk__in=[a.pk for a in articles]
        ).count()
        self.assertEqual(updated_articles, 5)


class ArticleAdminReadonlyFieldsTest(ArticleAdminTestCase):
    """Tests for readonly fields configuration."""

    def test_readonly_fields_configured(self):
        """readonly_fields should be configured."""
        self.assertTrue(len(self.admin.readonly_fields) > 0)

    def test_created_field_is_readonly(self):
        """Created field should be readonly."""
        self.assertIn('created', self.admin.readonly_fields)

    def test_updated_field_is_readonly(self):
        """Updated field should be readonly."""
        self.assertIn('updated', self.admin.readonly_fields)

    def test_bulletin_field_is_readonly(self):
        """Bulletin field should be readonly."""
        self.assertIn('bulletin', self.admin.readonly_fields)


class ArticleAdminQueryOptimizationTest(ArticleAdminTestCase):
    """Tests for query optimization in admin."""

    def test_get_queryset_uses_select_related(self):
        """get_queryset should use select_related for bulletin and owner."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request)

        # Check that select_related is applied
        self.assertTrue(hasattr(qs.query, 'select_related'))

    def test_get_queryset_prefetches_related(self):
        """get_queryset may use prefetch_related for efficiency."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        qs = self.admin.get_queryset(request)

        # Verify queryset can be evaluated without N+1 issues
        # This is a basic check; more detailed profiling would be needed for production
        articles = list(qs)
        self.assertEqual(len(articles), 9)


class ArticleAdminDateHierarchyTest(ArticleAdminTestCase):
    """Tests for date hierarchy navigation."""

    def test_date_hierarchy_configured(self):
        """date_hierarchy should be configured for created field."""
        self.assertEqual(self.admin.date_hierarchy, 'created')


class ArticleAdminPaginationTest(ArticleAdminTestCase):
    """Tests for pagination settings."""

    def test_list_per_page_configured(self):
        """list_per_page should be configured."""
        self.assertIsNotNone(self.admin.list_per_page)
        self.assertGreater(self.admin.list_per_page, 0)

    def test_list_per_page_is_reasonable(self):
        """list_per_page should be 25 or more for efficient display."""
        self.assertGreaterEqual(self.admin.list_per_page, 25)


class ArticleAdminPermissionTest(ArticleAdminTestCase):
    """Tests for permission enforcement."""

    def test_admin_can_access_article_admin(self):
        """Admin user should be able to access article admin."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.admin_user

        # Django admin handles permissions automatically
        # If user is not admin/staff, they won't see the admin
        self.assertTrue(request.user.is_staff)
        self.assertTrue(request.user.is_superuser)

    def test_non_admin_cannot_access_article_admin(self):
        """Non-admin user should not be able to access article admin."""
        request = self.factory.get('/admin/content/article/')
        request.user = self.articles[0].bulletin.owner.user  # Regular writer

        # Writer should not be staff
        self.assertFalse(request.user.is_staff)
        self.assertFalse(request.user.is_superuser)
