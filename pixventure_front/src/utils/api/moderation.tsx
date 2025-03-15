// src/utils/api/moderation.tsx
"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

export interface ModerationDashboardData {
  posts: any[];         // Adjust with your PostModerationSerializer output type
  orphan_media: any[];  // Adjust with your MediaItemModerationSerializer output type
}

export function useModerationAPI() {
  const axios = useAxios();

  const fetchDashboard = useCallback(async (): Promise<ModerationDashboardData> => {
    const res = await axios.get("/moderation/dashboard/");
    return res.data;
  }, [axios]);

  const performModerationAction = useCallback(async (payload: any) => {
    const res = await axios.post("/moderation/action/", payload);
    return res.data;
  }, [axios]);

  return { fetchDashboard, performModerationAction };
}
