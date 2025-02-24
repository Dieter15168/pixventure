"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

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
  // additional fields if needed
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

  const [post, setPost] = useState<PostDetail | null>(null);
  const [items, setItems] = useState<PostItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    // 1) Fetch the post detail by slug
    //    For example, you might have an API that allows queries like /api/posts/?slug=test-post
    //    Or you might do a special route like /api/posts/slug/test-post
    //    For demonstration, we'll assume /api/posts/?slug=<slug>
    const fetchPostBySlug = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. http://127.0.0.1:8000/api
        // Step A: Get the post detail
        const resPost = await fetch(`${baseUrl}/posts/?slug=${slug}`);
        if (!resPost.ok) {
          throw new Error(`Failed to fetch post: ${resPost.statusText}`);
        }
        const postData = await resPost.json();
        // We assume postData.results[0] is the matching post
        const foundPost = postData.results[0];
        if (!foundPost) {
          throw new Error(`No post found for slug: ${slug}`);
        }
        setPost(foundPost);

        // Step B: Once we have the post's ID, fetch the items
        const postId = foundPost.id;
        const resItems = await fetch(`${baseUrl}/posts/${postId}/items/`);
        if (!resItems.ok) {
          throw new Error(`Failed to fetch post items: ${resItems.statusText}`);
        }
        const itemsData = await resItems.json();
        setItems(itemsData.results);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPostBySlug();
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
              key={item.id}
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
