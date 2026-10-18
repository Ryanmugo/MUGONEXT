import React from "react";

import { Routes, Route, Navigate, useLocation } from "react-router-dom";

import Dashboard from "./Dashboard";

import Login from "./pages/Login";
import Team from "./pages/Team";
import Datasets from "./pages/Datasets";
import Forecasts from "./pages/Forecasts";
import Recommendations from "./pages/Recommendations";
import Settings from "./pages/Settings";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

import { useAuth } from "./context/AuthContext";

/*

# PROTECTED ROUTE

*/

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  /*
Wait until AuthContext finishes checking the
existing session.
*/

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b0f14] text-slate-200">
        {" "}
        <div className="text-center">
          {" "}
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-500" />
          <p className="mt-4 text-sm text-slate-500">
            Restoring your MUGONEXT session...
          </p>
        </div>
      </div>
    );
  }

  /*
No valid authentication token:
send the user to login.



*/

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  /*
User is authenticated.
Allow access to the application.
*/

  return children;
}

/*

# PUBLIC ROUTE

*/

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  /*
Wait for authentication restoration.
*/

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b0f14] text-slate-200">
        {" "}
        <div className="text-center">
          {" "}
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-500" />
          <p className="mt-4 text-sm text-slate-500">Loading MUGONEXT...</p>
        </div>
      </div>
    );
  }

  /*
If already logged in, don't allow the user to
unnecessarily return to the login page.
*/

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

/*

# APP

*/

function App() {
  return (
    <Routes>
      {/* =================================================
AUTHENTICATION
================================================= */}

      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      <Route path="/forgot-password" element={<ForgotPassword />} />

      <Route path="/reset-password" element={<ResetPassword />} />

      {/* =================================================
      MAIN APPLICATION
      ================================================= */}

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/datasets"
        element={
          <ProtectedRoute>
            <Datasets />
          </ProtectedRoute>
        }
      />

      <Route
        path="/forecasts"
        element={
          <ProtectedRoute>
            <Forecasts />
          </ProtectedRoute>
        }
      />

      <Route
        path="/recommendations"
        element={
          <ProtectedRoute>
            <Recommendations />
          </ProtectedRoute>
        }
      />

      <Route
        path="/team"
        element={
          <ProtectedRoute>
            <Team />
          </ProtectedRoute>
        }
      />

      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />

      {/* =================================================
      DEFAULT ROUTE
      ================================================= */}

      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* =================================================
      UNKNOWN ROUTES
      ================================================= */}

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
