from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import CASCADE, Model, OneToOneField, ImageField, ForeignKey
from django.db.models.fields import CharField, TextField, DateTimeField


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
    avatar = ImageField(default='default_avatar.png', upload_to='media/profile_pics')

    class Meta:
        ordering = ['user__username']

    def __repr__(self):
        return f"Profile(name={self.user}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        """Override save to add debugging information"""

        # Only perform file operations if we have an avatar and it's not the default
        if self.avatar and self.avatar.name != 'default_avatar.png':
            print(f"DEBUG: Saving profile with avatar: {self.avatar}")
            print(f"DEBUG: Avatar file object: {type(self.avatar)}")

            # Safely check if file exists before accessing it
            try:
                if hasattr(self.avatar, 'file') and default_storage.exists(self.avatar.name):
                    print(f"DEBUG: Avatar file: {self.avatar.file}")
            except (IOError, OSError) as e:
                print(f"DEBUG: Could not access avatar file: {e}")

        # Call the original save method
        result = super().save(*args, **kwargs)

        # Only try to get URL if file exists
        if self.avatar and self.avatar.name != 'default_avatar.png':
            try:
                if default_storage.exists(self.avatar.name):
                    print(f"DEBUG: After save, avatar path: {self.avatar}")
                    print(f"DEBUG: Avatar URL: {self.avatar.url}")
            except (IOError, OSError) as e:
                print(f"DEBUG: Could not generate avatar URL: {e}")

        return result

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