// src/utils/hooks/usePaginatedData.ts
"use client";

import { useState, useEffect, useCallback } from "react";

export interface PaginatedResponse<T> {
  results: T[];
  current_page: number;
  total_pages: number;
  // other fields if needed
}

export function usePaginatedData<T>(
  fetchFunction: (page: number) => Promise<PaginatedResponse<T>>,
  initialPage: number = 1
) {
  // Initialize state with the provided initialPage (instead of always 1)
  const [data, setData] = useState<T[]>([]);
  const [page, setPage] = useState<number>(initialPage);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const getData = useCallback(
    async (pageNumber: number) => {
      setLoading(true);
      try {
        const response = await fetchFunction(pageNumber);
        setData(response.results);
        setTotalPages(response.total_pages);
        setError(null);
      } catch (err: any) {
        setError(err.message ?? "Error fetching data");
      } finally {
        setLoading(false);
      }
    },
    [fetchFunction]
  );

  // Fetch data when the page changes
  useEffect(() => {
    getData(page);
  }, [page, getData]);

  const handlePageChange = (newPage: number) => {
    if (newPage < 1) return;
    // We now allow newPage even if our local totalPages is not updated yet.
    setPage(newPage);
  };

  return {
    data,
    page,
    totalPages,
    loading,
    error,
    setPage: handlePageChange,
    refresh: () => getData(page),
  };
}
