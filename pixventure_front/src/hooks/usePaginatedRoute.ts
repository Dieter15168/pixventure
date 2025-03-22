// src/utils/hooks/usePaginatedRoute.ts
"use client";

import { useParams } from "next/navigation";

/**
 * Derives the current page directly from route parameters.
 * This avoids an initial state of 1 and then updating after mount.
 * @param basePath The base path for page 1 (e.g. "/posts", "/tag/mytag", etc.)
 * @param defaultPage Defaults to 1.
 */
export function usePaginatedRoute(basePath: string, defaultPage: number = 1) {
  // Read the route params synchronously
  const { pageParams } = useParams() as { pageParams?: string[] };

  // Compute currentPage immediately.
  const currentPage =
    pageParams && pageParams[0] === "page" && pageParams[1]
      ? parseInt(pageParams[1], 10) || defaultPage
      : defaultPage;

  const buildPageUrl = (page: number) =>
    page === 1 ? basePath : `${basePath}/page/${page}`;

  return { currentPage, buildPageUrl };
}
