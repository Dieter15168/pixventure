// src/app/page.tsx
"use client";

import React from "react";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";
import RandomMediaWidget from "@/components/RandomMediaWidget";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePostsAPI } from "@/utils/api/posts";

export default function HomePage() {
  // For the featured posts route.
  const basePath = "/best-posts";
  const { currentPage } = usePaginatedRoute(basePath, 1);
  const buildPageUrl = (p: number) => (p === 1 ? basePath : `${basePath}/page/${p}`);

  const { fetchFeaturedPosts } = usePostsAPI();
  const fetchFunction = async (page: number) => await fetchFeaturedPosts(page);

  return (
    <div>
      <hr/>
      <RandomMediaWidget count={4} />
      <hr/>
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
