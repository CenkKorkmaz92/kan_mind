from django.urls import path
from .views import RegistrationView, LoginView, BoardListCreateView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListCreateView.as_view(), name='boards'),
]
