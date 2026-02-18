import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD env vars"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("SUPERUSER_USERNAME")
        email = os.getenv("SUPERUSER_EMAIL", "")
        password = os.getenv("SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "Skipping superuser creation: "
                "SUPERUSER_USERNAME and SUPERUSER_PASSWORD env vars are not set."
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists. Skipping.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
