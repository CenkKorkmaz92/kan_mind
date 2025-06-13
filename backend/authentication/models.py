"""
Models for the Kanban backend app.
Defines Board, Task, and Comment data structures.
"""

from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """
    Represents a Kanban board with a title, owner, and members.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, related_name='owned_boards', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Represents a task on a board, with status, priority, assignee, reviewer, and due date.
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    board = models.ForeignKey(
        'Board', related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(
        User, related_name='review_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a task, with author and creation timestamp.
    """
    task = models.ForeignKey(
        'Task', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.first_name} on {self.task.title}"
