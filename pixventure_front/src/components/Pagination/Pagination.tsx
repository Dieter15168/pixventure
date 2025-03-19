// src/components/Pagination/Pagination.tsx
"use client";

import React from "react";
import { Pagination } from "react-bootstrap";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function PaginationComponent({
  currentPage,
  totalPages,
  onPageChange,
}: PaginationProps) {
  // Generate the list of pages
  const generatePages = () => {
    const pages: (number | "...")[] = [];

    pages.push(1); // First page

    if (currentPage > 3) {
      pages.push("...");
    }

    for (let i = currentPage - 1; i <= currentPage + 1; i++) {
      if (i > 1 && i < totalPages) {
        pages.push(i);
      }
    }

    if (currentPage < totalPages - 2) {
      pages.push("...");
    }

    if (totalPages > 1) {
      pages.push(totalPages); // Last page
    }

    return pages;
  };

  const pages = generatePages();

  return (
    <Pagination className="justify-content-center mt-4">
      {/* Previous Button */}
      <Pagination.Prev
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
      />

      {/* Page Numbers */}
      {pages.map((page, index) => {
        if (page === "...") {
          return <Pagination.Ellipsis key={index} disabled />;
        }
        return (
          <Pagination.Item
            key={page}
            active={page === currentPage}
            onClick={() => onPageChange(page as number)}
          >
            {page}
          </Pagination.Item>
        );
      })}

      {/* Next Button */}
      <Pagination.Next
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      />
    </Pagination>
  );
}
