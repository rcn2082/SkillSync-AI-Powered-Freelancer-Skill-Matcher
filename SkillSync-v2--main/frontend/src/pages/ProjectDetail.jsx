import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "../api";
import { useAuth } from "../context/AuthContext";

export default function ProjectDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [project, setProject] = useState(null);
  const [matches, setMatches] = useState([]);
  const [coverLetter, setCoverLetter] = useState("");
  const [rate, setRate] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch(`/projects/${id}/`);
        setProject(data);
      } catch (err) {
        setError(err.message || "Unable to load project");
      }
    };
    load();
  }, [id]);

  const handleApply = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await apiFetch("/applications/", {
        method: "POST",
        body: JSON.stringify({
          project: id,
          cover_letter: coverLetter,
          proposed_rate: rate,
        }),
      });
      setMessage("Application submitted");
      setCoverLetter("");
      setRate("");
    } catch (err) {
      setError(err.message || "Unable to submit application");
    }
  };

  const loadMatches = async () => {
    if (!project) return;
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

  if (!project) {
    return <div className="page-shell">Loading project...</div>;
  }

  return (
    <div className="page-shell">
      <div className="card">
        <h2>{project.title}</h2>
        <p className="muted">{project.description}</p>
        <p className="small">Category: {project.category || "General"}</p>
        <p className="small">Budget: ${project.budget_min} - ${project.budget_max}</p>
        <p className="small">
          Required skills: {(project.required_skills || []).join(", ") || "Not specified"}
        </p>
      </div>

      {error ? <div className="error">{error}</div> : null}
      {message ? <div className="success">{message}</div> : null}

      {user?.role === "freelancer" ? (
        <div className="card">
          <h3>Apply to this project</h3>
          <form className="form" onSubmit={handleApply}>
            <label>
              Proposed rate
              <input
                type="number"
                value={rate}
                onChange={(e) => setRate(e.target.value)}
                required
              />
            </label>
            <label>
              Cover letter
              <textarea
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
              />
            </label>
            <button className="primary" type="submit">
              Submit application
            </button>
          </form>
        </div>
      ) : null}

      {user?.role === "client" ? (
        <div className="card">
          <div className="page-header">
            <h3>Match results</h3>
            <button className="ghost" type="button" onClick={loadMatches}>
              Refresh matches
            </button>
          </div>
          <div className="grid">
            {matches.map((match) => (
              <div key={match.freelancer_id} className="card nested">
                <h4>{match.freelancer?.name || `Freelancer #${match.freelancer_id}`}</h4>
                <p className="muted">Score: {match.score}%</p>
                <p className="small">
                  Skills: {(match.matched_skills || []).join(", ") || "No overlap"}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
