// src/utils/api/moderation.tsx
"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

export interface ModerationDashboardData {
  posts: any[];
  orphan_media: any[];
}

export interface RejectionReason {
  id: number;
  name: string;
  description?: string;
  order: number;
}

export function useModerationAPI() {
  const axios = useAxios();

  const fetchDashboard =
    useCallback(async (): Promise<ModerationDashboardData> => {
      const res = await axios.get("/moderation/dashboard/");
      return res.data;
    }, [axios]);

  const performModerationAction = useCallback(
    async (payload: any) => {
      const res = await axios.post("/moderation/action/", payload);
      return res.data;
    },
    [axios]
  );

  const fetchActiveRejectionReasons = useCallback(async (): Promise<
    RejectionReason[]
  > => {
    const res = await axios.get("/moderation/rejection-reasons/");
    return res.data as RejectionReason[];
  }, [axios]);

  return {
    fetchDashboard,
    performModerationAction,
    fetchActiveRejectionReasons,
  };
}
