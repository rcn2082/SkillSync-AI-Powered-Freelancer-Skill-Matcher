import React from "react";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">AI-Powered Freelancer Matching</p>
          <h1>SkillSync</h1>
          <p className="subtitle">
            Match freelancers to projects using NLP-based compatibility scoring. Remove
            guesswork, surface great fits, and hire with confidence.
          </p>
          <div className="cta-row">
            <Link to="/register" className="primary-link">
              Start matching
            </Link>
            <Link to="/login" className="ghost-link">
              Sign in
            </Link>
          </div>
          <p className="note">Smart ranking across skills, experience, and ratings.</p>
        </div>
        <div className="panel">
          <div className="panel-card">
            <h3>Freelancer</h3>
            <ul>
              <li>Create a rich profile</li>
              <li>See ranked projects</li>
              <li>Track applications</li>
            </ul>
          </div>
          <div className="panel-card">
            <h3>Client</h3>
            <ul>
              <li>Post project needs</li>
              <li>Compare top matches</li>
              <li>Shortlist instantly</li>
            </ul>
          </div>
        </div>
      </header>

      <section className="metrics">
        <div>
          <h2>75%+ Matching Accuracy</h2>
          <p>Weighted scoring across skills, experience, and ratings.</p>
        </div>
        <div>
          <h2>&lt; 3s Match Time</h2>
          <p>TF-IDF vectorization with cosine similarity.</p>
        </div>
        <div>
          <h2>Transparent Scoring</h2>
          <p>See matched skills and explain each score.</p>
        </div>
      </section>
    </div>
  );
}
