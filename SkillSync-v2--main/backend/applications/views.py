from rest_framework import permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related("project", "freelancer").order_by("-created_at")
        if user.is_staff:
            return qs
        if user.role == user.Role.FREELANCER:
            return qs.filter(freelancer=user.freelancer_profile)
        return qs.filter(project__client=user.client_profile)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != user.Role.FREELANCER:
            raise PermissionDenied("Only freelancers can apply to projects")
        serializer.save(freelancer=user.freelancer_profile)

    def update(self, request, *args, **kwargs):
        application = self.get_object()
        user = request.user
        data = request.data.copy()

        if user.is_staff:
            return super().update(request, *args, **kwargs)

        if user.role == user.Role.FREELANCER:
            if application.freelancer != user.freelancer_profile:
                raise PermissionDenied("You cannot update this application")
            if application.status != Application.Status.PENDING:
                return Response(
                    {"detail": "Only pending applications can be updated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data.pop("status", None)
        else:
            if application.project.client != user.client_profile:
                raise PermissionDenied("You cannot update this application")
            allowed = {"status"}
            data = {key: data[key] for key in allowed if key in data}
            if not data:
                return Response(
                    {"detail": "Only status can be updated"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(application, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
