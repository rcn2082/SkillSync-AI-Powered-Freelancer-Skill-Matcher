import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { useAuth } from "../context/AuthContext";

const emptyResume = {
  headline: "",
  summary: "",
  location: "",
  phone: "",
  website: "",
};

export default function Resume() {
  const { user } = useAuth();
  const [resume, setResume] = useState(null);
  const [form, setForm] = useState(emptyResume);
  const [expForm, setExpForm] = useState({
    title: "",
    company: "",
    location: "",
    start_date: "",
    end_date: "",
    is_current: false,
    description: "",
  });
  const [eduForm, setEduForm] = useState({
    school: "",
    degree: "",
    field_of_study: "",
    start_year: "",
    end_year: "",
    grade: "",
    description: "",
  });
  const [certForm, setCertForm] = useState({
    name: "",
    issuer: "",
    issue_year: "",
    credential_url: "",
  });
  const [linkForm, setLinkForm] = useState({
    platform: "",
    url: "",
    username: "",
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadResume = async () => {
    try {
      const data = await apiFetch("/resume/me");
      setResume(data);
      setForm({
        headline: data.headline || "",
        summary: data.summary || "",
        location: data.location || "",
        phone: data.phone || "",
        website: data.website || "",
      });
    } catch (err) {
      setError(err.message || "Unable to load resume");
    }
  };

  useEffect(() => {
    if (user?.role === "freelancer") {
      loadResume();
    }
  }, [user]);

  const handleBaseChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const saveBase = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const data = await apiFetch("/resume/me", {
        method: "PUT",
        body: JSON.stringify(form),
      });
      setResume(data);
      setMessage("Resume updated");
    } catch (err) {
      setError(err.message || "Unable to update resume");
    }
  };

  const addExperience = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/resume/experience/", {
        method: "POST",
        body: JSON.stringify(expForm),
      });
      setExpForm({
        title: "",
        company: "",
        location: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
      });
      await loadResume();
    } catch (err) {
      setError(err.message || "Unable to add experience");
    }
  };

  const addEducation = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/resume/education/", {
        method: "POST",
        body: JSON.stringify(eduForm),
      });
      setEduForm({
        school: "",
        degree: "",
        field_of_study: "",
        start_year: "",
        end_year: "",
        grade: "",
        description: "",
      });
      await loadResume();
    } catch (err) {
      setError(err.message || "Unable to add education");
    }
  };

  const addCertification = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/resume/certifications/", {
        method: "POST",
        body: JSON.stringify(certForm),
      });
      setCertForm({ name: "", issuer: "", issue_year: "", credential_url: "" });
      await loadResume();
    } catch (err) {
      setError(err.message || "Unable to add certification");
    }
  };

  const addLink = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/resume/links/", {
        method: "POST",
        body: JSON.stringify(linkForm),
      });
      setLinkForm({ platform: "", url: "", username: "" });
      await loadResume();
    } catch (err) {
      setError(err.message || "Unable to add link");
    }
  };

  const deleteItem = async (path) => {
    setError("");
    try {
      await apiFetch(path, { method: "DELETE" });
      await loadResume();
    } catch (err) {
      setError(err.message || "Unable to delete item");
    }
  };

  if (user?.role !== "freelancer") {
    return (
      <div className="page-shell">
        <div className="card">Resume is available for freelancers only.</div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="eyebrow">Resume</p>
          <h2>Showcase your experience</h2>
        </div>
      </div>

      {error ? <div className="error">{error}</div> : null}
      {message ? <div className="success">{message}</div> : null}

      <div className="card form-card">
        <h3>Headline & Summary</h3>
        <form className="form" onSubmit={saveBase}>
          <label>
            Headline
            <input name="headline" value={form.headline} onChange={handleBaseChange} />
          </label>
          <label>
            Summary
            <textarea name="summary" value={form.summary} onChange={handleBaseChange} />
          </label>
          <label>
            Location
            <input name="location" value={form.location} onChange={handleBaseChange} />
          </label>
          <label>
            Phone
            <input name="phone" value={form.phone} onChange={handleBaseChange} />
          </label>
          <label>
            Website
            <input name="website" value={form.website} onChange={handleBaseChange} />
          </label>
          <button className="primary" type="submit">
            Save resume
          </button>
        </form>
      </div>

      <div className="section">
        <h3>Experience</h3>
        <div className="grid">
          {(resume?.experiences || []).map((exp) => (
            <div key={exp.id} className="card">
              <h4>{exp.title}</h4>
              <p className="muted">{exp.company}</p>
              <p className="small">{exp.description}</p>
              <button
                className="ghost"
                type="button"
                onClick={() => deleteItem(`/resume/experience/${exp.id}/`)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <div className="card form-card">
          <h4>Add experience</h4>
          <form className="form" onSubmit={addExperience}>
            <label>
              Title
              <input
                value={expForm.title}
                onChange={(e) => setExpForm((prev) => ({ ...prev, title: e.target.value }))}
                required
              />
            </label>
            <label>
              Company
              <input
                value={expForm.company}
                onChange={(e) => setExpForm((prev) => ({ ...prev, company: e.target.value }))}
              />
            </label>
            <label>
              Location
              <input
                value={expForm.location}
                onChange={(e) => setExpForm((prev) => ({ ...prev, location: e.target.value }))}
              />
            </label>
            <label>
              Start date
              <input
                type="date"
                value={expForm.start_date}
                onChange={(e) => setExpForm((prev) => ({ ...prev, start_date: e.target.value }))}
              />
            </label>
            <label>
              End date
              <input
                type="date"
                value={expForm.end_date}
                onChange={(e) => setExpForm((prev) => ({ ...prev, end_date: e.target.value }))}
              />
            </label>
            <label className="inline">
              <input
                type="checkbox"
                checked={expForm.is_current}
                onChange={(e) =>
                  setExpForm((prev) => ({ ...prev, is_current: e.target.checked }))
                }
              />
              Current role
            </label>
            <label>
              Description
              <textarea
                value={expForm.description}
                onChange={(e) =>
                  setExpForm((prev) => ({ ...prev, description: e.target.value }))
                }
              />
            </label>
            <button className="primary" type="submit">
              Add experience
            </button>
          </form>
        </div>
      </div>

      <div className="section">
        <h3>Education</h3>
        <div className="grid">
          {(resume?.education || []).map((edu) => (
            <div key={edu.id} className="card">
              <h4>{edu.school}</h4>
              <p className="muted">{edu.degree}</p>
              <p className="small">{edu.field_of_study}</p>
              <button
                className="ghost"
                type="button"
                onClick={() => deleteItem(`/resume/education/${edu.id}/`)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <div className="card form-card">
          <h4>Add education</h4>
          <form className="form" onSubmit={addEducation}>
            <label>
              School
              <input
                value={eduForm.school}
                onChange={(e) => setEduForm((prev) => ({ ...prev, school: e.target.value }))}
                required
              />
            </label>
            <label>
              Degree
              <input
                value={eduForm.degree}
                onChange={(e) => setEduForm((prev) => ({ ...prev, degree: e.target.value }))}
              />
            </label>
            <label>
              Field of study
              <input
                value={eduForm.field_of_study}
                onChange={(e) =>
                  setEduForm((prev) => ({ ...prev, field_of_study: e.target.value }))
                }
              />
            </label>
            <label>
              Start year
              <input
                type="number"
                value={eduForm.start_year}
                onChange={(e) => setEduForm((prev) => ({ ...prev, start_year: e.target.value }))}
              />
            </label>
            <label>
              End year
              <input
                type="number"
                value={eduForm.end_year}
                onChange={(e) => setEduForm((prev) => ({ ...prev, end_year: e.target.value }))}
              />
            </label>
            <label>
              Grade
              <input
                value={eduForm.grade}
                onChange={(e) => setEduForm((prev) => ({ ...prev, grade: e.target.value }))}
              />
            </label>
            <label>
              Description
              <textarea
                value={eduForm.description}
                onChange={(e) =>
                  setEduForm((prev) => ({ ...prev, description: e.target.value }))
                }
              />
            </label>
            <button className="primary" type="submit">
              Add education
            </button>
          </form>
        </div>
      </div>

      <div className="section">
        <h3>Certifications</h3>
        <div className="grid">
          {(resume?.certifications || []).map((cert) => (
            <div key={cert.id} className="card">
              <h4>{cert.name}</h4>
              <p className="muted">{cert.issuer}</p>
              <p className="small">Issued: {cert.issue_year || "N/A"}</p>
              <button
                className="ghost"
                type="button"
                onClick={() => deleteItem(`/resume/certifications/${cert.id}/`)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <div className="card form-card">
          <h4>Add certification</h4>
          <form className="form" onSubmit={addCertification}>
            <label>
              Name
              <input
                value={certForm.name}
                onChange={(e) => setCertForm((prev) => ({ ...prev, name: e.target.value }))}
                required
              />
            </label>
            <label>
              Issuer
              <input
                value={certForm.issuer}
                onChange={(e) => setCertForm((prev) => ({ ...prev, issuer: e.target.value }))}
              />
            </label>
            <label>
              Issue year
              <input
                type="number"
                value={certForm.issue_year}
                onChange={(e) =>
                  setCertForm((prev) => ({ ...prev, issue_year: e.target.value }))
                }
              />
            </label>
            <label>
              Credential URL
              <input
                value={certForm.credential_url}
                onChange={(e) =>
                  setCertForm((prev) => ({ ...prev, credential_url: e.target.value }))
                }
              />
            </label>
            <button className="primary" type="submit">
              Add certification
            </button>
          </form>
        </div>
      </div>

      <div className="section">
        <h3>Links</h3>
        <div className="grid">
          {(resume?.links || []).map((link) => (
            <div key={link.id} className="card">
              <h4>{link.platform}</h4>
              <p className="muted">{link.username}</p>
              <p className="small">{link.url}</p>
              <button
                className="ghost"
                type="button"
                onClick={() => deleteItem(`/resume/links/${link.id}/`)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
        <div className="card form-card">
          <h4>Add link</h4>
          <form className="form" onSubmit={addLink}>
            <label>
              Platform
              <input
                value={linkForm.platform}
                onChange={(e) => setLinkForm((prev) => ({ ...prev, platform: e.target.value }))}
                required
              />
            </label>
            <label>
              URL
              <input
                value={linkForm.url}
                onChange={(e) => setLinkForm((prev) => ({ ...prev, url: e.target.value }))}
                required
              />
            </label>
            <label>
              Username
              <input
                value={linkForm.username}
                onChange={(e) => setLinkForm((prev) => ({ ...prev, username: e.target.value }))}
              />
            </label>
            <button className="primary" type="submit">
              Add link
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
