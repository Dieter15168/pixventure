// src/app/tag/[tagSlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";

export default function TagListingPage() {
  const { tagSlug, pageParams } = useParams() as {
    tagSlug: string;
    pageParams?: string[];
  };

  // Define the base path for page 1. For example: "/tag/test-tag"
  const basePath = `/tag/${tagSlug}`;

  // Use our custom hook to parse the route and build URLs.
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  const { fetchPostsByTag } = usePostsAPI();

  // Define a fetch function that calls our API with tagSlug and page.
  const fetchFunction = async (page: number) => {
    return await fetchPostsByTag(tagSlug, page);
  };

  return (
    <div>
      <h1>Tag: {tagSlug}</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title={`Posts tagged with "${tagSlug}"`}
      />
    </div>
  );
}
