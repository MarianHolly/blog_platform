from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from accounts.models import Profile
from content.models import Article, Bulletin

class SearchTests(TestCase):
    def setUp(self):
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.create(user=writer_user, role='writer')
        bulletin = Bulletin.objects.create(owner=writer_profile, title='Test', slug='test')

        Article.objects.create(
            title='Bytie a čas',
            description='Heideggerov magnum opus',
            content='<p>Heidegger</p>',
            bulletin=bulletin,
            status='published',
            visibility='public'
        )

        Article.objects.create(
            title='Stratený čas',
            description='Proustove myšlienky',
            content='<p>Proust</p>',
            bulletin=bulletin,
            status='published',
            visibility='public'
        )

    def test_search_finds_articles_by_title(self):
        """Test search finds articles by title"""
        response = self.client.get(reverse('article_search'), {'q': 'Bytie'})
        self.assertContains(response, 'Bytie a čas')
        self.assertNotContains(response, 'Stratený čas')

    def test_search_finds_articles_by_description(self):
        """Test search finds articles by description"""
        response = self.client.get(reverse('article_search'), {'q': 'myšlienky'})
        self.assertContains(response, 'Proustove myšlienky')

    def test_search_empty_query(self):
        """Test search with empty query"""
        response = self.client.get(reverse('article_search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Proustove myšlienky')

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get(reverse('article_search'), {'q': 'neexistujúce'})
        self.assertContains(response, 'Žiadne výsledky')