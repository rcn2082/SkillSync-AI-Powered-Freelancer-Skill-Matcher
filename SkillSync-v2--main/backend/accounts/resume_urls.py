from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ResumeMeView,
    ResumeExperienceViewSet,
    ResumeEducationViewSet,
    ResumeCertificationViewSet,
    ResumeLinkViewSet,
)

router = DefaultRouter()
router.register(r"experience", ResumeExperienceViewSet, basename="resume-experience")
router.register(r"education", ResumeEducationViewSet, basename="resume-education")
router.register(r"certifications", ResumeCertificationViewSet, basename="resume-certifications")
router.register(r"links", ResumeLinkViewSet, basename="resume-links")

urlpatterns = [
    path("me", ResumeMeView.as_view(), name="resume-me"),
]

urlpatterns += router.urls
