// src/utils/useAxios.ts
"use client";

import { useMemo } from "react";
import axios from "axios";
import { useAuth } from "../contexts/AuthContext";

export default function useAxios() {
  const { token, logout } = useAuth();

  const axiosInstance = useMemo(() => {
    const instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL, // e.g. "http://127.0.0.1:8000/api"
    });

    // Attach token if available
    instance.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Handle 401 => log out
    instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          logout();
        }
        return Promise.reject(error);
      }
    );

    return instance;
  }, [token, logout]);

  return axiosInstance;
}
