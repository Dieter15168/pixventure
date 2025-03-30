// src/app/tag/[tagSlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";

/**
 * TagListingPage
 *
 * Displays posts filtered by a specific tag with integrated pagination.
 * Supports both /tag/[tagSlug] and /tag/[tagSlug]/page/N routes.
 */
export default function TagListingPage() {
  // Destructure the tagSlug from the route parameters.
  const { tagSlug } = useParams() as { tagSlug: string };

  // Define the base path for page 1, e.g., "/tag/test-tag"
  const basePath = `/tag/${tagSlug}`;

  // Custom hook parses pagination info from the URL and provides URL building.
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  // API function to fetch posts by tag.
  const { fetchPostsByTag } = usePostsAPI();
  const fetchFunction = async (page: number) => await fetchPostsByTag(tagSlug, page);

  return (
    <div>
      <h1>Tag: {tagSlug}</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title={`Posts tagged with "${tagSlug}"`}
        ListComponent={PostsList} // Pass the posts list component as required
      />
    </div>
  );
}
