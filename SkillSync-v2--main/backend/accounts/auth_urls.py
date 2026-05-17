from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileDetailView, MeView

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("me", MeView.as_view(), name="me"),
    path("profile/<int:user_id>", ProfileDetailView.as_view(), name="profile-detail"),
]
