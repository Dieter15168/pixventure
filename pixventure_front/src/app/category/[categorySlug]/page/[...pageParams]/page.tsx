// src/app/category/[categorySlug]/page/[...pageParams]/page.tsx
// or you can do something simpler with two routes; here's the "catch-all" style.

"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PostsList from "@/components/PostsList/PostsList";

export default function CategoryPostsPage() {
  const { categorySlug, pageParams } = useParams() as {
    categorySlug: string;
    pageParams?: string[];
  };

  // pageParams might be undefined (for page=1)
  // or ["2"], ["3"], etc. 
  const pageNum = pageParams && pageParams[0] ? parseInt(pageParams[0], 10) : 1;

  const { fetchPostsByCategory } = usePostsAPI();

  // We'll wrap fetchPostsByCategory so that it has the categorySlug built in
  const fetchFunction = async (page: number) => {
    return await fetchPostsByCategory(categorySlug, page);
  };

  return (
    <div>
      <h1>Category: {categorySlug}</h1>
      <PostsList
        fetchFunction={fetchFunction}
        initialPage={pageNum}
      />
    </div>
  );
}
