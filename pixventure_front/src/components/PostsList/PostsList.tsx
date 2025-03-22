// src/components/PostsList/PostsList.tsx
"use client";

import React from "react";
import { usePaginatedData } from "@/hooks/usePaginatedData";
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
  title?: string;
  initialPage?: number; // default 1
}

/**
 * PostsList now directly passes initialPage to usePaginatedData.
 * We also set a key based on initialPage so that when it changes the component re-mounts.
 */
export default function PostsList({
  fetchFunction,
  title,
  initialPage = 1,
}: PostsListProps) {
  const { data: posts, page, totalPages, loading, error, setPage } =
    usePaginatedData<Post>(fetchFunction, initialPage);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div key={initialPage}>
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
    </div>
  );
}
