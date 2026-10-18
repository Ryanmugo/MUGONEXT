import { createContext, useContext, useEffect, useMemo, useState } from "react";

import {
  login as loginRequest,
  logout as logoutRequest,
  getCompany,
} from "../services/api";

const AuthContext = createContext(null);

const TOKEN_KEY = "mugonext_access_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));

  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  /*

# RESTORE EXISTING SESSION

*/

  useEffect(() => {
    async function restoreSession() {
      if (!token) {
        setCompany(null);
        setLoading(false);
        return;
      }

      try {
        const companyData = await getCompany();

        setCompany(
          Array.isArray(companyData)
            ? companyData[0] || null
            : companyData || null,
        );
      } catch (error) {
        console.error("Session restore failed:", error);

        // Token is no longer valid.
        localStorage.removeItem(TOKEN_KEY);

        setToken(null);
        setCompany(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, [token]);
  /*

# LOGIN

*/

  async function login(email, password) {
    const data = await loginRequest(email.trim(), password);

    if (!data?.access_token) {
      throw new Error("Login succeeded but no access token was returned.");
    }

    // Save token immediately.
    localStorage.setItem(TOKEN_KEY, data.access_token);

    setToken(data.access_token);

    /*
  Load the company associated with the authenticated user.
*/

    try {
      const companyData = await getCompany();

      setCompany(
        Array.isArray(companyData)
          ? companyData[0] || null
          : companyData || null,
      );
    } catch (error) {
      console.error("Unable to load company after login:", error);

      /*
    Do not destroy a successful login simply because
    company loading failed.
  */

      setCompany(null);
    }

    return data;
  }

  /*

# LOGOUT

*/

  async function logout() {
    /*
Try to tell the backend that the user is logging out.

```
  Even if the backend request fails, we STILL clear the
  local session below.
*/

    try {
      await logoutRequest();
    } catch (error) {
      console.error("Backend logout failed:", error);
    } finally {
      /*
    IMPORTANT:

    Always destroy the local authentication session.
  */

      localStorage.removeItem(TOKEN_KEY);

      setToken(null);
      setCompany(null);
    }
  }

  /*

# AUTHENTICATED USER

*/

  const user = token
    ? {
        authenticated: true,
      }
    : null;

  /*

# CONTEXT VALUE

*/

  const value = useMemo(
    () => ({
      token,
      user,
      company,
      loading,

      isAuthenticated: Boolean(token),

      login,
      logout,
    }),
    [token, user, company, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
