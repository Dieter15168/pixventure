// src/app/posts/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";

export default function AllPostsPage() {
  const basePath = "/posts";
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);
  const { fetchPosts } = usePostsAPI();

  const fetchFunction = async (page: number) => {
    return await fetchPosts(page);
  };

  return (
    <div>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title="All Posts"
        ListComponent={PostsList}
      />
    </div>
  );
}
