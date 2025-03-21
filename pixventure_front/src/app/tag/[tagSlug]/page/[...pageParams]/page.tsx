// src/app/tag/[tagSlug]/page/[...pageParams]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PostsList from "@/components/PostsList/PostsList";

export default function TagPostsPage() {
  const { tagSlug, pageParams } = useParams() as {
    tagSlug: string;
    pageParams?: string[];
  };

  const pageNum = pageParams && pageParams[0] ? parseInt(pageParams[0], 10) : 1;

  const { fetchPostsByTag } = usePostsAPI();

  const fetchFunction = async (page: number) => {
    return await fetchPostsByTag(tagSlug, page);
  };

  return (
    <div>
      <h1>Tag: {tagSlug}</h1>
      <PostsList
        fetchFunction={fetchFunction}
        initialPage={pageNum}
      />
    </div>
  );
}
