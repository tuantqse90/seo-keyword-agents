"use client";

import { useState, useEffect, useCallback } from "react";
import { loginApi, registerApi, getMe } from "@/lib/api";
import type { AuthUser } from "@/lib/api";

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("token");
          localStorage.removeItem("refresh_token");
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await loginApi(email, password);
    localStorage.setItem("token", res.token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setUser(res.user);
    return res.user;
  }, []);

  const register = useCallback(async (email: string, password: string, name: string) => {
    const res = await registerApi(email, password, name);
    localStorage.setItem("token", res.token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setUser(res.user);
    return res.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    window.location.href = "/login";
  }, []);

  const isAdmin = user?.role === "admin";

  return { user, loading, login, register, logout, isAdmin };
}
