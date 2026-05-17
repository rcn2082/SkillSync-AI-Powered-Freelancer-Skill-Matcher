import React from "react";
import { useAuth } from "../context/AuthContext";
import FreelancerDashboard from "./FreelancerDashboard";
import ClientDashboard from "./ClientDashboard";

export default function Dashboard() {
  const { user } = useAuth();
  if (!user) return null;
  return user.role === "client" ? <ClientDashboard /> : <FreelancerDashboard />;
}
