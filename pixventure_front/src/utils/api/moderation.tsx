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

export interface DuplicateClusterItem {
  id: number;
  media_type: string;
  status: string;
  thumbnail_url: string;
  width: number | null;
  height: number | null;
  file_size: number | null;
  is_best_item: boolean;
}

export interface DuplicateCluster {
  id: number;
  hash_type_name: string;
  hash_value: string;
  status: string;
  best_item_id: number | null;
  items: DuplicateClusterItem[];
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
