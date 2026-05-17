import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { clearTokens, getAccessToken, getMe, login as apiLogin, register as apiRegister, updateMe } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadMe = async () => {
    try {
      const data = await getMe();
      setUser(data.user);
      setProfile(data.profile);
    } catch (error) {
      clearTokens();
      setUser(null);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (getAccessToken()) {
      loadMe();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (identifier, password) => {
    const data = await apiLogin(identifier, password);
    await loadMe();
    return data;
  };

  const register = async (payload) => {
    const data = await apiRegister(payload);
    return data;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    setProfile(null);
  };

  const saveProfile = async (payload) => {
    const data = await updateMe(payload);
    setUser(data.user || user);
    setProfile(data.profile || profile);
    return data;
  };

  const value = useMemo(
    () => ({
      user,
      profile,
      loading,
      login,
      register,
      logout,
      saveProfile,
      refresh: loadMe,
    }),
    [user, profile, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
