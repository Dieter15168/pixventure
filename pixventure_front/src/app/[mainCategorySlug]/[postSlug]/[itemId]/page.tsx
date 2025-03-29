"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import ZoomableImage from "@/components/ZoomableImage/ZoomableImage";
import ItemViewerNavigation from "@/components/ItemViewerNavigation/ItemViewerNavigation";
import { usePostsAPI } from "@/utils/api/posts";
import styles from "./ItemViewerPage.module.scss";

interface Post {
  id: number;
  slug: string;
}

interface ItemDetail {
  item_id: number;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
  served_width: number;
  served_height: number;
  // ... other fields
}

export default function ItemViewerPage() {
  const { mainCategorySlug, postSlug, itemId } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
    itemId: string;
  };

  const searchParams = useSearchParams();
  // If your links supply a "?from" param, or default to post's URL
  const fromParam = searchParams.get("from") || `/${mainCategorySlug}/${postSlug}`;

  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);

  // These control the loader
  const [isFetchingItem, setIsFetchingItem] = useState(false);
  const [isImageLoading, setIsImageLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { fetchPostBySlug, fetchPostItem } = usePostsAPI();

  // Whenever slug or itemId changes, load the data
  useEffect(() => {
    if (!postSlug || !itemId) return;

    const loadData = async () => {
      try {
        setIsFetchingItem(true);  // Start loading
        setIsImageLoading(true);  // Will remain true until the <img> triggers onLoad
        setError(null);

        const foundPost = await fetchPostBySlug(postSlug);
        if (!foundPost) {
          throw new Error(`No post found for slug: ${postSlug}`);
        }
        setPost(foundPost);

        const detailData = await fetchPostItem(foundPost.id, parseInt(itemId, 10));
        setItemDetail(detailData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsFetchingItem(false);
      }
    };

    loadData();
  }, [postSlug, itemId, fetchPostBySlug, fetchPostItem]);

  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;

  // If we haven't finished fetching or we have no data yet
  if (!post || !itemDetail) {
    return (
      <div className={styles.loaderScreen}>
        {/* You could show a spinner or text here */}
        <div className={styles.spinner} />
        <p>Loading item...</p>
      </div>
    );
  }

  const {
    item_id,
    previous_item_id,
    next_item_id,
    item_url,
    served_width,
    served_height,
  } = itemDetail;

  // Build the next/prev/back URLs
  const prevUrl = previous_item_id
    ? `/${mainCategorySlug}/${postSlug}/${previous_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  const nextUrl = next_item_id
    ? `/${mainCategorySlug}/${postSlug}/${next_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  return (
    <div className={styles.fullscreen}>
      {/* NAVIGATION ARROWS & "BACK TO POST" */}
      <ItemViewerNavigation
        previousItemUrl={prevUrl}
        nextItemUrl={nextUrl}
        backUrl={fromParam}
      />

      {/* The actual image with zoom. We pass an onLoad callback. */}
      <ZoomableImage
        src={item_url}
        alt={`Item ${item_id}`}
        imageWidth={served_width}
        imageHeight={served_height}
        onLoadComplete={() => setIsImageLoading(false)}
      />

      {/* LOADING OVERLAY (while new item data or image is still loading) */}
      {(isFetchingItem || isImageLoading) && (
        <div className={styles.loaderOverlay}>
          <div className={styles.spinner} />
          <p>Loading image...</p>
        </div>
      )}
    </div>
  );
}
