// src/utils/api/albums.tsx
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

export function useAlbumsAPI() {
  const axios = useAxios();

  // GET /api/albums/?page=<N>
  const fetchAlbums = useCallback(
    async (page = 1) => {
      const res = await axios.get(`/albums/?page=${page}`);
      return res.data;
    },
    [axios]
  );

  // GET /api/albums/mine/ - Albums owned by the current user
  const fetchMyAlbums = useCallback(async () => {
    const res = await axios.get("/albums/mine/");
    return res.data.results;
  }, [axios]);

  // GET /api/albums/<slug>/
  const fetchAlbumBySlug = useCallback(
    async (slug: string) => {
      const res = await axios.get(`/albums/${slug}/`);
      return res.data;
    },
    [axios]
  );

  // GET /api/albums/<slug>/elements/?page=<N>
  // => returns paginated results
  const fetchAlbumElementsBySlug = useCallback(
    async (slug: string, page = 1) => {
      const res = await axios.get(`/albums/${slug}/elements/?page=${page}`);
      return res.data; // { results, current_page, total_pages, ... }
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

  return {
    fetchAlbums,
    fetchMyAlbums,
    fetchAlbumBySlug,
    fetchAlbumElementsBySlug,
    createAlbum,
  };
}
