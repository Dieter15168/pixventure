// src/utils/api/posts.ts
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

  // 1) Fetch all posts (paginated, if the endpoint supports it)
  const fetchPosts = useCallback(
    async (page = 1) => {
      const res = await axios.get(`/posts/?page=${page}`);
      // Expect paginated data: { results, current_page, total_pages, ... }
      return res.data;
    },
    [axios]
  );

  // 2) Fetch single post by slug
  const fetchPostBySlug = useCallback(
    async (slug: string) => {
      const res = await axios.get(`/posts/?slug=${slug}`);
      return res.data.results[0];
    },
    [axios]
  );

  // 3) Fetch items belonging to a specific post (paginated)
  const fetchPostItems = useCallback(
    async (postId: number, page = 1) => {
      const res = await axios.get(`/posts/${postId}/items/?page=${page}`);
      // Expect { results, current_page, total_pages, ... }
      return res.data;
    },
    [axios]
  );

  // 4) Fetch a specific post item
  const fetchPostItem = useCallback(
    async (postId: number, itemId: number) => {
      const res = await axios.get(`/posts/${postId}/items/${itemId}/`);
      return res.data;
    },
    [axios]
  );

  // 5) Fetch meta info about a post (owner, categories, tags, etc.)
  const fetchPostMeta = useCallback(
    async (postId: number) => {
      const res = await axios.get(`/posts/${postId}/meta/`);
      // ex. { id, name, slug, owner_username, categories, tags, can_edit }
      return res.data;
    },
    [axios]
  );

  // 6) Delete a post
  const deletePost = useCallback(
    async (postId: number) => {
      const res = await axios.delete(`/posts/${postId}/edit/`);
      return res.data;
    },
    [axios]
  );

  // 7) Fetch posts belonging to the current user
  const fetchMyPosts = useCallback(
    async () => {
      const res = await axios.get("/posts/mine/");
      return res.data.results;
    },
    [axios]
  );

  // 8) Create a new post
  const createPost = useCallback(
    async (payload: CreatePostPayload) => {
      const res = await axios.post("/posts/new/", payload);
      return res.data;
    },
    [axios]
  );

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
