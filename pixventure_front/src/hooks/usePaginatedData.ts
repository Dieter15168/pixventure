// src/utils/hooks/usePaginatedData.ts
"use client";

import { useState, useEffect, useCallback } from "react";

export interface PaginatedResponse<T> {
  results: T[];
  current_page: number;
  total_pages: number;
  // you can include other fields if your backend returns them
}

export function usePaginatedData<T>(
  fetchFunction: (page: number) => Promise<PaginatedResponse<T>>
) {
  const [data, setData] = useState<T[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
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

  // Fetch data whenever "page" changes
  useEffect(() => {
    getData(page);
  }, [page, getData]);

  // Expose a page-changer that ensures we stay in range
  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
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
