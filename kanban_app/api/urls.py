from django.urls import path
from .views import (
    BoardListCreateView, BoardDetailView, EmailCheckView,
    TaskAssignedToMeView, TaskReviewingView, TaskCreateView, TaskDetailView,
    TaskCommentsView, TaskCommentDeleteView
)
from .members_views import BoardMembersListView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', TaskAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewingView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDeleteView.as_view(), name='task-comment-delete'),
    path('boards/<int:board_id>/members/', BoardMembersListView.as_view(), name='board-members-list'),
]
