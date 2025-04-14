from django.db.models import Model, CASCADE, CharField, TextField, DateTimeField, ManyToManyField, OneToOneField, \
    SlugField

from accounts.models import Profile


# Create your models here.
class Bulletin(Model):
    owner = OneToOneField(Profile, on_delete=CASCADE, related_name='bulletin')
    title = CharField(max_length=255)
    description = TextField(blank=True)
    slug = SlugField(unique=True, max_length=295)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __repr__(self):
        return f"Bulletin(title={self.title}, owner={self.owner})"

    def __str__(self):
        return self.title


class Article(Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('under_evaluation', 'Under Evaluation'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    title = CharField(max_length=150, null=False, blank=False, unique=True)
    content = TextField(null=True, blank=True)

    subtite = CharField(max_length=200, null=True, blank=True)
    description = TextField(null=True, blank=True)

    status = CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')

    created = DateTimeField(auto_now_add=True)
    published = DateTimeField(null=True, blank=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __repr__(self):
        return f"Article(title={self.title}, created={self.created})"

    def __str__(self):
        return self.title
