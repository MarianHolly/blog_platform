import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from faker import Faker

from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Comment, Like, ReadLater


class Command(BaseCommand):
    help = 'Generate realistic mock data for the blog platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=30,
            help='Number of users to create (default: 30)'
        )
        parser.add_argument(
            '--articles',
            type=int,
            default=50,
            help='Number of articles to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating'
        )

    def handle(self, *args, **options):
        fake = Faker()

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared'))

        num_users = options['users']
        num_articles = options['articles']

        # Calculate distributions
        num_writers = int(num_users * 0.2)  # 20% writers
        num_readers = num_users - num_writers

        self.stdout.write(f'Generating {num_users} users ({num_writers} writers, {num_readers} readers)...')

        # Create readers
        readers = []
        for i in range(num_readers):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )

            profile = user.profile
            profile.role = 'reader'
            profile.biography = fake.text(max_nb_chars=200) if random.random() > 0.3 else ''
            profile.save()

            readers.append(profile)

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1} readers...')

        self.stdout.write(self.style.SUCCESS(f'Created {num_readers} readers'))

        # Create writers with bulletins
        writers = []
        bulletins = []
        for i in range(num_writers):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )

            profile = user.profile
            profile.role = 'writer'
            profile.biography = fake.text(max_nb_chars=300)
            profile.save()

            # Create bulletin
            bulletin_title = fake.catch_phrase()
            bulletin = Bulletin.objects.create(
                owner=profile,
                title=bulletin_title,
                slug=slugify(bulletin_title),
                description=fake.text(max_nb_chars=200)
            )

            writers.append(profile)
            bulletins.append(bulletin)

            if (i + 1) % 5 == 0:
                self.stdout.write(f'  Created {i + 1} writers with bulletins...')

        self.stdout.write(self.style.SUCCESS(f'Created {num_writers} writers with bulletins'))

        # Create subscriptions (readers subscribe to random bulletins)
        self.stdout.write('Creating subscriptions...')
        subscription_count = 0
        for reader in readers:
            # Each reader subscribes to 2-5 random bulletins
            num_subs = random.randint(2, min(5, len(bulletins)))
            selected_bulletins = random.sample(bulletins, num_subs)

            for bulletin in selected_bulletins:
                Subscription.objects.get_or_create(
                    subscriber=reader,
                    bulletin=bulletin
                )
                subscription_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {subscription_count} subscriptions'))

        # Create articles
        self.stdout.write(f'Generating {num_articles} articles...')
        articles = []

        for i in range(num_articles):
            bulletin = random.choice(bulletins)

            title = fake.sentence(nb_words=6).rstrip('.')

            # Generate article content (multiple paragraphs)
            paragraphs = [f'<p>{fake.paragraph(nb_sentences=random.randint(3, 8))}</p>'
                         for _ in range(random.randint(5, 15))]
            content = '\n'.join(paragraphs)

            # 80% published, 20% draft
            status = 'published' if random.random() > 0.2 else 'draft'

            # 90% public, 10% private
            visibility = 'public' if random.random() > 0.1 else 'private'

            # Random evaluation
            if status == 'published':
                evaluation = random.choice(['approved', 'approved', 'approved', 'pending'])
            else:
                evaluation = 'pending'

            article = Article.objects.create(
                bulletin=bulletin,
                title=title,
                slug=slugify(title),
                subtitle=fake.sentence() if random.random() > 0.3 else '',
                description=fake.text(max_nb_chars=150) if random.random() > 0.5 else '',
                content=content,
                status=status,
                visibility=visibility,
                evaluation=evaluation
            )

            articles.append(article)

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1} articles...')

        published_articles = [a for a in articles if a.status == 'published']
        self.stdout.write(self.style.SUCCESS(f'Created {num_articles} articles ({len(published_articles)} published)'))

        # Create engagement (likes, comments, bookmarks)
        self.stdout.write('Creating engagement data...')

        like_count = 0
        comment_count = 0
        bookmark_count = 0

        for article in published_articles:
            # Random number of likes (0-15)
            num_likes = random.randint(0, min(15, len(readers)))
            for reader in random.sample(readers, num_likes):
                Like.objects.get_or_create(author=reader, article=article)
                like_count += 1

            # Random number of comments (0-5)
            num_comments = random.randint(0, min(5, len(readers)))
            for reader in random.sample(readers, num_comments):
                try:
                    Comment.objects.create(
                        author=reader,
                        article=article,
                        content=fake.text(max_nb_chars=200)
                    )
                    comment_count += 1
                except:
                    # Skip if already commented (unique constraint)
                    pass

            # Random bookmarks (0-8)
            num_bookmarks = random.randint(0, min(8, len(readers)))
            for reader in random.sample(readers, num_bookmarks):
                ReadLater.objects.get_or_create(author=reader, article=article)
                bookmark_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {like_count} likes, {comment_count} comments, {bookmark_count} bookmarks'
        ))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== DATA GENERATION COMPLETE ==='))
        self.stdout.write(f'Users: {num_users} ({num_readers} readers, {num_writers} writers)')
        self.stdout.write(f'Bulletins: {len(bulletins)}')
        self.stdout.write(f'Articles: {num_articles} ({len(published_articles)} published)')
        self.stdout.write(f'Subscriptions: {subscription_count}')
        self.stdout.write(f'Likes: {like_count}')
        self.stdout.write(f'Comments: {comment_count}')
        self.stdout.write(f'Bookmarks: {bookmark_count}')
        self.stdout.write('\nDefault password for all users: password123')
