// src/utils/posts.ts
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

export function usePostsAPI() {
  const axios = useAxios();

  const fetchPosts = useCallback(async () => {
    const res = await axios.get("/posts/");
    return res.data.results;
  }, [axios]);

  const fetchPostBySlug = useCallback(
    async (slug: string) => {
      const res = await axios.get(`/posts/?slug=${slug}`);
      return res.data.results[0];
    },
    [axios]
  );

  const fetchPostItems = useCallback(
    async (postId: number) => {
      const res = await axios.get(`/posts/${postId}/items/`);
      return res.data.results;
    },
    [axios]
  );

  const fetchPostItem = useCallback(async (postId: number, itemId: number) => {
    const res = await axios.get(`/posts/${postId}/items/${itemId}/`);
    return res.data;
  }, [axios]);

  return {
    fetchPosts,
    fetchPostBySlug,
    fetchPostItems,
    fetchPostItem,
  };
}
