// src/components/routes/PaginatedRoute.tsx
"use client";

import React from "react";
import PaginationComponent from "../Pagination/Pagination";

// Define props with a generic type T for the entity.
interface PaginatedRouteProps<T> {
  currentPage: number;
  buildPageUrl: (page: number) => string;
  fetchFunction: (page: number) => Promise<{ results: T[]; total_pages: number }>;
  title?: string;
  // ListComponent is a React component that takes fetchFunction and initialPage as props.
  ListComponent: React.ComponentType<{
    fetchFunction: (page: number) => Promise<{ results: T[]; total_pages: number }>;
    initialPage: number;
  }>;
}

export default function PaginatedRoute<T>({
  currentPage,
  buildPageUrl,
  fetchFunction,
  title,
  ListComponent,
}: PaginatedRouteProps<T>) {
  // Local state for total pages
  const [totalPages, setTotalPages] = React.useState<number>(1);

  // Wrap the provided fetchFunction so that it also updates totalPages.
  const fetchWrapper = async (page: number) => {
    const data = await fetchFunction(page);
    setTotalPages(data.total_pages);
    return data;
  };

  return (
    <div>
      {title && <h2>{title}</h2>}
      <ListComponent fetchFunction={fetchWrapper} initialPage={currentPage} />
      {totalPages > 1 && (
        <PaginationComponent
          currentPage={currentPage}
          totalPages={totalPages}
          buildPageUrl={buildPageUrl}
        />
      )}
    </div>
  );
}
