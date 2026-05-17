import React from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  const links = user
    ? [
        { label: "Dashboard", to: "/dashboard" },
        { label: "Projects", to: "/projects" },
        { label: "Applications", to: "/applications" },
        ...(user.role === "freelancer" ? [{ label: "Resume", to: "/resume" }] : []),
        { label: "Profile", to: "/profile" },
      ]
    : [
        { label: "Home", to: "/" },
        { label: "Login", to: "/login" },
        { label: "Register", to: "/register" },
      ];

  return (
    <nav className="nav">
      <Link to="/" className="brand">
        SkillSync
      </Link>
      <div className="nav-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            {link.label}
          </NavLink>
        ))}
      </div>
      <div className="nav-actions">
        {user ? (
          <>
            <span className="pill">{user.role}</span>
            <button className="ghost" onClick={logout} type="button">
              Log out
            </button>
          </>
        ) : (
          <Link to="/login" className="primary-link">
            Get started
          </Link>
        )}
      </div>
    </nav>
  );
}
