"""
URL configuration for the Kanban backend app.
Defines all API routes for authentication, boards, tasks, and comments.
"""

from django.urls import path
from .views import RegistrationView, LoginView, BoardListCreateView, BoardDetailUpdateView, BoardDeleteView, EmailCheckView, TaskListCreateView, TaskDetailView, TasksAssignedToMeView, TasksReviewingView, TaskCommentsListCreateView, TaskCommentDeleteView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:board_id>/', BoardDetailUpdateView.as_view(), name='board-detail-update'),
    path('boards/<int:board_id>/delete/', BoardDeleteView.as_view(), name='board-delete'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/', TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', TasksReviewingView.as_view(), name='tasks-reviewing'),
    path('tasks/<int:task_id>/comments/', TaskCommentsListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDeleteView.as_view(), name='task-comment-delete'),
]