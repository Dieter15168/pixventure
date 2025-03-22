// src/app/best-posts/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";

export default function BestPostsPage() {
  // Set the basePath to "/best-posts" so that page 1 is /best-posts,
  // and other pages become /best-posts/page/2, etc.
  const basePath = "/best-posts";
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  const { fetchFeaturedPosts } = usePostsAPI();

  // Define the fetch function to get featured posts (paginated)
  const fetchFunction = async (page: number) => {
    return await fetchFeaturedPosts(page);
  };

  return (
    <div>
      <h1>Featured Posts</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title="Featured Posts"
        ListComponent={PostsList}
      />
    </div>
  );
}
