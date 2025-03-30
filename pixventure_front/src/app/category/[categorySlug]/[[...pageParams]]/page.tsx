// src/app/category/[categorySlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";

/**
 * CategoryPage
 *
 * Displays posts filtered by a specific category with integrated pagination.
 * Supports both /category/[categorySlug] and /category/[categorySlug]/page/N routes.
 */
export default function CategoryPage() {
  // Destructure the categorySlug from the route parameters.
  const { categorySlug } = useParams() as { categorySlug: string };

  // Define the base path for page 1, e.g., "/category/test-category"
  const basePath = `/category/${categorySlug}`;

  // Custom hook parses pagination info from the URL and provides URL building.
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  // API function to fetch posts by category.
  const { fetchPostsByCategory } = usePostsAPI();
  const fetchFunction = async (page: number) => await fetchPostsByCategory(categorySlug, page);

  return (
    <div>
      <h1>Category: {categorySlug}</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title={`Posts in "${categorySlug}"`}
        ListComponent={PostsList} // Pass the posts list component as required
      />
    </div>
  );
}
