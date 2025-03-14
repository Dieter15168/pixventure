// src/utils/api/posts.tsx
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

interface CreatePostPayload {
  name: string;
  items: number[];        // array of media IDs
  featured_item: number;
  terms: number[];        // array of term IDs
}

export function usePostsAPI() {
  const axios = useAxios();

  const fetchPosts = useCallback(async () => {
    const res = await axios.get("/posts/");
    return res.data.results;
  }, [axios]);

  const fetchPostBySlug = useCallback(async (slug: string) => {
    const res = await axios.get(`/posts/?slug=${slug}`);
    return res.data.results[0];
  }, [axios]);

  const fetchPostItems = useCallback(async (postId: number) => {
    const res = await axios.get(`/posts/${postId}/items/`);
    return res.data.results;
  }, [axios]);

  const fetchPostItem = useCallback(async (postId: number, itemId: number) => {
    const res = await axios.get(`/posts/${postId}/items/${itemId}/`);
    return res.data;
  }, [axios]);

  const fetchPostMeta = useCallback(async (postId: number) => {
    const res = await axios.get(`/posts/${postId}/meta/`);
    return res.data; // { id, name, slug, owner_username, categories, tags, can_edit }
  }, [axios]);

  const deletePost = useCallback(async (postId: number) => {
    const res = await axios.delete(`/posts/${postId}/edit/`);
    return res.data;
  }, [axios]);

  const fetchMyPosts = useCallback(async () => {
    const res = await axios.get("/posts/mine/");
    return res.data.results;
  }, [axios]);

  const createPost = useCallback(async (payload: CreatePostPayload) => {
    const res = await axios.post("/posts/new/", payload);
    return res.data;
  }, [axios]);

  return {
    fetchPosts,
    fetchPostBySlug,
    fetchPostItems,
    fetchPostItem,
    fetchPostMeta,
    deletePost,
    fetchMyPosts,
    createPost,
  };
}
