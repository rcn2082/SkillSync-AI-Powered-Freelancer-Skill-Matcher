import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

export default function Register() {
  const navigate = useNavigate();
  const { register, login } = useAuth();
  const [role, setRole] = useState("freelancer");
  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    confirm_password: "",
    name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!passwordPattern.test(form.password)) {
      setError(
        "Password must be at least 8 characters and include uppercase, lowercase, number, and special character."
      );
      return;
    }

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    const payload = {
      email: form.email,
      username: form.username || undefined,
      password: form.password,
      confirm_password: form.confirm_password,
      role,
      name: form.name,
    };

    try {
      await register(payload);
      await login(form.email || form.username, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="card form-card">
        <h2>Create your account</h2>
        <p className="muted">Pick a role to unlock tailored workflows.</p>

        <div className="oauth">
          <button className="google" type="button">
            Continue with Google
          </button>
          <div className="divider">
            <span>Or sign up with email</span>
          </div>
        </div>

        <div className="toggle">
          <button
            type="button"
            className={role === "freelancer" ? "active" : ""}
            onClick={() => setRole("freelancer")}
          >
            Freelancer
          </button>
          <button
            type="button"
            className={role === "client" ? "active" : ""}
            onClick={() => setRole("client")}
          >
            Client
          </button>
        </div>

        <form onSubmit={handleSubmit} className="form" autoComplete="off">
          <label>
            Full name
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>
          <label>
            Email
            <input
              name="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Username (optional)
            <input
              name="username"
              autoComplete="off"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck="false"
              value={form.username}
              onChange={handleChange}
            />
          </label>

          <label>
            Password
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={form.password}
              onChange={handleChange}
              minLength={8}
              required
            />
            <span className="hint">
              Tip: Chrome can suggest a strong password when you focus this field.
            </span>
          </label>
          <label>
            Confirm password
            <input
              name="confirm_password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={form.confirm_password}
              onChange={handleChange}
              minLength={8}
              required
            />
          </label>
          <label className="inline">
            <input
              type="checkbox"
              checked={showPassword}
              onChange={(e) => setShowPassword(e.target.checked)}
            />
            Show password
          </label>

          {error ? <div className="error">{error}</div> : null}
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
