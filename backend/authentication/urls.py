from django.urls import path
from .views import RegistrationView, LoginView, BoardListCreateView, BoardDetailUpdateView, BoardDeleteView, EmailCheckView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:board_id>/', BoardDetailUpdateView.as_view(), name='board-detail-update'),
    path('boards/<int:board_id>/delete/', BoardDeleteView.as_view(), name='board-delete'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
