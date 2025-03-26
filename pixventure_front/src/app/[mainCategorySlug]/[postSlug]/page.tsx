// src/app/[mainCategorySlug]/[postSlug]/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";
import Tile, { TileProps } from "@/components/Tile/Tile";
import LikeButton from "@/elements/LikeButton/LikeButton";
import PaginationComponent from "@/components/Pagination/Pagination";
import SharedMasonry from "@/components/common/SharedMasonry";

interface PostDetail {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  images_count: number;
  videos_count: number;
  has_liked: boolean;
  main_category_slug?: string;
  thumbnail_url: string;
  locked: boolean;
  owner_username: string;
}

interface PostItem {
  id: number;
  media_type: number; // 1 = photo, 2 = video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  locked: boolean;
  tile_size: "small" | "medium" | "large";
}

export default function PostPage() {
  const { mainCategorySlug, postSlug } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
  };
  const router = useRouter();
  const { fetchPostBySlug, fetchPostItemsBySlug } = usePostsAPI();

  // --- Load post meta ---
  const [post, setPost] = useState<PostDetail | null>(null);
  const [postLoading, setPostLoading] = useState<boolean>(true);
  const [postError, setPostError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setPostLoading(true);
      try {
        const data = await fetchPostBySlug(postSlug);
        setPost(data);
      } catch (err: any) {
        setPostError(err.message || "Failed to load post");
      } finally {
        setPostLoading(false);
      }
    })();
  }, [postSlug, fetchPostBySlug]);

  // --- Load first page of post items as preview ---
  const [previewItems, setPreviewItems] = useState<PostItem[]>([]);
  const [previewLoading, setPreviewLoading] = useState<boolean>(true);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setPreviewLoading(true);
      try {
        // Always load page 1 for the preview.
        const res = await fetchPostItemsBySlug(postSlug, 1);
        setPreviewItems(res.results);
      } catch (err: any) {
        setPreviewError(err.message || "Failed to load post items");
      } finally {
        setPreviewLoading(false);
      }
    })();
  }, [postSlug, fetchPostItemsBySlug]);

  // --- Build the paginator link for navigating to the dedicated items route ---
  // When the user clicks a page link, they will be taken to:
  // /[mainCategorySlug]/[postSlug]/items for page 1
  // /[mainCategorySlug]/[postSlug]/items/page/2 for page 2, etc.
  const buildPageUrl = (page: number) => {
    return page === 1
      ? `/${mainCategorySlug}/${postSlug}/items`
      : `/${mainCategorySlug}/${postSlug}/items/page/${page}`;
  };

  // For the paginator on the preview, we'll assume the preview only shows page 1.
  // But if there are more pages, the API should tell us total_pages.
  // Here, we load totalPages from the first-page preview response.
  const [totalPages, setTotalPages] = useState<number>(1);
  useEffect(() => {
    (async () => {
      try {
        const res = await fetchPostItemsBySlug(postSlug, 1);
        setTotalPages(res.total_pages);
      } catch (err) {
        console.error("Error fetching total pages:", err);
      }
    })();
  }, [postSlug, fetchPostItemsBySlug]);

  if (postLoading) return <div>Loading post...</div>;
  if (postError) return <div>Error: {postError}</div>;
  if (!post) return <div>No post found for slug {postSlug}</div>;

  return (
    <div>
      <h1>{post.name}</h1>
      <p>By {post.owner_username}</p>
      <LikeButton
        entity_type="post"
        targetId={post.id}
        initialLikesCounter={post.likes_counter}
        initialHasLiked={post.has_liked}
      />
      {previewLoading ? (
        <p>Loading post items...</p>
      ) : previewError ? (
        <p>Error loading post items: {previewError}</p>
      ) : (
        <SharedMasonry>
          {previewItems.map((item) => {
            const tile: TileProps = {
              id: item.id,
              name: post.name,
              slug: `${post.slug}/${item.id}`,
              main_category_slug: post.main_category_slug,
              thumbnail_url: item.thumbnail_url,
              locked: item.locked,
              media_type: item.media_type,
              likes_counter: item.likes_counter,
              has_liked: item.has_liked,
              owner_username: post.owner_username,
              tile_size: item.tile_size,
              entity_type: "media",
              page_type: "post",
            };
            return (
              <Tile
                key={tile.id}
                item={tile}
              />
            );
          })}
        </SharedMasonry>
      )}

      {/* Render paginator that links to the dedicated paginated items route */}
      {totalPages > 1 && (
        <PaginationComponent
          currentPage={1} // preview always shows page 1
          totalPages={totalPages}
          buildPageUrl={buildPageUrl}
        />
      )}

      {/* Optionally, provide a link/button to "View All Items" */}
      {totalPages > 1 && (
        <div style={{ marginTop: "1rem" }}>
          <a href={`/${mainCategorySlug}/${postSlug}/items`}>
            View All Post Items
          </a>
        </div>
      )}
    </div>
  );
}
