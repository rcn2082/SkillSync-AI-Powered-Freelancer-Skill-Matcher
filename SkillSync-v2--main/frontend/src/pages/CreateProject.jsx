import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

export default function CreateProject() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    description: "",
    required_skills: "",
    budget_min: "",
    budget_max: "",
    deadline: "",
    category: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    const payload = {
      title: form.title,
      description: form.description,
      required_skills: form.required_skills
        .split(",")
        .map((s) => s.trim().toLowerCase())
        .filter(Boolean),
      budget_min: form.budget_min,
      budget_max: form.budget_max,
      deadline: form.deadline || null,
      category: form.category,
    };

    try {
      const data = await apiFetch("/projects/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      navigate(`/projects/${data.id}`);
    } catch (err) {
      setError(err.message || "Unable to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="card form-card">
        <h2>Post a project</h2>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Project title
            <input name="title" value={form.title} onChange={handleChange} required />
          </label>
          <label>
            Description
            <textarea name="description" value={form.description} onChange={handleChange} required />
          </label>
          <label>
            Required skills (comma separated)
            <input name="required_skills" value={form.required_skills} onChange={handleChange} />
          </label>
          <label>
            Budget min
            <input
              name="budget_min"
              type="number"
              value={form.budget_min}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Budget max
            <input
              name="budget_max"
              type="number"
              value={form.budget_max}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Deadline
            <input name="deadline" type="date" value={form.deadline} onChange={handleChange} />
          </label>
          <label>
            Category
            <input name="category" value={form.category} onChange={handleChange} />
          </label>
          {error ? <div className="error">{error}</div> : null}
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Saving..." : "Create project"}
          </button>
        </form>
      </div>
    </div>
  );
}
