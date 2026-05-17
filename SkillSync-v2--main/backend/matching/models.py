from django.db import models
from accounts.models import FreelancerProfile
from projects.models import Project


class Match(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="matches")
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name="matches")
    match_score = models.FloatField()
    matched_skills = models.JSONField(default=list, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} -> {self.freelancer.name} ({self.match_score})"
