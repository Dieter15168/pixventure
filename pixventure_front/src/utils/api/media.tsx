// src/utils/api/media.ts
"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

export interface MinimalMediaItemDTO {
  id: number;
  media_type_str: "photo" | "video" | "unknown";
  status_str: string;
  thumbnail_url?: string | null;
  width?: number | null;
  height?: number | null;
  file_size?: number | null;
}

export function useMediaAPI() {
  const axios = useAxios(); // your specialized Axios w/ auth tokens, interceptors, etc.

  const uploadFile = useCallback(
    async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post("/media/new/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
    [axios]
  );

  const fetchAvailableMedia = useCallback(async (): Promise<
    MinimalMediaItemDTO[]
  > => {
    const res = await axios.get("/media/unpublished/");
    return res.data;
  }, [axios]);

  return { uploadFile, fetchAvailableMedia };
}
