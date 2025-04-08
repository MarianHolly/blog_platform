from django.contrib.auth.base_user import AbstractUser
from django.db.models import CASCADE, Model, OneToOneField, ManyToManyField
from django.db.models.fields import CharField, TextField

from content.models import Article


# Create your models here.
class User(AbstractUser):
    """Custom User model"""
    ROLE_CHOICES = ('reader', 'writer', 'admin', 'superadmin')
    role = CharField(max_length=10, choices=ROLE_CHOICES, default='reader')

    def __repr__(self):
        return f"User(title={self.title}, role={self.role})"

    def __str__(self):
        return f"{self.username}"


class Profile(Model):
    """Profile Model for Every User"""
    user = OneToOneField(User, on_delete=CASCADE)
    biography = models.TextField(blank=True)

    def __repr__(self):
        return f"Profile(user={self.user})"

    def __str__(self):
        return f"{self.user}"


class Bulletin(Model):
    """Bulletin Model only for Writers"""
    title = CharField(max_length=100, null=False, blank=False, unique=True)
    description = TextField(max_length=500)
    writer = OneToOneField(Profile, on_delete=CASCADE)
    articles = ManyToManyField(Article, blank=True, related_name='articles')

    def __repr__(self):
        return f"Bulletin(title={self.title}, writer={self.writer})"

    def __str__(self):
        return f"{self.title} - {self.writer}"
