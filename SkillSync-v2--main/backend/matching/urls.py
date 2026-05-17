from django.urls import path
from .views import match_project, match_freelancer

urlpatterns = [
    path("project/<int:project_id>", match_project, name="match-project"),
    path("freelancer/<int:freelancer_id>", match_freelancer, name="match-freelancer"),
]
