// src/utils/albumElements.tsx
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

export function useAlbumElementsAPI() {
  const axios = useAxios();

  /**
   * Adds an entity (post or media) to an album.
   * Payload example:
   * {
   *   "element_type": "post",
   *   "element_id": 3
   * }
   */
  const addEntityToAlbum = useCallback(
    async (albumSlug: string, entityType: "post" | "media", entityId: number) => {
      const payload = {
        element_type: entityType,
        element_id: entityId,
      };
      const res = await axios.post(`/albums/${albumSlug}/elements/`, payload);
      return res.data;
    },
    [axios]
  );

  const removeEntityFromAlbum = useCallback(
    async (albumSlug: string, albumElementId: number) => {
      const res = await axios.delete(`/albums/${albumSlug}/elements/${albumElementId}/`);
      return res.data;
    },
    [axios]
  );

  return {
    addEntityToAlbum,
    removeEntityFromAlbum,
  };
}
