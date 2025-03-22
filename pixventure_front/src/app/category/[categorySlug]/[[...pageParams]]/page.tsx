// src/app/category/[categorySlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";

export default function CategoryPage() {
  const { categorySlug, pageParams } = useParams() as {
    categorySlug: string;
    pageParams?: string[];
  };

  // Define the base path for page 1, e.g. "/category/test-category"
  const basePath = `/category/${categorySlug}`;
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  const { fetchPostsByCategory } = usePostsAPI();
  const fetchFunction = async (page: number) => {
    return await fetchPostsByCategory(categorySlug, page);
  };

  return (
    <div>
      <h1>Category: {categorySlug}</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title={`Posts in "${categorySlug}"`}
      />
    </div>
  );
}
