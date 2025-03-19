// src/app/[slug]/page.tsx
"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";

import { usePostsAPI } from "../../utils/api/posts";
import { usePaginatedData } from "../../hooks/usePaginatedData";
import Tile, { TileProps } from "../../components/Tile/Tile";
import LikeButton from "../../elements/LikeButton/LikeButton";
import PaginationComponent from "../../components/Pagination/Pagination";

// Type definitions
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
  media_type: number; // 1 = photo, 2 = video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  tile_size: "small" | "medium" | "large";
}

export default function PostPage() {
  const params = useParams();
  const router = useRouter();

  // Slug might be numeric or string
  const rawSlug = Array.isArray(params.slug) ? params.slug[0] : params.slug;

  const { fetchPostById, fetchPostBySlug, fetchPostItems } = usePostsAPI();

  // 1) Manage the "post" state
  const [post, setPost] = useState<PostDetail | null>(null);
  const [postLoading, setPostLoading] = useState(true);
  const [postError, setPostError] = useState<string | null>(null);

  // 2) Load the post by slug or numeric ID
  useEffect(() => {
    if (!rawSlug) return;

    const loadPost = async () => {
      setPostLoading(true);
      try {
        let foundPost: PostDetail | null = null;
        // If numeric, fetch by ID
        if (/^\d+$/.test(rawSlug)) {
          const numericId = parseInt(rawSlug, 10);
          foundPost = await fetchPostById(numericId);
        } else {
          // Otherwise fetch by slug
          foundPost = await fetchPostBySlug(rawSlug);
        }

        if (!foundPost) {
          setPostError("Post not found");
        } else {
          setPost(foundPost);
        }
      } catch (err: any) {
        setPostError(err.message ?? "Error fetching post");
      } finally {
        setPostLoading(false);
      }
    };

    loadPost();
  }, [rawSlug, fetchPostById, fetchPostBySlug]);

  // 3) Define the fetch function for post items
  // If post is null, we return a default shape to prevent errors
  const fetchItemsForPost = useCallback(
    async (page: number) => {
      if (!post) {
        // Return a default empty shape if post isn't loaded yet
        return { results: [], current_page: 1, total_pages: 1 };
      }
      return await fetchPostItems(post.id, page);
    },
    [post, fetchPostItems]
  );

  // 4) Use our pagination hook with the items fetch function
  const {
    data: items,
    page,
    totalPages,
    loading: itemsLoading,
    error: itemsError,
    setPage,
  } = usePaginatedData<PostItem>(fetchItemsForPost);

  // 5) Render logic
  if (postLoading) {
    return <div>Loading post...</div>;
  }
  if (postError) {
    return <div>Error: {postError}</div>;
  }
  if (!post) {
    return <div>No post found</div>;
  }

  // If the post is loaded but items are in the process of loading
  // you can show a partial spinner, or show them as they come in:
  if (itemsLoading && items.length === 0) {
    return <div>Loading post items...</div>;
  }
  if (itemsError) {
    return <div>Error while loading items: {itemsError}</div>;
  }

  // Convert "items" to your TileProps
  const tileItems: TileProps[] = items.map((item) => ({
    id: item.id,
    name: post.name,
    slug: `${post.slug}/${item.id}`,
    thumbnail_url: item.thumbnail_url,
    media_type: item.media_type as 1 | 2,
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
        entity_type="post"
        targetId={post.id}
        initialLikesCounter={post.likes_counter}
        initialHasLiked={post.has_liked}
      />

      <div className="pin_container">
        {tileItems.map((tile) => (
          <Tile
            key={tile.id}
            item={tile}
          />
        ))}
      </div>

      {/* Pagination UI */}
      <PaginationComponent
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
}
