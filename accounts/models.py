from django.contrib.auth.models import User
from django.db.models import CASCADE, Model, OneToOneField, ImageField, ForeignKey
from django.db.models.fields import CharField, TextField, DateTimeField, BooleanField
from cloudinary_storage.storage import MediaCloudinaryStorage


# Extending existing User model
class Profile(Model):
    USER_ROLES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Administrator'),
    ]

    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    role = CharField(max_length=20, choices=USER_ROLES, default='reader')
    biography = TextField(max_length=500, null=True, blank=True)
    avatar = ImageField(
        default='default_avatar.png',
        upload_to='profile_pics/',
        storage=MediaCloudinaryStorage()
    )
    auto_subscribed_to_platform = BooleanField(default=False)

    class Meta:
        ordering = ['user__username']

    def __repr__(self):
        return f"Profile(name={self.user}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_reader(self):
        return True

    @property
    def is_writer(self):
        return self.role == 'writer'

    @property
    def is_admin(self):
        return self.role == 'admin'