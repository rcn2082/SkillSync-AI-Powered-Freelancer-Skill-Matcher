import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Applications() {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const data = await apiFetch("/applications/");
      setApplications(data.results || data);
    } catch (err) {
      setError(err.message || "Unable to load applications");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      await apiFetch(`/applications/${id}/`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      await load();
    } catch (err) {
      setError(err.message || "Unable to update status");
    }
  };

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Applications</p>
          <h2>{user?.role === "client" ? "Incoming applications" : "Your applications"}</h2>
        </div>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="grid">
        {applications.map((app) => (
          <div key={app.id} className="card">
            <h3>{app.project_title}</h3>
            <p className="muted">Status: {app.status}</p>
            <p className="small">Rate: ${app.proposed_rate}</p>
            {user?.role === "client" ? (
              <div className="inline">
                <label>
                  Update status
                  <select
                    value={app.status}
                    onChange={(e) => updateStatus(app.id, e.target.value)}
                  >
                    <option value="pending">Pending</option>
                    <option value="accepted">Accepted</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </label>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
