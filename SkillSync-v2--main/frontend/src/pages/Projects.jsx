import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Projects() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  const load = async (search = "") => {
    try {
      const data = await apiFetch(`/projects/?q=${encodeURIComponent(search)}`);
      setProjects(data.results || data);
    } catch (err) {
      setError(err.message || "Unable to load projects");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSearch = (event) => {
    event.preventDefault();
    load(query);
  };

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Projects</p>
          <h2>{user?.role === "client" ? "Your project postings" : "Open projects"}</h2>
        </div>
        {user?.role === "client" ? (
          <Link to="/projects/new" className="primary-link">
            New project
          </Link>
        ) : null}
      </div>

      <form className="search" onSubmit={handleSearch}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title or description"
        />
        <button className="ghost" type="submit">
          Search
        </button>
      </form>

      {error ? <div className="error">{error}</div> : null}

      <div className="grid">
        {projects.map((project) => (
          <div key={project.id} className="card">
            <h3>{project.title}</h3>
            <p className="muted">Category: {project.category || "General"}</p>
            <p className="small">Budget: ${project.budget_min} - ${project.budget_max}</p>
            <Link className="ghost-link" to={`/projects/${project.id}`}>
              View details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
