from django.contrib.auth.models import User
from django.db.models import CASCADE, Model, OneToOneField, ImageField
from django.db.models.fields import BooleanField, CharField, TextField


class Profile(Model):
    USER_ROLES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Administrator'),
    ]

    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    role = CharField(max_length=20, choices=USER_ROLES, default='reader')
    biography = TextField(max_length=500, null=True, blank=True)
    avatar = ImageField(default='default_avatar.jpg', upload_to='static/images')
    auto_subscribed_to_platform = BooleanField(default=True)

    class Meta:
        ordering = ['user__username']

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

    @property
    def is_super_admin(self):
        return self.user.is_superuser

    @property
    def display_role(self):
        role_names = {
            'reader': 'Čitateľ',
            'writer': 'Autor',
            'admin': 'Administrátor'
        }
        return role_names.get(self.role, self.role)

    def __repr__(self):
        return f"Profile(name={self.user}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)