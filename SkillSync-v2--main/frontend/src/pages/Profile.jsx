import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, profile, saveProfile } = useAuth();
  const [form, setForm] = useState({
    username: "",
    email: "",
    name: "",
    company_name: "",
    skills: "",
    experience_level: "Mid",
    hourly_rate: "",
    bio: "",
    portfolio_links: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user || !profile) return;
    setForm((prev) => ({
      ...prev,
      username: user.username || "",
      email: user.email || "",
      name: profile.name || "",
      company_name: profile.company_name || "",
      skills: (profile.skills || []).join(", "),
      experience_level: profile.experience_level || "Mid",
      hourly_rate: profile.hourly_rate || "",
      bio: profile.bio || "",
      portfolio_links: (profile.portfolio_links || []).join(", "),
    }));
  }, [user, profile]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    const payload = {
      user: {
        username: form.username,
        email: form.email,
      },
      profile: {
        name: form.name,
      },
    };

    if (user?.role === "client") {
      payload.profile.company_name = form.company_name;
    } else {
      payload.profile.skills = form.skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      payload.profile.experience_level = form.experience_level;
      payload.profile.hourly_rate = form.hourly_rate;
      payload.profile.bio = form.bio;
      payload.profile.portfolio_links = form.portfolio_links
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }

    try {
      await saveProfile(payload);
      setMessage("Profile updated");
    } catch (err) {
      setError(err.message || "Unable to update profile");
    }
  };

  return (
    <div className="page-shell">
      <div className="card form-card">
        <h2>Your profile</h2>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Username
            <input name="username" value={form.username} onChange={handleChange} />
          </label>
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={handleChange} />
          </label>
          <label>
            Name
            <input name="name" value={form.name} onChange={handleChange} />
          </label>

          {user?.role === "client" ? (
            <label>
              Company name
              <input name="company_name" value={form.company_name} onChange={handleChange} />
            </label>
          ) : (
            <>
              <label>
                Skills
                <input name="skills" value={form.skills} onChange={handleChange} />
              </label>
              <label>
                Experience level
                <select
                  name="experience_level"
                  value={form.experience_level}
                  onChange={handleChange}
                >
                  <option value="Junior">Junior</option>
                  <option value="Mid">Mid</option>
                  <option value="Senior">Senior</option>
                </select>
              </label>
              <label>
                Hourly rate
                <input
                  name="hourly_rate"
                  type="number"
                  value={form.hourly_rate}
                  onChange={handleChange}
                />
              </label>
              <label>
                Bio
                <textarea name="bio" value={form.bio} onChange={handleChange} />
              </label>
              <label>
                Portfolio links
                <input
                  name="portfolio_links"
                  value={form.portfolio_links}
                  onChange={handleChange}
                />
              </label>
            </>
          )}

          {error ? <div className="error">{error}</div> : null}
          {message ? <div className="success">{message}</div> : null}
          <button className="primary" type="submit">
            Save changes
          </button>
        </form>
      </div>
    </div>
  );
}
