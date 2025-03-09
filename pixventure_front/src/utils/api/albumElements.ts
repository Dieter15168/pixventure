// src/utils/albumElements.ts
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

/**
 * Hook for performing album element operations, such as adding or removing a post from an album.
 */
export function useAlbumElementsAPI() {
  const axios = useAxios();

  /**
   * Adds a post to an album.
   *
   * @param albumSlug - The slug of the album.
   * @param postId - The ID of the post to add.
   */
  const addPostToAlbum = useCallback(async (albumSlug: string, postId: number) => {
    const res = await axios.post(`/albums/${albumSlug}/elements/`, {
      element_type: "post",
      element_post: postId,
    });
    return res.data;
  }, [axios]);

  /**
   * Removes a post from an album.
   *
   * @param albumSlug - The slug of the album.
   * @param albumElementId - The album element ID for the post.
   */
  const removePostFromAlbum = useCallback(async (albumSlug: string, albumElementId: number) => {
    const res = await axios.delete(`/albums/${albumSlug}/elements/${albumElementId}/`);
    return res.data;
  }, [axios]);

  return {
    addPostToAlbum,
    removePostFromAlbum,
  };
}
