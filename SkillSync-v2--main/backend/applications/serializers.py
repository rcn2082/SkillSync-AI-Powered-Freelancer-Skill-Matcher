from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_budget_min = serializers.DecimalField(
        source="project.budget_min", max_digits=10, decimal_places=2, read_only=True
    )
    project_budget_max = serializers.DecimalField(
        source="project.budget_max", max_digits=10, decimal_places=2, read_only=True
    )
    freelancer_name = serializers.CharField(source="freelancer.name", read_only=True)
    freelancer_experience = serializers.CharField(
        source="freelancer.experience_level", read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "project",
            "project_title",
            "project_budget_min",
            "project_budget_max",
            "freelancer",
            "freelancer_name",
            "freelancer_experience",
            "cover_letter",
            "proposed_rate",
            "status",
            "created_at",
        ]
        read_only_fields = ["freelancer", "created_at"]
