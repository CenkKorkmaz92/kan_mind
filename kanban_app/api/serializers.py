"""
Serializers for Kanban app: Board, Task, Comment.
Provide serialization and custom field logic for API responses.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from users_app.api.serializers import UserSerializer
from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board model, includes member and ticket counts.
    """
    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'member_count',
                  'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

    def get_member_count(self, obj):
        """Return the number of members in the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks (tickets) in the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of 'to-do' tasks in the board."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks in the board."""
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(BoardSerializer):
    """
    Detailed serializer for Board, includes members and all tasks.
    """
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ['members', 'tasks']

    def get_tasks(self, obj):
        """Return all tasks for the board."""
        return TaskSerializer(obj.tasks.all(), many=True).data


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model, includes assignee, reviewer, and comment count.
    Accepts and returns board as integer (board ID).
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status',
                  'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        """Return the number of comments for the task."""
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model, includes author's name.
    """
    author = serializers.CharField(source='author.first_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
