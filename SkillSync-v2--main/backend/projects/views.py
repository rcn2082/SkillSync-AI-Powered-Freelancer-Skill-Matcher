from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.select_related("client").all()

        if not user.is_staff:
            if user.role == user.Role.CLIENT:
                qs = qs.filter(client=user.client_profile)
            else:
                qs = qs.filter(status=Project.Status.OPEN)

        params = self.request.query_params
        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        category = params.get("category")
        if category:
            qs = qs.filter(category__iexact=category)

        budget_min = params.get("budget_min")
        budget_max = params.get("budget_max")
        if budget_min:
            qs = qs.filter(budget_min__gte=budget_min)
        if budget_max:
            qs = qs.filter(budget_max__lte=budget_max)

        skills = params.get("skills")
        if skills:
            for skill in [s.strip().lower() for s in skills.split(",") if s.strip()]:
                qs = qs.filter(required_skills__contains=[skill])

        query = params.get("q")
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != user.Role.CLIENT:
            raise PermissionDenied("Only clients can create projects")
        serializer.save(client=user.client_profile)

    def perform_update(self, serializer):
        project = self.get_object()
        user = self.request.user
        if not user.is_staff and (user.role != user.Role.CLIENT or project.client != user.client_profile):
            raise PermissionDenied("You cannot update this project")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and (user.role != user.Role.CLIENT or instance.client != user.client_profile):
            raise PermissionDenied("You cannot delete this project")
        instance.delete()
