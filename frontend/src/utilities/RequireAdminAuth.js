// src/utilities/RequireAdminAuth.js
import React from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function RequireAdminAuth({ children }) {
  const adminToken = localStorage.getItem("adminToken");
  const location = useLocation();

  if (!adminToken) {
    return <Navigate to="/admin" state={{ from: location }} replace />;
  }

  return children;
}
