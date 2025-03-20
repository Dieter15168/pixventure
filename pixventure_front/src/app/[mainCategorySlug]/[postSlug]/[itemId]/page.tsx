// src/app/[mainCategorySlug]/[postSlug]/[itemId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { usePostsAPI } from "@/utils/api/posts";

interface Post {
  id: number;
  slug: string;
  // ...
}

interface ItemDetail {
  item_id: number;
  likes_counter: number;
  has_liked: boolean;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
}

export default function ItemViewerPage() {
  const { mainCategorySlug, postSlug, itemId } = useParams() as {
    mainCategorySlug: string;
    postSlug: string;
    itemId: string;
  };

  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { fetchPostBySlug, fetchPostItem } = usePostsAPI();

  useEffect(() => {
    if (!postSlug || !itemId) return;

    const loadData = async () => {
      try {
        // Step A: fetch the post (by postSlug)
        const foundPost = await fetchPostBySlug(postSlug);
        if (!foundPost) {
          throw new Error(`No post found for slug: ${postSlug}`);
        }
        setPost(foundPost);

        // Step B: fetch the item from that post
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

  const { item_id, previous_item_id, next_item_id, item_url } = itemDetail;

  return (
    <div>
      <h2>
        Viewing Item #{item_id} of Post "{post.slug}"
      </h2>
      <div style={{ margin: "10px 0" }}>
        <img
          src={item_url}
          alt={`Item ${item_id}`}
          style={{ maxWidth: "400px" }}
        />
      </div>

      <div style={{ marginTop: "20px" }}>
        {previous_item_id && (
          <Link href={`/${mainCategorySlug}/${postSlug}/${previous_item_id}`}>
            <button>Previous</button>
          </Link>
        )}
        {next_item_id && (
          <Link href={`/${mainCategorySlug}/${postSlug}/${next_item_id}`}>
            <button style={{ marginLeft: "10px" }}>Next</button>
          </Link>
        )}
      </div>
    </div>
  );
}
