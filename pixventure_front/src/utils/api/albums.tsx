// src/utils/albums.ts
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

export function useAlbumsAPI() {
  const axios = useAxios();

  // GET /api/albums/
  const fetchAlbums = useCallback(async () => {
    const res = await axios.get("/albums/");
    return res.data.results;
  }, [axios]);

  // GET /api/albums/<slug>/
  const fetchAlbumBySlug = useCallback(
    async (slug: string) => {
      const res = await axios.get(`/albums/${slug}/`);
      return res.data;
      // Format: { album: {...}, album_elements: [...], ...}
    },
    [axios]
  );

  return { fetchAlbums, fetchAlbumBySlug };
}
