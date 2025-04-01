// src/app/[mainCategorySlug]/[postSlug]/[itemId]/page.tsx

"use client";

/**
 * ItemViewerPage
 * --------------
 * This page displays a single "media item" within a post, providing:
 *  - Fullscreen media viewer (image or video) via MediaViewer
 *  - Navigation arrows to previous/next item
 *  - "Back to post" link
 *  - Loader overlay while fetching data or loading media
 *  - Like button & item menu button in navigation overlay
 */

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import ItemViewerNavigation from "@/components/ItemViewerNavigation/ItemViewerNavigation";
import MediaViewer from "@/components/MediaViewer/MediaViewer";
import { usePostsAPI } from "@/utils/api/posts";
import styles from "./ItemViewerPage.module.scss";
import GlowingResolutionPrompt from "@/components/GlowingResolutionPrompt/GlowingResolutionPrompt";
import LockLogo from "@/elements/LockLogo/LockLogo";

// Basic interface for storing info about the post
interface Post {
  id: number;
  slug: string;
}

/**
 * ItemDetail
 * ----------
 * The API now provides media_type to indicate "image" or "video".
 */
interface ItemDetail {
  item_id: number;
  media_type: "image" | "video";
  likes_counter: number;
  has_liked: boolean;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
  served_width: number;
  served_height: number;
  original_width: number;
  original_height: number;
  video_poster_url: string;
  higher_resolution_available: boolean;
  locked: boolean; // Indicates if the item is locked.
}

export default function ItemViewerPage() {
  // Route parameters
  const { mainCategorySlug, postSlug, itemId } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
    itemId: string;
  };

  // "from" param for back navigation
  const searchParams = useSearchParams();
  const fromParam =
    searchParams.get("from") || `/${mainCategorySlug}/${postSlug}`;

  // Local state for post and item detail
  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);

  // Loader states: data fetch + media load
  const [isFetchingItem, setIsFetchingItem] = useState(false);
  const [isMediaLoading, setIsMediaLoading] = useState(false);

  // Error state
  const [error, setError] = useState<string | null>(null);

  // API hooks
  const { fetchPostBySlug, fetchPostItem } = usePostsAPI();

  /**
   * Fetch post + item detail whenever slug/itemId changes
   */
  useEffect(() => {
    if (!postSlug || !itemId) return;

    const loadData = async () => {
      try {
        setIsFetchingItem(true);
        setIsMediaLoading(true);
        setError(null);

        const foundPost = await fetchPostBySlug(postSlug);
        if (!foundPost) {
          throw new Error(`No post found for slug: ${postSlug}`);
        }
        setPost(foundPost);

        const numericItemId = parseInt(itemId, 10);
        const detailData = await fetchPostItem(foundPost.id, numericItemId);
        setItemDetail(detailData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsFetchingItem(false);
      }
    };

    loadData();
  }, [postSlug, itemId, fetchPostBySlug, fetchPostItem]);

  // If there's an error, show it
  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  // If not yet loaded, show a basic loader
  if (!post || !itemDetail) {
    return (
      <div className={styles.loaderScreen}>
        <div className={styles.spinner} />
        <p>Loading item...</p>
      </div>
    );
  }

  // Deconstruct item detail
  const {
    item_id,
    media_type,
    likes_counter,
    has_liked,
    previous_item_id,
    next_item_id,
    item_url,
    served_width,
    served_height,
    original_width,
    original_height,
    video_poster_url,
    higher_resolution_available,
    locked,
  } = itemDetail;

  // Construct prev/next URLs for navigation
  const prevUrl = previous_item_id
    ? `/${mainCategorySlug}/${postSlug}/${previous_item_id}?from=${encodeURIComponent(
        fromParam
      )}`
    : undefined;

  const nextUrl = next_item_id
    ? `/${mainCategorySlug}/${postSlug}/${next_item_id}?from=${encodeURIComponent(
        fromParam
      )}`
    : undefined;

  // Data for the item menu
  const itemMenuData = {
    id: item_id,
    name: post.slug,
    entity_type: "media",
    canAddToAlbum: true,
    categories: [],
    tags: [],
    pageContext: {
      page_type: "post",
      entityId: item_id,
    },
  };

  return (
    <div className={styles.fullscreen}>
      {/**
       * NAVIGATION OVERLAY
       * Includes:
       *  - Back arrow => fromParam
       *  - Prev/Next arrows => prevUrl, nextUrl
       *  - Like button => likes_counter, has_liked
       *  - Menu button => itemMenuData
       */}
      <ItemViewerNavigation
        previousItemUrl={prevUrl}
        nextItemUrl={nextUrl}
        backUrl={fromParam}
        entityType="media"
        targetId={item_id}
        initialLikes={likes_counter}
        initialHasLiked={has_liked}
        itemMenuData={itemMenuData}
      />

      {/**
       * MEDIA VIEWER (image or video)
       * We'll rely on MediaViewer to handle correct rendering &
       * center the content on-screen. We pass onLoadComplete to
       * turn off the loader overlay once ready.
       */}
      <MediaViewer
        src={item_url}
        alt={`Item ${item_id}`}
        imageWidth={served_width}
        imageHeight={served_height}
        onLoadComplete={() => setIsMediaLoading(false)}
        fallbackMediaType={media_type}
        posterUrl={video_poster_url}
      />

      {/**
       * LOCKED OVERLAY
       * --------------
       * Renders a large glowing crown icon in the center of the screen when the item is locked.
       */}
      {locked && <LockLogo />}

      {/* Membership Prompt for Higher Resolution */}
      {higher_resolution_available && (
        <div className={styles.membershipPrompt}>
          <GlowingResolutionPrompt
            servedWidth={served_width}
            servedHeight={served_height}
            fullWidth={original_width}
            fullHeight={original_height}
            modalText="Please sign up for membership to access premium features."
          >
            <span>HD</span>
          </GlowingResolutionPrompt>
        </div>
      )}

      {/**
       * LOADING OVERLAY
       * Active while we're fetching item data or if the media isn't loaded yet.
       */}
      {(isFetchingItem || isMediaLoading) && (
        <div className={styles.loaderOverlay}>
          <div className={styles.spinner} />
          <p>Loading media...</p>
        </div>
      )}
    </div>
  );
}
