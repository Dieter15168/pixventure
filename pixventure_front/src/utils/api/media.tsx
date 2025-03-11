// src/utils/api/media.ts
"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

/**
 * Provides a function to upload a single file to "/api/media/new/".
 */
export function useMediaAPI() {
  const axios = useAxios(); // your specialized Axios w/ auth tokens, interceptors, etc.

  const uploadFile = useCallback(
    async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      // Adjust if your Django endpoint is different
      const res = await axios.post("/media/new/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      return res.data; // e.g., the newly created MediaItem
    },
    [axios]
  );

  return { uploadFile };
}
