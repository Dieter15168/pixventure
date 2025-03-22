// src/app/[mainCategorySlug]/[postSlug]/items/[[...pageParams]]/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PostItemsPaginated from "./PostItemsPaginated";

export default function PostItemsPage() {
  // Get postSlug from the route (we assume mainCategorySlug is handled elsewhere)
  const { postSlug } = useParams() as { postSlug: string };
  const { fetchPostBySlug } = usePostsAPI();

  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!postSlug) return;
    (async () => {
      setLoading(true);
      try {
        const data = await fetchPostBySlug(postSlug);
        setPost(data);
      } catch (err: any) {
        setError(err.message || "Error loading post");
      } finally {
        setLoading(false);
      }
    })();
  }, [postSlug, fetchPostBySlug]);

  if (loading) return <p>Loading post info...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!post) return <p>No post found for slug: {postSlug}</p>;

  // Once post meta is loaded, render the child component.
  return <PostItemsPaginated post={post} />;
}
