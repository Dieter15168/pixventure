// src/utils/api/search.ts
"use client";

import useAxios from "../useAxios";
import { useCallback } from "react";

/**
 * Custom hook to interact with the search API.
 */
export function useSearchAPI() {
  const axios = useAxios();

  /**
   * Fetches paginated search results for posts based on the search query.
   *
   * @param query - The search term.
   * @param page - The page number for pagination.
   * @returns A promise with the paginated search results.
   */
  const fetchSearchResults = useCallback(
    async (query: string, page = 1) => {
      const res = await axios.get(
        `/search/?q=${encodeURIComponent(query)}&page=${page}`
      );
      return res.data;
    },
    [axios]
  );

  return { fetchSearchResults };
}
