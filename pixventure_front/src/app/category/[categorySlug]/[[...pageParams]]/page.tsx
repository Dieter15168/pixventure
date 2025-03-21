// src/app/category/[categorySlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PostsList from "@/components/PostsList/PostsList";

export default function CategoryListingPage() {
  const router = useRouter();
  const { categorySlug, pageParams } = useParams() as {
    categorySlug: string;
    pageParams?: string[];
  };

  // Default page=1
  let currentPage = 1;

  // If the URL is something like "/category/food/page/2", 
  // then pageParams might be ["page", "2"]
  if (pageParams && pageParams[0] === "page") {
    const possiblePageNumber = pageParams[1];
    if (possiblePageNumber) {
      currentPage = parseInt(possiblePageNumber, 10) || 1;
    }
  }

  const { fetchPostsByCategory } = usePostsAPI();

  // We'll pass a function that calls the correct backend route
  const fetchFunction = async (page: number) => {
    return fetchPostsByCategory(categorySlug, page);
  };

  // If we have "/category/[categorySlug]/page" with no number, 
  // e.g. "/category/food/page", we can redirect to page=1
  if (pageParams && pageParams[0] === "page" && pageParams.length === 1) {
    router.replace(`/category/${categorySlug}/page/1`);
    return null; // short-circuit
  }

  return (
    <div>
      <h1>Category: {categorySlug}</h1>
      <PostsList fetchFunction={fetchFunction} initialPage={currentPage} />
    </div>
  );
}
