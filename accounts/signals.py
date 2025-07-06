from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Profile


@receiver(post_save, sender=User)
def create_profile_and_auto_subscribe(sender, instance, created, **kwargs):
    """ Automatically subscribe when a profile is created """
    if created:
        profile = Profile.objects.create(user=instance)
        print(f"Profile created for user: {instance.username}")

        # Auto-subscribe to platform bulletin if it exists
        auto_subscribe_to_platform_docs(profile)