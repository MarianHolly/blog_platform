from django.contrib.auth.models import User
from django.db.models import CASCADE, OneToOneField, Model
from django.db.models.fields import CharField, TextField

from content.models import Article


# Extending existing User model
class Profile(Model):
    USER_ROLES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Administrator'),
    ]

    user = OneToOneField(User, on_delete=CASCADE)
    role = CharField(max_length=20, choices=USER_ROLES, default='reader')

    biography = TextField(null=True, blank=True)

    def __repr__(self):
        return f"Profile(name={self.user.username}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"