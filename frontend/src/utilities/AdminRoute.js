import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const AdminRoute = ({ children }) => {
  const { user, groups, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!user || !groups.includes('admin')) {
    return <Navigate to="/admin" />;
  }

  return children;
};

export default AdminRoute;
