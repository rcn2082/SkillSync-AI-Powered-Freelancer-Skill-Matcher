import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";

export default function FreelancerDashboard() {
  const { profile } = useAuth();
  const [matches, setMatches] = useState([]);
  const [applications, setApplications] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      if (!profile?.id) return;
      try {
        const matchData = await apiFetch(`/match/freelancer/${profile.id}`, {
          method: "POST",
          body: JSON.stringify({ top_n: 6 }),
        });
        setMatches(matchData.matches || []);
        const applicationData = await apiFetch("/applications/");
        setApplications(applicationData.results || applicationData);
      } catch (err) {
        setError(err.message || "Unable to load dashboard data");
      }
    };
    load();
  }, [profile]);

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Freelancer dashboard</p>
          <h2>Recommended projects</h2>
        </div>
        <Link className="primary-link" to="/projects">
          Browse projects
        </Link>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="grid">
        {matches.map((match) => (
          <div key={match.project_id} className="card">
            <h3>{match.project?.title || `Project #${match.project_id}`}</h3>
            <p className="muted">Match score: {match.score}%</p>
            <p className="small">
              Skills matched: {(match.matched_skills || []).join(", ") || "No overlap"}
            </p>
            <Link className="ghost-link" to={`/projects/${match.project_id}`}>
              View project
            </Link>
          </div>
        ))}
      </div>

      <div className="section">
        <h3>Active applications</h3>
        <div className="grid">
          {applications.map((app) => (
            <div key={app.id} className="card">
              <h4>{app.project_title}</h4>
              <p className="muted">Status: {app.status}</p>
              <p className="small">Proposed rate: ${app.proposed_rate}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
