from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    FreelancerProfile,
    ClientProfile,
    Resume,
    ResumeExperience,
    ResumeEducation,
    ResumeCertification,
    ResumeLink,
)
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
    FreelancerProfileSerializer,
    ClientProfileSerializer,
    ResumeSerializer,
    ResumeDetailSerializer,
    ResumeExperienceSerializer,
    ResumeEducationSerializer,
    ResumeCertificationSerializer,
    ResumeLinkSerializer,
)

User = get_user_model()


def _normalize_list(values, lower=False):
    if values is None:
        return []
    if isinstance(values, str):
        values = values.split(",")
    cleaned = []
    for value in values:
        if not value:
            continue
        item = str(value).strip()
        if not item:
            continue
        cleaned.append(item.lower() if lower else item)
    return cleaned


def _get_resume_for_user(user):
    if user.role != User.Role.FREELANCER:
        raise PermissionDenied("Only freelancers can access resumes")
    profile = getattr(user, "freelancer_profile", None)
    if not profile:
        raise PermissionDenied("Freelancer profile not found")
    resume, _ = Resume.objects.get_or_create(freelancer=profile)
    return resume


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = (
            request.data.get("identifier")
            or request.data.get("email")
            or request.data.get("username")
        )
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"detail": "Identifier and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            User.objects.filter(email__iexact=identifier).first()
            or User.objects.filter(username__iexact=identifier).first()
        )
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = (
            getattr(user, "freelancer_profile", None)
            if user.role == User.Role.FREELANCER
            else getattr(user, "client_profile", None)
        )
        if not profile:
            return Response({"detail": "Profile not found"}, status=404)
        if user.role == User.Role.FREELANCER:
            profile_serializer = FreelancerProfileSerializer(profile)
        else:
            profile_serializer = ClientProfileSerializer(profile)

        return Response({"user": UserSerializer(user).data, "profile": profile_serializer.data})

    def put(self, request):
        user = request.user
        payload = request.data or {}
        user_payload = payload.get("user", {}) if isinstance(payload, dict) else {}
        profile_payload = payload.get("profile", {}) if isinstance(payload, dict) else {}

        if not user_payload:
            user_payload = {
                key: payload[key]
                for key in ("username", "email")
                if isinstance(payload, dict) and key in payload
            }

        if user.role == User.Role.FREELANCER:
            profile = getattr(user, "freelancer_profile", None)
            profile_fields = {
                "name",
                "skills",
                "experience_level",
                "hourly_rate",
                "bio",
                "portfolio_links",
            }
            if not profile_payload:
                profile_payload = {
                    key: payload[key]
                    for key in profile_fields
                    if isinstance(payload, dict) and key in payload
                }
            if "skills" in profile_payload:
                profile_payload["skills"] = _normalize_list(profile_payload.get("skills"), lower=True)
            if "portfolio_links" in profile_payload:
                profile_payload["portfolio_links"] = _normalize_list(
                    profile_payload.get("portfolio_links")
                )
            serializer_class = FreelancerProfileSerializer
        else:
            profile = getattr(user, "client_profile", None)
            profile_fields = {"name", "company_name"}
            if not profile_payload:
                profile_payload = {
                    key: payload[key]
                    for key in profile_fields
                    if isinstance(payload, dict) and key in payload
                }
            serializer_class = ClientProfileSerializer

        if not profile:
            return Response({"detail": "Profile not found"}, status=404)

        user_serializer = UserUpdateSerializer(user, data=user_payload, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        profile_serializer = serializer_class(profile, data=profile_payload, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        return Response({"user": user_serializer.data, "profile": profile_serializer.data})


class ProfileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.role == User.Role.FREELANCER:
            profile = getattr(user, "freelancer_profile", None)
            if not profile:
                return Response({"detail": "Profile not found"}, status=404)
            serializer = FreelancerProfileSerializer(profile)
        else:
            profile = getattr(user, "client_profile", None)
            if not profile:
                return Response({"detail": "Profile not found"}, status=404)
            serializer = ClientProfileSerializer(profile)

        return Response({"user": UserSerializer(user).data, "profile": serializer.data})

    def put(self, request, user_id):
        if request.user.id != user_id and not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=403)

        user = get_object_or_404(User, id=user_id)
        if user.role == User.Role.FREELANCER:
            profile = getattr(user, "freelancer_profile", None)
            if not profile:
                return Response({"detail": "Profile not found"}, status=404)
            serializer = FreelancerProfileSerializer(profile, data=request.data, partial=True)
        else:
            profile = getattr(user, "client_profile", None)
            if not profile:
                return Response({"detail": "Profile not found"}, status=404)
            serializer = ClientProfileSerializer(profile, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResumeMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume = _get_resume_for_user(request.user)
        serializer = ResumeDetailSerializer(resume)
        return Response(serializer.data)

    def put(self, request):
        resume = _get_resume_for_user(request.user)
        serializer = ResumeSerializer(resume, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        detail = ResumeDetailSerializer(resume)
        return Response(detail.data)


class ResumeExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        resume = _get_resume_for_user(self.request.user)
        return ResumeExperience.objects.filter(resume=resume).order_by("-start_date", "-id")

    def perform_create(self, serializer):
        serializer.save(resume=_get_resume_for_user(self.request.user))


class ResumeEducationViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        resume = _get_resume_for_user(self.request.user)
        return ResumeEducation.objects.filter(resume=resume).order_by("-end_year", "-id")

    def perform_create(self, serializer):
        serializer.save(resume=_get_resume_for_user(self.request.user))


class ResumeCertificationViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        resume = _get_resume_for_user(self.request.user)
        return ResumeCertification.objects.filter(resume=resume).order_by("-issue_year", "-id")

    def perform_create(self, serializer):
        serializer.save(resume=_get_resume_for_user(self.request.user))


class ResumeLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        resume = _get_resume_for_user(self.request.user)
        return ResumeLink.objects.filter(resume=resume).order_by("platform", "id")

    def perform_create(self, serializer):
        serializer.save(resume=_get_resume_for_user(self.request.user))


class FreelancerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FreelancerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FreelancerProfile.objects.select_related("user").all().order_by("name")
        params = self.request.query_params

        skills = params.get("skills")
        if skills:
            for skill in [s.strip().lower() for s in skills.split(",") if s.strip()]:
                qs = qs.filter(skills__contains=[skill])

        experience = params.get("experience_level")
        if experience:
            qs = qs.filter(experience_level__iexact=experience)

        rate_min = params.get("hourly_rate_min")
        rate_max = params.get("hourly_rate_max")
        if rate_min:
            qs = qs.filter(hourly_rate__gte=rate_min)
        if rate_max:
            qs = qs.filter(hourly_rate__lte=rate_max)

        query = params.get("q")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(bio__icontains=query))

        return qs


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ClientProfile.objects.select_related("user").all().order_by("company_name")
        query = self.request.query_params.get("q")
        if query:
            qs = qs.filter(Q(company_name__icontains=query) | Q(name__icontains=query))
        return qs
