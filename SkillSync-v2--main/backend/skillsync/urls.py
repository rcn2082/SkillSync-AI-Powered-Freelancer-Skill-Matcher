from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.auth_urls")),
    path("api/users/", include("accounts.urls")),
    path("api/resume/", include("accounts.resume_urls")),
    path("api/projects/", include("projects.urls")),
    path("api/applications/", include("applications.urls")),
    path("api/match/", include("matching.urls")),
]
