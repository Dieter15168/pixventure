// src/app/page.tsx
"use client";

import React from "react";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";
import RandomMediaWidget from "@/components/RandomMediaWidget";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePostsAPI } from "@/utils/api/posts";
import Link from "next/link";

export default function HomePage() {
  // For the featured posts route.
  const basePath = "/best-posts";
  const { currentPage } = usePaginatedRoute(basePath, 1);
  const buildPageUrl = (p: number) =>
    p === 1 ? basePath : `${basePath}/page/${p}`;

  const { fetchFeaturedPosts } = usePostsAPI();
  const fetchFunction = async (page: number) => await fetchFeaturedPosts(page);

  return (
    <div>
      {/* Random Items Section */}
      <div className="mb-4">
        <div className="d-flex align-items-center mb-3">
          <h2 className="mb-0 me-3">Random Items</h2>
          <Link href="/random-items" className="btn btn-link p-0">
            See More
          </Link>
        </div>
        {/* Display a smaller preview (4 items) on the main page */}
        <RandomMediaWidget count={4} />
      </div>
      <hr />
      {/* Featured Posts Section */}
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
