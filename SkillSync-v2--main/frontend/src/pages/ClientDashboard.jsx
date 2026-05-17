import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api";

export default function ClientDashboard() {
  const [projects, setProjects] = useState([]);
  const [matches, setMatches] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch("/projects/");
        setProjects(data.results || data);
      } catch (err) {
        setError(err.message || "Unable to load projects");
      }
    };
    load();
  }, []);

  const loadMatches = async (project) => {
    setSelectedProject(project);
    try {
      const data = await apiFetch(`/match/project/${project.id}`, {
        method: "POST",
        body: JSON.stringify({ top_n: 6 }),
      });
      setMatches(data.matches || []);
    } catch (err) {
      setError(err.message || "Unable to load matches");
    }
  };

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Client dashboard</p>
          <h2>Your projects</h2>
        </div>
        <Link className="primary-link" to="/projects/new">
          Post a project
        </Link>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="grid">
        {projects.map((project) => (
          <div key={project.id} className="card">
            <h3>{project.title}</h3>
            <p className="muted">Budget: ${project.budget_min} - ${project.budget_max}</p>
            <button className="ghost" type="button" onClick={() => loadMatches(project)}>
              View matches
            </button>
          </div>
        ))}
      </div>

      <div className="section">
        <h3>{selectedProject ? `Top matches for ${selectedProject.title}` : "Match results"}</h3>
        <div className="grid">
          {matches.map((match) => (
            <div key={match.freelancer_id} className="card">
              <h4>{match.freelancer?.name || `Freelancer #${match.freelancer_id}`}</h4>
              <p className="muted">Score: {match.score}%</p>
              <p className="small">
                Skills: {(match.matched_skills || []).join(", ") || "No overlap"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
