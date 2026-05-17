from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import FreelancerProfile
from projects.models import Project
from .engine import MatchingEngine
from .models import Match


def _weights_from_request(request):
    payload = request.data if isinstance(request.data, dict) else {}
    weights = payload.get("weights") if isinstance(payload, dict) else None
    if not isinstance(weights, dict):
        return None
    try:
        skill = float(weights.get("skill", 0.6))
        exp = float(weights.get("experience", 0.3))
        rating = float(weights.get("rating", 0.1))
    except (TypeError, ValueError):
        return None

    total = skill + exp + rating
    if total == 0:
        return None
    return {"skill": skill / total, "experience": exp / total, "rating": rating / total}


def _top_n_from_request(request, default=20):
    payload = request.data if isinstance(request.data, dict) else {}
    top_n = payload.get("top_n", default)
    try:
        top_n = int(top_n)
        return max(1, min(top_n, 100))
    except (TypeError, ValueError):
        return default


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def match_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = request.user

    if not user.is_staff:
        if user.role != user.Role.CLIENT or project.client != user.client_profile:
            return Response({"detail": "Forbidden"}, status=403)

    freelancers = (
        FreelancerProfile.objects.select_related("user", "resume")
        .prefetch_related(
            "resume__experiences",
            "resume__education",
            "resume__certifications",
            "resume__links",
        )
        .all()
    )
    engine = MatchingEngine()
    weights = _weights_from_request(request)
    top_n = _top_n_from_request(request)
    matches = engine.match_project_to_freelancers(project, freelancers, weights=weights, top_n=top_n)

    freelancer_map = {f.id: f for f in freelancers}

    for item in matches:
        freelancer = freelancer_map.get(item["freelancer_id"])
        if freelancer:
            item["freelancer"] = {
                "id": freelancer.id,
                "name": freelancer.name,
                "experience_level": freelancer.experience_level,
                "hourly_rate": freelancer.hourly_rate,
                "rating": freelancer.rating,
                "skills": freelancer.skills,
            }

        Match.objects.update_or_create(
            project=project,
            freelancer_id=item["freelancer_id"],
            defaults={
                "match_score": item["score"],
                "matched_skills": item["matched_skills"],
            },
        )

    return Response({"project_id": project_id, "matches": matches})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def match_freelancer(request, freelancer_id):
    freelancer = (
        FreelancerProfile.objects.select_related("resume")
        .prefetch_related(
            "resume__experiences",
            "resume__education",
            "resume__certifications",
            "resume__links",
        )
        .filter(id=freelancer_id)
        .first()
    )
    if not freelancer:
        return Response({"detail": "Freelancer not found"}, status=404)
    user = request.user

    if not user.is_staff:
        if user.role != user.Role.FREELANCER or freelancer.user_id != user.id:
            return Response({"detail": "Forbidden"}, status=403)

    projects = Project.objects.filter(status=Project.Status.OPEN)
    engine = MatchingEngine()
    weights = _weights_from_request(request)
    top_n = _top_n_from_request(request)
    matches = engine.match_freelancer_to_projects(
        freelancer, list(projects), weights=weights, top_n=top_n
    )

    project_map = {p.id: p for p in projects}

    for item in matches:
        project = project_map.get(item["project_id"])
        if project:
            item["project"] = {
                "id": project.id,
                "title": project.title,
                "budget_min": project.budget_min,
                "budget_max": project.budget_max,
                "category": project.category,
                "required_skills": project.required_skills,
            }

        Match.objects.update_or_create(
            project_id=item["project_id"],
            freelancer=freelancer,
            defaults={
                "match_score": item["score"],
                "matched_skills": item["matched_skills"],
            },
        )

    return Response({"freelancer_id": freelancer_id, "matches": matches})
