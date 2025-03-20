// src/app/posts/page.tsx
"use client";

import React from "react";
import { usePostsAPI } from "../../utils/api/posts";
import PostsList from "../../components/PostsList/PostsList";

export default function AllPostsPage() {
  const { fetchPosts } = usePostsAPI();

  return (
    <div>
      <h1>All Posts</h1>
      <PostsList fetchFunction={fetchPosts} />
    </div>
  );
}
