// src/app/page.tsx  (the Home page -> featuring posts)

"use client";

import React from "react";
import { usePostsAPI } from "../utils/api/posts";
import PostsList from "../components/PostsList/PostsList";

export default function Home() {
  const { fetchFeaturedPosts } = usePostsAPI();

  return (
    <div>
      <h1>Featured Posts</h1>
      <PostsList fetchFunction={fetchFeaturedPosts} />
    </div>
  );
}
