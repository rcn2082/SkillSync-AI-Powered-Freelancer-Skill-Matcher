from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    FreelancerProfile,
    ClientProfile,
    Resume,
    ResumeExperience,
    ResumeEducation,
    ResumeCertification,
    ResumeLink,
)

User = get_user_model()

admin.site.register(User)
admin.site.register(FreelancerProfile)
admin.site.register(ClientProfile)
admin.site.register(Resume)
admin.site.register(ResumeExperience)
admin.site.register(ResumeEducation)
admin.site.register(ResumeCertification)
admin.site.register(ResumeLink)
