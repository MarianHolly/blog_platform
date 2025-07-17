from bleach import clean
from ckeditor.fields import RichTextField
from django.db.models import Model, CASCADE, CharField, TextField, DateTimeField, ManyToManyField, OneToOneField, \
    SlugField, ForeignKey, Index
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from accounts.models import Profile


# Create your models here.
class Bulletin(Model):
    owner = OneToOneField(Profile, on_delete=CASCADE, related_name='bulletin')
    title = CharField(max_length=255, unique=True)
    description = TextField(blank=True)
    slug = SlugField(unique=True, max_length=295)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __repr__(self):
        return f"Bulletin(title={self.title}, owner={self.owner})"

    def __str__(self):
        return self.title

    def get_subscribers_count(self):
        return self.subscribers.count()


class Article(Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published')
    ]
    EVALUATION_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3']
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        '*': ['class']
    }

    title = CharField(max_length=150, null=False, blank=False, unique=True)
    content = CKEditor5Field(null=True, blank=True)
    bulletin = ForeignKey(Bulletin, on_delete=CASCADE, related_name='articles')

    subtitle = CharField(max_length=200, null=True, blank=True)
    description = TextField(null=True, blank=True)

    status = CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    evaluation = CharField(max_length=20, choices=EVALUATION_CHOICES, default='pending')

    created = DateTimeField(auto_now_add=True)
    published = DateTimeField(null=True, blank=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            Index(fields=['status', 'visibility', 'evaluation']),
            Index(fields=['bulletin', 'status']),
            Index(fields=['evaluation', 'created']),
        ]

    def __repr__(self):
        return f"Article(title={self.title}, status={self.status}, evaluation={self.evaluation})"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.content:
            self.content = clean(self.content, tags=self.ALLOWED_TAGS, attributes=self.ALLOWED_ATTRIBUTES, strip=True)

        if self.status == 'published':
            self.published = timezone.now()

        super().save(*args, **kwargs)

    @property
    def author(self):
        return self.bulletin.owner

    @property
    def is_draft(self):
        return self.status == 'draft'

    @property
    def is_published_public(self):
        return self.status == 'published' and self.visibility == 'public'

    @property
    def is_published_private(self):
        return self.status == 'published' and self.visibility == 'private'

    @property
    def is_approved(self):
        return self.evaluation == 'approved'

    @property
    def is_rejected(self):
        return self.evaluation == 'rejected'


class Subscription(Model):
    subscriber = ForeignKey(Profile, on_delete=CASCADE, related_name='subscriptions')
    bulletin = ForeignKey(Bulletin, on_delete=CASCADE, related_name='subscribers')
    created = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'bulletin')

    def __repr__(self):
        return f"Subscription(subscriber={self.subscriber}, bulletin={self.bulletin})"

    def __str__(self):
        return f"{self.subscriber} subscribed to '{self.bulletin.title}'"