from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from kanban_app.models import Board, Task, Comment

class Command(BaseCommand):
    help = 'Clear all data from the database except for migrations and admin setup.'

    def handle(self, *args, **options):
        Comment.objects.all().delete()
        Task.objects.all().delete()
        Board.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All boards, tasks, comments, and users have been deleted.'))
