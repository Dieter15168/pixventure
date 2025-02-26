// src/app/[slug]/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { usePostsAPI } from '../../utils/api/posts';

interface PostDetail {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  images_count: number;
  videos_count: number;
  has_liked: boolean;
  thumbnail_url: string;
  owner_username: string;
}

interface PostItem {
  id: number;
  item_type: number; // 1=photo, 2=video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
}

export default function PostPage() {
  const params = useParams();
  const slug = params.slug; // This corresponds to the [slug] in the route /[slug]
  const { fetchPostBySlug, fetchPostItems } = usePostsAPI();

  const [post, setPost] = useState<PostDetail | null>(null);
  const [items, setItems] = useState<PostItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const loadPostData = async () => {
      try {
        // Fetch post details using the new API utility
        const foundPost = await fetchPostBySlug(slug);
        setPost(foundPost);

        // Once we have the post's ID, fetch the post items
        const postId = foundPost.id;
        const postItems = await fetchPostItems(postId);
        setItems(postItems);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPostData();
  }, [slug]);

  if (loading) return <div>Loading post...</div>;
  if (error) return <div>Error: {error}</div>;

  // If we got here, we should have the post and items
  if (!post) return <div>No post found</div>;

  return (
    <div>
      <h1>{post.name}</h1>
      <p>By {post.owner_username}</p>
      <p>Likes: {post.likes_counter}</p>
      <p>
        Images: {post.images_count}, Videos: {post.videos_count}
      </p>
      <p>Has Liked: {post.has_liked ? "Yes" : "No"}</p>

      <hr />

      <h2>Post Items:</h2>
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/${slug}/${item.id}`}
          >
            <div
              style={{
                border: "1px solid #ddd",
                padding: "10px",
                width: "120px",
              }}
            >
              <img
                src={item.thumbnail_url}
                alt={`Item ${item.id}`}
                width={100}
              />
              <p>Type: {item.item_type === 1 ? "Photo" : "Video"}</p>
              <p>Likes: {item.likes_counter}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
