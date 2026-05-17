from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = [
            "id",
            "user",
            "name",
            "skills",
            "experience_level",
            "hourly_rate",
            "bio",
            "portfolio_links",
            "rating",
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = ["id", "user", "company_name", "name"]


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "headline", "summary", "location", "phone", "website", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class ResumeExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeExperience
        fields = [
            "id",
            "resume",
            "title",
            "company",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
        ]
        read_only_fields = ["resume"]


class ResumeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeEducation
        fields = [
            "id",
            "resume",
            "school",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "grade",
            "description",
        ]
        read_only_fields = ["resume"]


class ResumeCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeCertification
        fields = ["id", "resume", "name", "issuer", "issue_year", "credential_url"]
        read_only_fields = ["resume"]


class ResumeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeLink
        fields = ["id", "resume", "platform", "url", "username"]
        read_only_fields = ["resume"]


class ResumeDetailSerializer(ResumeSerializer):
    experiences = ResumeExperienceSerializer(many=True, read_only=True)
    education = ResumeEducationSerializer(many=True, read_only=True)
    certifications = ResumeCertificationSerializer(many=True, read_only=True)
    links = ResumeLinkSerializer(many=True, read_only=True)

    class Meta(ResumeSerializer.Meta):
        fields = ResumeSerializer.Meta.fields + [
            "experiences",
            "education",
            "certifications",
            "links",
        ]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices)

    name = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)

    skills = serializers.ListField(child=serializers.CharField(), required=False)
    experience_level = serializers.ChoiceField(
        choices=FreelancerProfile.ExperienceLevel.choices,
        required=False,
    )
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    portfolio_links = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        role = attrs.get("role")
        required = ["name"]

        missing = [key for key in required if not attrs.get(key)]
        if missing:
            raise serializers.ValidationError(
                {"missing_fields": f"Required fields: {', '.join(missing)}"}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("confirm_password", None)
        username = validated_data.pop("username", "")
        email = validated_data.get("email")

        if not username:
            username = email.split("@", 1)[0]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=validated_data.get("role"),
        )

        if user.role == User.Role.FREELANCER:
            FreelancerProfile.objects.create(
                user=user,
                name=validated_data.get("name", ""),
                skills=_normalize_list(validated_data.get("skills", []), lower=True),
                experience_level=validated_data.get("experience_level")
                or FreelancerProfile.ExperienceLevel.MID,
                hourly_rate=validated_data.get("hourly_rate") or 0,
                bio=validated_data.get("bio", ""),
                portfolio_links=_normalize_list(validated_data.get("portfolio_links", [])),
            )
        else:
            ClientProfile.objects.create(
                user=user,
                name=validated_data.get("name", ""),
                company_name=validated_data.get("company_name") or "Independent",
            )

        return user
