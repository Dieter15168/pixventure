"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
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
  likes_counter: number;
  has_liked: boolean;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
  served_width: number;
  served_height: number;
  original_width: number;
  original_height: number;
  show_membership_prompt: boolean;
  locked: boolean;
}

export default function ItemViewerPage() {
  const { mainCategorySlug, postSlug, itemId } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
    itemId: string;
  };

  // If you are using searchParams to pass ?from=someUrl
  const searchParams = useSearchParams();
  const fromParam = searchParams.get("from") || `/${mainCategorySlug}/${postSlug}`;
  // Or you can define any fallback if 'from' doesn't exist

  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { fetchPostBySlug, fetchPostItem } = usePostsAPI();

  useEffect(() => {
    if (!postSlug || !itemId) return;

    const loadData = async () => {
      try {
        const foundPost = await fetchPostBySlug(postSlug);
        if (!foundPost) {
          throw new Error(`No post found for slug: ${postSlug}`);
        }
        setPost(foundPost);

        const postId = foundPost.id;
        const numericItemId = parseInt(itemId, 10);
        const detailData = await fetchPostItem(postId, numericItemId);
        setItemDetail(detailData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [postSlug, itemId, fetchPostBySlug, fetchPostItem]);

  if (loading) return <p>Loading item...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!post || !itemDetail) return <p>No data found</p>;

  const {
    item_id,
    previous_item_id,
    next_item_id,
    item_url,
    served_width,
    served_height,
  } = itemDetail;

  // Construct your navigation URLs:
  const prevUrl = previous_item_id
    ? `/${mainCategorySlug}/${postSlug}/${previous_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  const nextUrl = next_item_id
    ? `/${mainCategorySlug}/${postSlug}/${next_item_id}?from=${encodeURIComponent(fromParam)}`
    : undefined;

  // For "Back to Post" or "Back to Category" logic, you can pass fromParam or fallback:
  const backUrl = fromParam;

  return (
    <div className={styles.fullscreen}>
      {/* The zoomed image (z-index: 10 in .outerContainer from ZoomableImage) */}
      <ZoomableImage
        src={item_url}
        alt={`Item ${item_id}`}
        imageWidth={served_width}
        imageHeight={served_height}
      />

      {/* The high-level navigation overlay above the zoomed image */}
      <ItemViewerNavigation
        previousItemUrl={prevUrl}
        nextItemUrl={nextUrl}
        backUrl={backUrl}
      />

      {/* 
        Optionally, if you still want to show some textual info, 
        you could place it somewhere else in the DOM or style it 
        with appropriate z-index 
      */}
      <div className={styles.infoBox}>
        <p>Item #{item_id} of Post "{post.slug}"</p>
      </div>
    </div>
  );
}
