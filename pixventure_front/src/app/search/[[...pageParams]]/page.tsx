// src/app/search/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useSearchParams } from "next/navigation";
import { useSearchAPI } from "@/utils/api/search";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import PostsList from "@/components/PostsList/PostsList";

/**
 * SearchResultsPage
 *
 * Displays search results based on the 'q' query parameter with integrated pagination.
 * Supports both /search and /search/page/N routes.
 */
export default function SearchResultsPage() {
  // Retrieve the search query from URL parameters.
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  
  // Define the base path WITHOUT the query parameters.
  const basePath = `/search`;
  
  // Use the custom pagination hook with the clean base path.
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);
  
  // Custom URL builder: append the query string (if any) after generating the paginated path.
  const customBuildPageUrl = (page: number) => {
    const url = buildPageUrl(page);
    return query ? `${url}?q=${encodeURIComponent(query)}` : url;
  };

  // API function to fetch search results (wrapped to include the current query).
  const { fetchSearchResults } = useSearchAPI();
  const fetchFunction = async (page: number) =>
    await fetchSearchResults(query, page);

  return (
    <div>
      <h1>Search results for "{query}"</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={customBuildPageUrl}
        fetchFunction={fetchFunction}
        title={`Search results for "${query}"`}
        ListComponent={PostsList} // Reuse the existing posts list component.
      />
    </div>
  );
}
