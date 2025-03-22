// src/components/Pagination/Pagination.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Pagination } from "react-bootstrap";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange?: (page: number) => void;
  buildPageUrl?: (page: number) => string; // If provided, we create <Link>
}

export default function PaginationComponent({
  currentPage,
  totalPages,
  onPageChange,
  buildPageUrl,
}: PaginationProps) {
  if (totalPages <= 1) return null; // no pagination needed

  // We'll generate a short array of pages to show:
  // [1, ..., current-1, current, current+1, ..., last]
  const generatePages = () => {
    const pages: (number | "...")[] = [];

    pages.push(1);
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
      pages.push(totalPages);
    }
    return pages;
  };

  const pages = generatePages();

  const useLinks = !!buildPageUrl; // if buildPageUrl is set, we do link-based pagination

  const handleClick = (p: number) => {
    if (onPageChange) {
      onPageChange(p);
    }
  };

  // We'll define a helper to safely get a URL or fallback "#"
  // if the page is out-of-range
  const safeBuildUrl = (p: number) => {
    if (!buildPageUrl) return "#";
    if (p < 1) return "#";
    if (p > totalPages) return "#";
    return buildPageUrl(p);
  };

  const canGoPrev = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <Pagination className="justify-content-center mt-4">
      {/* PREV */}
      <Pagination.Item
        as="div" // We'll render a <div> instead of an <a>
        disabled={!canGoPrev}
      >
        {useLinks ? (
          <Link href={safeBuildUrl(currentPage - 1)}>
            <span style={{ cursor: canGoPrev ? "pointer" : "default" }}>
              Previous
            </span>
          </Link>
        ) : (
          <span
            role="button"
            style={{ cursor: canGoPrev ? "pointer" : "default" }}
            onClick={() => canGoPrev && handleClick(currentPage - 1)}
          >
            Previous
          </span>
        )}
      </Pagination.Item>

      {/* PAGE NUMBERS */}
      {pages.map((p, i) => {
        if (p === "...") {
          return (
            <Pagination.Ellipsis key={`ellipsis-${i}`} disabled as="div" />
          );
        }
        const pageNum = p as number;
        const isActive = pageNum === currentPage;

        return (
          <Pagination.Item
            as="div"
            key={pageNum}
            active={isActive}
            disabled={isActive}
          >
            {useLinks ? (
              <Link href={safeBuildUrl(pageNum)}>
                <span style={{ cursor: "pointer" }}>{pageNum}</span>
              </Link>
            ) : (
              <span
                style={{ cursor: "pointer" }}
                onClick={() => handleClick(pageNum)}
              >
                {pageNum}
              </span>
            )}
          </Pagination.Item>
        );
      })}

      {/* NEXT */}
      <Pagination.Item
        as="div"
        disabled={!canGoNext}
      >
        {useLinks ? (
          <Link href={safeBuildUrl(currentPage + 1)}>
            <span style={{ cursor: canGoNext ? "pointer" : "default" }}>
              Next
            </span>
          </Link>
        ) : (
          <span
            role="button"
            style={{ cursor: canGoNext ? "pointer" : "default" }}
            onClick={() => canGoNext && handleClick(currentPage + 1)}
          >
            Next
          </span>
        )}
      </Pagination.Item>
    </Pagination>
  );
}
