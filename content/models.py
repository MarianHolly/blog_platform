from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db.models import Model, CASCADE, CharField, TextField, DateTimeField, \
    SlugField, ForeignKey, Index, BooleanField, OneToOneField
from django.utils import timezone

from accounts.models import Profile


# Create your models here.
class Bulletin(Model):
    # Constants
    RESERVED_TITLES = ['Platformová dokumentácia', 'platformova dokumentacia']
    RESERVED_SLUGS = ['platformova-dokumentacia', 'platform-docs']

    # Database Fields
    owner = OneToOneField(Profile, on_delete=CASCADE, related_name='bulletin')
    title = CharField(max_length=255, unique=True)
    description = TextField(blank=True)
    slug = SlugField(unique=True, max_length=295)
    is_platform_docs = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        if self.is_platform_docs:
            return f"SuperAdmin - {self.title}"
        return self.title

    def __repr__(self):
        return f"Bulletin(title={self.title}, owner={self.owner})"

    # Decorator
    @property
    def is_superadmin_bulletin(self):
        return self.owner.is_super_admin

    # Methods
    def clean(self):
        if hasattr(self, 'owner') and self.owner:
            if not self.owner.is_super_admin:
                if self.title in self.RESERVED_TITLES:
                    raise ValidationError('Tento názov je rezervovaný.')

        if self.is_platform_docs:
            existing = Bulletin.objects.filter(is_platform_docs=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError('Platformová dokumentácia už existuje.')

    def save(self, *args, **kwargs):
        if self.owner.is_super_admin:
            self.is_platform_docs = True
            if not self.title:
                self.title = 'Platformová dokumentácia'
            if not self.slug:
                self.slug = 'platformova-dokumentacia'

        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_platform_docs:
            raise ValidationError('Nemôžete vymazať platformovú dokumentáciu.')
        super().delete(*args, **kwargs)

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

    title = CharField(max_length=150, null=False, blank=False, unique=True)
    content = RichTextField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        is_new_publication = False

        if self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.status != 'published' and self.status == 'published':
                    is_new_publication = True
            except self.__class__.DoesNotExist:
                pass

        if self.status == 'published':
            if not self.published or is_new_publication:
                self.published = timezone.now()

        if hasattr(self, 'bulletin') and self.bulletin and hasattr(self.bulletin, 'owner'):
            if self.bulletin.owner.is_super_admin:
                self.evaluation = 'approved'

        super().save(*args, **kwargs)


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