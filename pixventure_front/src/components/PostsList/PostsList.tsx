// src/components/PostsList/PostsList.tsx
"use client";

import React from "react";
import { usePaginatedData } from "@/hooks/usePaginatedData";
import PaginationComponent from "../Pagination/Pagination";
import PostTile from "../Tile/Tile";

export interface Post {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked: boolean;
  main_category_slug?: string;
}

interface PostsListProps {
  fetchFunction: (page: number) => Promise<any>;
  // Optionally pass a "title" or other props if desired
  title?: string;
}

export default function PostsList({ fetchFunction, title }: PostsListProps) {
  const {
    data: posts,
    page,
    totalPages,
    loading,
    error,
    setPage,
  } = usePaginatedData<Post>(fetchFunction);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <>
      {title && <h2>{title}</h2>}

      <div className="pin_container">
        {posts.map((post) => (
          <PostTile
            key={post.id}
            item={{
              ...post,
              entity_type: "post",
              page_type: "posts_list",
            }}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <PaginationComponent
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </>
  );
}
