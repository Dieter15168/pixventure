// src/utils/albums.tsx
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

export function useAlbumsAPI() {
  const axios = useAxios();

  // GET /api/albums/
  const fetchAlbums = useCallback(async () => {
    const res = await axios.get("/albums/mine/");
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

  // POST /api/albums/new/
  const createAlbum = useCallback(
    async (albumData: {
      name: string;
      is_public: boolean;
      show_creator_to_others?: boolean;
    }) => {
      const res = await axios.post("/albums/new/", albumData);
      return res.data;
    },
    [axios]
  );

  return { fetchAlbums, fetchAlbumBySlug, createAlbum };
}
