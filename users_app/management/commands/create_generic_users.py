from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create generic users for testing assignee and reviewer selection.'

    def handle(self, *args, **options):
        users = [
            {'fullname': 'Max Mustermann', 'email': 'max.mustermann@example.com', 'password': 'test1234'},
            {'fullname': 'Erika Musterfrau', 'email': 'erika.musterfrau@example.com', 'password': 'test1234'},
            {'fullname': 'John Doe', 'email': 'john.doe@example.com', 'password': 'test1234'},
            {'fullname': 'Jane Doe', 'email': 'jane.doe@example.com', 'password': 'test1234'},
        ]
        for u in users:
            if not User.objects.filter(email=u['email']).exists():
                user = User.objects.create_user(
                    username=u['email'],
                    email=u['email'],
                    password=u['password'],
                    first_name=u['fullname']
                )
                self.stdout.write(self.style.SUCCESS(f"Created user: {u['fullname']}"))
            else:
                self.stdout.write(self.style.WARNING(f"User already exists: {u['fullname']}"))
