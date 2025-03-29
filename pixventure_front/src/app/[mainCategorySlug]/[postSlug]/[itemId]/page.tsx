// src/app/[mainCategorySlug]/[postSlug]/[itemId]/page.tsx

"use client";

/**
 * ItemViewerPage
 * --------------
 * This page displays a single "media item" within a post, providing:
 *  - Fullscreen zoomable image
 *  - Navigation arrows to previous/next item
 *  - "Back to post" link
 *  - Loader overlay while fetching data or loading images
 *  - Like button & item menu button in navigation overlay
 *
 * The page fetches item details via the Posts API based on the current
 * route parameters (mainCategorySlug, postSlug, itemId). Once loaded,
 * it displays a ZoomableImage component and a navigation overlay.
 */

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import ZoomableImage from "@/components/ZoomableImage/ZoomableImage";
import ItemViewerNavigation from "@/components/ItemViewerNavigation/ItemViewerNavigation";
import { usePostsAPI } from "@/utils/api/posts";
import styles from "./ItemViewerPage.module.scss";

// Post interface for storing basic post info
interface Post {
  id: number;
  slug: string;
}

/**
 * ItemDetail
 * ----------
 * Represents metadata for the specific item (media).
 * The API returns previous_item_id, next_item_id, etc.
 * We also have fields for controlling like state and counters.
 */
interface ItemDetail {
  item_id: number;
  likes_counter: number;
  has_liked: boolean;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
  served_width: number;
  served_height: number;
  // ... other fields relevant to item
}

export default function ItemViewerPage() {
  // Extract route parameters
  const { mainCategorySlug, postSlug, itemId } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
    itemId: string;
  };

  // Retrieve any "from" parameter to allow "Back to post" or fallback
  const searchParams = useSearchParams();
  const fromParam = searchParams.get("from") || `/${mainCategorySlug}/${postSlug}`;

  // Local state for storing the post and item detail
  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);

  // Loader states: fetch in progress (data) and image in progress
  const [isFetchingItem, setIsFetchingItem] = useState(false);
  const [isImageLoading, setIsImageLoading] = useState(false);

  // Error state for any fetch or load issues
  const [error, setError] = useState<string | null>(null);

  // API hook for fetching data
  const { fetchPostBySlug, fetchPostItem } = usePostsAPI();

  /**
   * useEffect - on route parameter changes:
   *  1. Start item fetch
   *  2. Clear error
   *  3. Mark that we're fetching, and that an image load is pending
   *  4. Fetch post + item data
   */
  useEffect(() => {
    if (!postSlug || !itemId) return;

    const loadData = async () => {
      try {
        setIsFetchingItem(true);
        setIsImageLoading(true); // we'll unset this when the <img> finishes loading
        setError(null);

        // Fetch the Post object by slug
        const foundPost = await fetchPostBySlug(postSlug);
        if (!foundPost) {
          throw new Error(`No post found for slug: ${postSlug}`);
        }
        setPost(foundPost);

        // Fetch the ItemDetail using the post's ID and numeric itemId
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

  // If there's any error, show it
  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  // If we have no post or item detail yet, show a simple full-screen loader
  if (!post || !itemDetail) {
    return (
      <div className={styles.loaderScreen}>
        <div className={styles.spinner} />
        <p>Loading item...</p>
      </div>
    );
  }

  // Deconstruct needed fields from item detail
  const {
    item_id,
    likes_counter,
    has_liked,
    previous_item_id,
    next_item_id,
    item_url,
    served_width,
    served_height,
  } = itemDetail;

  /**
   * Build next and prev URLs, including "?from" parameter
   * so the user can navigate back to the referring page.
   */
  const prevUrl = previous_item_id
    ? `/${mainCategorySlug}/${postSlug}/${previous_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  const nextUrl = next_item_id
    ? `/${mainCategorySlug}/${postSlug}/${next_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  /**
   * Prepare data for the Item Menu.
   * Example: we assume "media" as the entity_type for an item,
   * but you can adjust it if needed.
   */
  const itemMenuData = {
    id: item_id,
    name: post.slug,        // use post slug or any other title
    entity_type: "media",   // "post" or "album" also possible
    canAddToAlbum: true,    // adjust if needed
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
       *  - Back arrow (top-left) => fromParam
       *  - Prev/Next arrows (left/right center)
       *  - Like button (bottom-left), using likes_counter & has_liked
       *  - Menu button (bottom-right), opening itemMenuData
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
       * ZOOMABLE IMAGE
       * We pass an onLoadComplete prop so we can hide the overlay loader
       * as soon as the image finishes loading in the browser.
       */}
      <ZoomableImage
        src={item_url}
        alt={`Item ${item_id}`}
        imageWidth={served_width}
        imageHeight={served_height}
        onLoadComplete={() => setIsImageLoading(false)}
      />

      {/**
       * LOADING OVERLAY
       * Displayed whenever we're fetching new item data or the image has not yet loaded.
       */}
      {(isFetchingItem || isImageLoading) && (
        <div className={styles.loaderOverlay}>
          <div className={styles.spinner} />
          <p>Loading image...</p>
        </div>
      )}
    </div>
  );
}
