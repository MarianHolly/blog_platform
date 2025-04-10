from django.contrib.auth.models import User
from django.db.models import CASCADE, Model, OneToOneField, ImageField, ForeignKey
from django.db.models.fields import CharField, TextField, DateTimeField


# Extending existing User model
class Profile(Model):
    USER_ROLES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Administrator'),
    ]

    user = OneToOneField(User, on_delete=CASCADE)
    role = CharField(max_length=20, choices=USER_ROLES, default='reader')
    biography = TextField(max_length=500, null=True, blank=True)
    avatar = ImageField(default='default_avatar.png', upload_to='profile_pics')

    class Meta:
        ordering = ['user__username']

    def __repr__(self):
        return f"Profile(name={self.user}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"


class Subscription(Model):
    subscriber = ForeignKey(User, on_delete=CASCADE, related_name='subscriptions')
    writer = ForeignKey(User, on_delete=CASCADE, related_name='subscribers')
    created = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"Subscription(subscriber={self.subscriber}, writer={self.writer})"

    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.writer}"
