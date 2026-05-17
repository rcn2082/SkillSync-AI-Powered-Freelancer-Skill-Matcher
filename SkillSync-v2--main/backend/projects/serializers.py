from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    client_company = serializers.CharField(source="client.company_name", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "client",
            "client_name",
            "client_company",
            "title",
            "description",
            "required_skills",
            "budget_min",
            "budget_max",
            "deadline",
            "category",
            "status",
            "created_at",
        ]
        read_only_fields = ["client", "created_at"]

    def validate_required_skills(self, value):
        if value is None:
            return []
        if isinstance(value, str):
            value = value.split(",")
        return [str(skill).strip().lower() for skill in value if str(skill).strip()]
