// src/utilities/RequireUserAuth.js
import React from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function RequireUserAuth({ children }) {
  const token = localStorage.getItem("accessToken"); // User token
  const location = useLocation();

  // If no user token, redirect to landing or signup
  if (!token) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return children;
}
