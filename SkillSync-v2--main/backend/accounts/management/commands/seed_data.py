from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import (
    ClientProfile,
    FreelancerProfile,
    Resume,
    ResumeExperience,
    ResumeEducation,
    ResumeCertification,
    ResumeLink,
)
from applications.models import Application
from matching.engine import MatchingEngine, normalize_skills
from matching.models import Match
from projects.models import Project


class Command(BaseCommand):
    help = "Seed the database with demo users, profiles, projects, and applications."

    def handle(self, *args, **options):
        User = get_user_model()

        freelancers_data = [
            {
                "email": "john.doe@demo.skillsync",
                "username": "johndoe",
                "name": "John Doe",
                "skills": ["react", "node.js", "mongodb", "javascript", "typescript"],
                "experience_level": FreelancerProfile.ExperienceLevel.SENIOR,
                "hourly_rate": Decimal("55.00"),
                "bio": "Full-stack developer with 6+ years in MERN stack.",
                "portfolio_links": [
                    "https://github.com/johndoe",
                    "https://www.linkedin.com/in/johndoe",
                ],
                "rating": 4.8,
            },
            {
                "email": "jane.smith@demo.skillsync",
                "username": "janesmith",
                "name": "Jane Smith",
                "skills": ["python", "django", "nlp", "tensorflow", "api"],
                "experience_level": FreelancerProfile.ExperienceLevel.MID,
                "hourly_rate": Decimal("42.00"),
                "bio": "AI/ML engineer specializing in NLP products.",
                "portfolio_links": [
                    "https://github.com/janesmith",
                    "https://www.linkedin.com/in/janesmith",
                ],
                "rating": 4.6,
            },
            {
                "email": "ahmed.ali@demo.skillsync",
                "username": "ahmedali",
                "name": "Ahmed Ali",
                "skills": ["figma", "product design", "ux", "ui", "research"],
                "experience_level": FreelancerProfile.ExperienceLevel.JUNIOR,
                "hourly_rate": Decimal("28.00"),
                "bio": "Product designer focused on clean UX for SaaS teams.",
                "portfolio_links": [
                    "https://www.behance.net/ahmedali",
                ],
                "rating": 4.2,
            },
        ]

        clients_data = [
            {
                "email": "client.acme@demo.skillsync",
                "username": "acmeclient",
                "name": "Sarah Connor",
                "company_name": "Acme Corp",
            },
            {
                "email": "client.nova@demo.skillsync",
                "username": "novaclient",
                "name": "Miguel Torres",
                "company_name": "Nova Labs",
            },
        ]

        projects_data = [
            {
                "title": "E-commerce Website Development",
                "description": "Build a modern e-commerce platform with payments and admin.",
                "required_skills": ["react", "node.js", "mongodb", "payments"],
                "budget_min": Decimal("2000.00"),
                "budget_max": Decimal("5000.00"),
                "deadline": None,
                "category": "Web Development",
            },
            {
                "title": "AI Chatbot Development",
                "description": "Develop an intelligent customer support chatbot with NLP.",
                "required_skills": ["python", "nlp", "machine learning", "api"],
                "budget_min": Decimal("3000.00"),
                "budget_max": Decimal("7000.00"),
                "deadline": None,
                "category": "AI/ML",
            },
            {
                "title": "Product Design Sprint",
                "description": "Design UX flows and UI system for a fintech dashboard.",
                "required_skills": ["product design", "ux", "ui", "figma"],
                "budget_min": Decimal("1200.00"),
                "budget_max": Decimal("2500.00"),
                "deadline": None,
                "category": "Design",
            },
        ]

        with transaction.atomic():
            freelancer_profiles = []
            for data in freelancers_data:
                user, created = User.objects.get_or_create(
                    email=data["email"],
                    defaults={
                        "username": data["username"],
                        "role": User.Role.FREELANCER,
                    },
                )
                if created:
                    user.set_password("DemoPassword1!")
                    user.save()

                profile, _ = FreelancerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "name": data["name"],
                        "skills": normalize_skills(data["skills"]),
                        "experience_level": data["experience_level"],
                        "hourly_rate": data["hourly_rate"],
                        "bio": data["bio"],
                        "portfolio_links": data["portfolio_links"],
                        "rating": data["rating"],
                    },
                )
                resume, _ = Resume.objects.get_or_create(
                    freelancer=profile,
                    defaults={
                        "headline": f"{data['experience_level']} {', '.join(data['skills'][:2])} Specialist",
                        "summary": data["bio"],
                        "location": "Remote",
                        "website": data["portfolio_links"][0] if data["portfolio_links"] else "",
                    },
                )

                if not resume.experiences.exists():
                    ResumeExperience.objects.create(
                        resume=resume,
                        title="Lead Developer" if data["experience_level"] == "Senior" else "Contributor",
                        company="SkillSync Labs",
                        location="Remote",
                        description="Delivered client projects across multiple industries.",
                        is_current=True,
                    )
                if not resume.education.exists():
                    ResumeEducation.objects.create(
                        resume=resume,
                        school="Global Tech University",
                        degree="BSc",
                        field_of_study="Computer Science",
                        end_year=2022,
                    )
                if not resume.certifications.exists():
                    ResumeCertification.objects.create(
                        resume=resume,
                        name="Professional Certificate",
                        issuer="SkillSync Academy",
                        issue_year=2024,
                    )
                if not resume.links.exists() and data["portfolio_links"]:
                    ResumeLink.objects.create(
                        resume=resume,
                        platform="Portfolio",
                        url=data["portfolio_links"][0],
                    )

                freelancer_profiles.append(profile)

            client_profiles = []
            for data in clients_data:
                user, created = User.objects.get_or_create(
                    email=data["email"],
                    defaults={
                        "username": data["username"],
                        "role": User.Role.CLIENT,
                    },
                )
                if created:
                    user.set_password("DemoPassword1!")
                    user.save()

                profile, _ = ClientProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "name": data["name"],
                        "company_name": data["company_name"],
                    },
                )
                client_profiles.append(profile)

            created_projects = []
            for index, project_data in enumerate(projects_data):
                client = client_profiles[index % len(client_profiles)]
                project, _ = Project.objects.get_or_create(
                    title=project_data["title"],
                    client=client,
                    defaults={
                        "description": project_data["description"],
                        "required_skills": normalize_skills(project_data["required_skills"]),
                        "budget_min": project_data["budget_min"],
                        "budget_max": project_data["budget_max"],
                        "deadline": project_data["deadline"],
                        "category": project_data["category"],
                        "status": Project.Status.OPEN,
                    },
                )
                created_projects.append(project)

            if not Application.objects.exists():
                Application.objects.create(
                    project=created_projects[0],
                    freelancer=freelancer_profiles[0],
                    cover_letter="Excited to build a robust ecommerce platform.",
                    proposed_rate=Decimal("52.00"),
                )
                Application.objects.create(
                    project=created_projects[1],
                    freelancer=freelancer_profiles[1],
                    cover_letter="Strong NLP experience, ready to deliver.",
                    proposed_rate=Decimal("45.00"),
                )
                Application.objects.create(
                    project=created_projects[2],
                    freelancer=freelancer_profiles[2],
                    cover_letter="Design sprint ready, can start next week.",
                    proposed_rate=Decimal("30.00"),
                )

            engine = MatchingEngine()
            for project in created_projects:
                matches = engine.match_project_to_freelancers(project, freelancer_profiles)
                for item in matches:
                    Match.objects.update_or_create(
                        project=project,
                        freelancer_id=item["freelancer_id"],
                        defaults={
                            "match_score": item["score"],
                            "matched_skills": item["matched_skills"],
                        },
                    )

        self.stdout.write(self.style.SUCCESS("Seed data created/updated successfully."))
