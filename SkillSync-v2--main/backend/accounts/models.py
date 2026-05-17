from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        FREELANCER = "freelancer", "Freelancer"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)

    REQUIRED_FIELDS = ["email"]


class FreelancerProfile(models.Model):
    class ExperienceLevel(models.TextChoices):
        JUNIOR = "Junior", "Junior"
        MID = "Mid", "Mid"
        SENIOR = "Senior", "Senior"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="freelancer_profile")
    name = models.CharField(max_length=255)
    skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    portfolio_links = models.JSONField(default=list, blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    company_name = models.CharField(max_length=255, blank=True, default="Independent")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.company_name} - {self.name}"


class Resume(models.Model):
    freelancer = models.OneToOneField(
        FreelancerProfile, on_delete=models.CASCADE, related_name="resume"
    )
    headline = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.freelancer.name}"


class ResumeExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"


class ResumeEducation(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.school} ({self.degree})"


class ResumeCertification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True)
    issue_year = models.IntegerField(null=True, blank=True)
    credential_url = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class ResumeLink(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="links")
    platform = models.CharField(max_length=100)
    url = models.CharField(max_length=500)
    username = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.platform}: {self.url}"
