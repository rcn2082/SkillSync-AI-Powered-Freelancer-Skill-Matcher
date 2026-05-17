from django.db import models
from accounts.models import FreelancerProfile
from projects.models import Project


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(blank=True)
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer.name} -> {self.project.title}"
