// src/app/[slug]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { usePostsAPI } from "../../utils/api/posts";
import Tile, { TileProps } from "../../components/Tile/Tile";
import LikeButton from "../../elements/LikeButton/LikeButton";

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
  item_type: number; // 1 = photo, 2 = video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  tile_size: "small" | "medium" | "large";
}

export default function PostPage() {
  const params = useParams();
  const slug = Array.isArray(params.slug) ? params.slug[0] : params.slug;

  const { fetchPostBySlug, fetchPostItems } = usePostsAPI();

  const [post, setPost] = useState<PostDetail | null>(null);
  const [items, setItems] = useState<PostItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const loadPostData = async () => {
      try {
        // Fetch post details by slug
        const foundPost = await fetchPostBySlug(slug);
        setPost(foundPost);

        // Fetch post items by post ID
        const postItems = await fetchPostItems(foundPost.id);
        setItems(postItems);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPostData();
  }, [slug, fetchPostBySlug, fetchPostItems]);

  if (loading) return <div>Loading post...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!post) return <div>No post found</div>;

  // Transform each post item into a TileProps object
  // For a post item, we use the post's slug and owner data.
  const tileItems: TileProps[] = items.map((item) => ({
    id: item.id,
    name: post.name,
    slug: `${post.slug}/${item.id}`,
    thumbnail_url: item.thumbnail_url,
    item_type: item.item_type as 1 | 2, // assuming only photo (1) or video (2)
    likes_counter: item.likes_counter,
    has_liked: item.has_liked,
    owner_username: post.owner_username,
    tile_size: item.tile_size,
    page_type: "post",
    entity_type: "media",
  }));

  return (
    <div>
      <h1>{post.name}</h1>
      <p>By {post.owner_username}</p>
      <LikeButton
        entity_type={"post"}
        targetId={post.id}
        initialLikesCounter={post.likes_counter}
        initialHasLiked={post.has_liked}
      />
      <div style={{ display: "grid", gap: "10px" }}>
        {tileItems.map((tile) => (
          <Tile
            key={tile.id}
            item={{ ...tile, entity_type: "media" }}
          />
        ))}
      </div>
    </div>
  );
}
