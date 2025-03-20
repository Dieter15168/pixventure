// src/app/[slug]/page.tsx
"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";

import { usePostsAPI } from "../../utils/api/posts";
import { usePaginatedData } from "../../hooks/usePaginatedData";
import Tile, { TileProps } from "../../components/Tile/Tile";
import LikeButton from "../../elements/LikeButton/LikeButton";
import PaginationComponent from "../../components/Pagination/Pagination";

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
  media_type: number; // 1=photo, 2=video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  tile_size: "small" | "medium" | "large";
}

export default function PostPage() {
  const params = useParams() as { slug: string };
  const { fetchPostBySlug, fetchPostItemsBySlug } = usePostsAPI();
  const [post, setPost] = useState<PostDetail | null>(null);
  const [postLoading, setPostLoading] = useState(true);
  const [postError, setPostError] = useState<string | null>(null);

  // 1) Load the post metadata (by slug)
  useEffect(() => {
    const loadPost = async () => {
      setPostLoading(true);
      try {
        const data = await fetchPostBySlug(params.slug);
        setPost(data);
      } catch (err: any) {
        setPostError(err.message ?? "Failed to load post");
      } finally {
        setPostLoading(false);
      }
    };

    loadPost();
  }, [params.slug, fetchPostBySlug]);

  // 2) Define a fetch function for the post items
  // If the post is not yet available, return empty results
  const fetchItems = useCallback(
    async (page: number) => {
      if (!params.slug) {
        return { results: [], current_page: 1, total_pages: 1 };
      }
      const res = await fetchPostItemsBySlug(params.slug, page);
      return res;
    },
    [params.slug, fetchPostItemsBySlug]
  );

  // 3) Paginated data for the post items
  const {
    data: items,
    page,
    totalPages,
    loading: itemsLoading,
    error: itemsError,
    setPage,
  } = usePaginatedData<PostItem>(fetchItems);

  // 4) Basic checks
  if (postLoading) return <div>Loading post...</div>;
  if (postError) return <div>Error: {postError}</div>;
  if (!post) return <div>No post found for slug {params.slug}</div>;

  // If items are still loading
  if (itemsLoading && items.length === 0) {
    return <div>Loading post items...</div>;
  }
  if (itemsError) {
    return <div>Error loading post items: {itemsError}</div>;
  }

  // 5) Transform items -> TileProps
  const tileItems: TileProps[] = items.map((item) => ({
    id: item.id,
    name: post.name,
    slug: `${post.slug}/${item.id}`,
    thumbnail_url: item.thumbnail_url,
    media_type: item.media_type,
    likes_counter: item.likes_counter,
    has_liked: item.has_liked,
    owner_username: post.owner_username,
    tile_size: item.tile_size,
    entity_type: "media",
    page_type: "post",
  }));

  // 6) Render
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
          <Tile key={tile.id} item={tile} />
        ))}
      </div>

      {/* Paginate if more than one page */}
      {totalPages > 1 && (
        <PaginationComponent
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
