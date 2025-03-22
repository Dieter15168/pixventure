// src/app/[mainCategorySlug]/[postSlug]/items/PostItemsPaginated.tsx
"use client";

import React, { useCallback } from "react";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePaginatedData } from "@/hooks/usePaginatedData";
import { usePostsAPI } from "@/utils/api/posts";
import PaginationComponent from "@/components/Pagination/Pagination";
import PostItemsList, {
  PostItem,
  PostDetail,
} from "@/components/PostItemsList/PostItemsList";

interface PostItemsPaginatedProps {
  post: PostDetail;
}

export default function PostItemsPaginated({ post }: PostItemsPaginatedProps) {
  // Our intended URL structure for post items is now:
  // /[mainCategorySlug]/[postSlug]/pages for page 1,
  // /[mainCategorySlug]/[postSlug]/pages/page/2 for page 2, etc.
  // We build the base path using the post meta. (Assume post.main_category_slug is set.)
  const basePath = `/${post.main_category_slug || "posts"}/${post.slug}/items`;

  // Our custom hook synchronously derives the current page from the route's optional catch-all
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  const { fetchPostItemsBySlug } = usePostsAPI();
  // Define the fetch function for post items.
  const fetchFunction = useCallback(
    async (page: number) => {
      return await fetchPostItemsBySlug(post.slug, page);
    },
    [post.slug, fetchPostItemsBySlug]
  );

  // Use the paginated data hook with the derived currentPage as the initial page.
  const {
    data: items,
    totalPages,
    loading,
    error,
  } = usePaginatedData<PostItem>(fetchFunction, currentPage);

  // Render a presentational list component for post items.
  // PostItemsList is responsible for transforming items into TileProps.
  return (
    <div>
      <h2>Items for: {post.name}</h2>
      <PostItemsList
        post={post}
        items={items}
        loading={loading}
        error={error}
      />
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
