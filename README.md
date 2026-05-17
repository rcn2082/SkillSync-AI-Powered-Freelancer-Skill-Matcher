# SkillSync

SkillSync is a full-stack web app that matches freelancers to projects using NLP-based similarity scoring. This repo contains a Django REST backend and a React (Vite) frontend.

## Structure
- backend: Django REST API, matching engine, and data models
- frontend: React UI and API client

## Key API endpoints
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`
- `PUT /api/auth/me`
- `GET /api/resume/me`
- `PUT /api/resume/me`
- `POST /api/resume/experience`
- `POST /api/resume/education`
- `POST /api/resume/certifications`
- `POST /api/resume/links`
- `GET /api/projects/`
- `POST /api/projects/`
- `GET /api/projects/:id`
- `POST /api/match/project/:id`
- `POST /api/match/freelancer/:id`
- `GET /api/applications/`
- `POST /api/applications/`

## Backend setup
1. Create a virtual environment
2. Install dependencies
3. Configure environment variables
4. Run migrations
5. Start the server

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Frontend setup
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Environment variables
Backend is configured to use `DATABASE_URL` if present (PostgreSQL recommended). If not set, SQLite is used for local development.

See `.env.example` files in each folder for full options.

## Notes
- Clients can only manage their own projects.
- Freelancers can only apply to projects and update pending applications.
- Matching endpoints are role-restricted to project owners and the freelancer themselves.
