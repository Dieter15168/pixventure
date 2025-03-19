// src/app/page.tsx
"use client";

import React from "react";
import PostTile from "../components/Tile/Tile";
import PaginationComponent from "../components/Pagination/Pagination";

import { usePostsAPI } from "../utils/api/posts";
import { usePaginatedData } from "@/hooks/usePaginatedData";

interface Post {
  id: number;
  name: string;
  likes_counter: number;
  has_liked: boolean;
  slug: string;
}

// Our backend returns { results: Post[], current_page, total_pages, ... }
// We'll pass fetchPosts(page) to our hook.
export default function Home() {
  const { fetchPosts } = usePostsAPI();

  const {
    data: posts,
    page,
    totalPages,
    loading,
    error,
    setPage,
  } = usePaginatedData<Post>(fetchPosts); // <-- pass your fetch function

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <>
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
        {/* Pagination */}
      </div>
      <PaginationComponent
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </>
  );
}
