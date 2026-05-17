import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_MAP = {
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "typescript": "typescript",
    "js": "javascript",
    "py": "python",
}


def normalize_skill(skill: str) -> str:
    cleaned = re.sub(r"[^a-z0-9.+#]", "", skill.lower().strip())
    return SKILL_MAP.get(cleaned, cleaned)


def normalize_skills(skills):
    if not skills:
        return []
    normalized = [normalize_skill(s) for s in skills if s]
    return sorted(set(normalized))


def preprocess_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


class MatchingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", lowercase=True, max_features=1500)

    def _experience_score(self, level: str) -> float:
        levels = {"Junior": 0.5, "Mid": 0.75, "Senior": 1.0}
        return levels.get(level, 0.5)

    def _rating_score(self, rating: float) -> float:
        if rating is None:
            return 0.0
        return max(min(rating / 5.0, 1.0), 0.0)

    def _build_project_text(self, project) -> str:
        skills = " ".join(normalize_skills(project.required_skills))
        parts = [project.title, project.description, skills, project.category]
        return preprocess_text(" ".join([p for p in parts if p]))

    def _build_resume_text(self, freelancer) -> str:
        try:
            resume = freelancer.resume
        except Exception:
            return ""

        parts = [
            resume.headline,
            resume.summary,
            resume.location,
            resume.website,
            resume.phone,
        ]

        for exp in resume.experiences.all():
            parts.extend([exp.title, exp.company, exp.location, exp.description])

        for edu in resume.education.all():
            parts.extend(
                [edu.school, edu.degree, edu.field_of_study, edu.description, edu.grade]
            )

        for cert in resume.certifications.all():
            parts.extend([cert.name, cert.issuer])

        for link in resume.links.all():
            parts.extend([link.platform, link.url, link.username])

        return " ".join([p for p in parts if p])

    def _build_freelancer_text(self, freelancer) -> str:
        skills = " ".join(normalize_skills(freelancer.skills))
        resume_text = self._build_resume_text(freelancer)
        parts = [skills, freelancer.bio or "", freelancer.experience_level, resume_text]
        return preprocess_text(" ".join([p for p in parts if p]))

    def _build_project_corpus(self, project, freelancers):
        project_text = self._build_project_text(project)
        freelancer_texts = [self._build_freelancer_text(f) for f in freelancers]
        return project_text, freelancer_texts

    def match_project_to_freelancers(self, project, freelancers, weights=None, top_n=20):
        if not freelancers:
            return []

        weights = weights or {"skill": 0.6, "experience": 0.3, "rating": 0.1}
        project_text, freelancer_texts = self._build_project_corpus(project, freelancers)
        corpus = [project_text] + freelancer_texts

        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        results = []
        project_skills = normalize_skills(project.required_skills)

        for idx, freelancer in enumerate(freelancers):
            skill_score = float(similarities[idx])
            exp_score = self._experience_score(freelancer.experience_level)
            rating_score = self._rating_score(freelancer.rating)
            final_score = (
                weights["skill"] * skill_score
                + weights["experience"] * exp_score
                + weights["rating"] * rating_score
            )
            matched_skills = [s for s in normalize_skills(freelancer.skills) if s in project_skills]

            results.append(
                {
                    "freelancer_id": freelancer.id,
                    "score": round(final_score * 100, 2),
                    "skill_match": round(skill_score * 100, 2),
                    "matched_skills": matched_skills,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

    def match_freelancer_to_projects(self, freelancer, projects, weights=None, top_n=20):
        if not projects:
            return []

        weights = weights or {"skill": 0.6, "experience": 0.3, "rating": 0.1}
        freelancer_text = self._build_freelancer_text(freelancer)
        project_texts = [self._build_project_text(p) for p in projects]
        corpus = [freelancer_text] + project_texts

        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        freelancer_skills = normalize_skills(freelancer.skills)
        results = []

        for idx, project in enumerate(projects):
            skill_score = float(similarities[idx])
            exp_score = self._experience_score(freelancer.experience_level)
            rating_score = self._rating_score(freelancer.rating)
            final_score = (
                weights["skill"] * skill_score
                + weights["experience"] * exp_score
                + weights["rating"] * rating_score
            )
            project_skills = normalize_skills(project.required_skills)
            matched_skills = [s for s in freelancer_skills if s in project_skills]

            results.append(
                {
                    "project_id": project.id,
                    "score": round(final_score * 100, 2),
                    "skill_match": round(skill_score * 100, 2),
                    "matched_skills": matched_skills,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]
