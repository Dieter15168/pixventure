// src/app/tag/[tagSlug]/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import PostsList from "@/components/PostsList/PostsList";

export default function TagListingPage() {
  const router = useRouter();
  const { tagSlug, pageParams } = useParams() as {
    tagSlug: string;
    pageParams?: string[];
  };

  // If user just typed `/tag/test-tag`, then `pageParams` is undefined -> page=1
  // If user typed `/tag/test-tag/page/2`, then pageParams = ["page", "2"]
  // We'll parse the second segment as the page number if it exists.
  let currentPage = 1;
  if (pageParams && pageParams[0] === "page") {
    // If there's a page number provided
    const possiblePageNumber = pageParams[1];
    if (possiblePageNumber) {
      currentPage = parseInt(possiblePageNumber, 10) || 1;
    }
  }

  const { fetchPostsByTag } = usePostsAPI();

  // We'll pass a function that calls the correct backend route
  const fetchFunction = async (page: number) => {
    return fetchPostsByTag(tagSlug, page);
  };

  // If you want to handle `/tag/test-tag/page` with no number -> redirect to page=1
  // e.g. if pageParams = ["page"] with no second element
  if (pageParams && pageParams[0] === "page" && pageParams.length === 1) {
    router.replace(`/tag/${tagSlug}/page/1`);
    return null;
  }

  return (
    <div>
      <h1>Tag: {tagSlug}</h1>
      <PostsList fetchFunction={fetchFunction} initialPage={currentPage} />
    </div>
  );
}
