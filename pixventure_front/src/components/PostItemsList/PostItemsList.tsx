// src/components/PostItemsList/PostItemsList.tsx
"use client";

import React from "react";
import Tile, { TileProps } from "../Tile/Tile";
import SharedMasonry from "../common/SharedMasonry";

export interface PostItem {
  id: number;
  media_type: number; // 1 = photo, 2 = video
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  tile_size: "small" | "medium" | "large";
}

export interface PostDetail {
  id: number;
  name: string;
  slug: string;
  main_category_slug?: string;
  owner_username: string;
}

interface PostItemsListProps {
  post: PostDetail;
  items: PostItem[];
  loading: boolean;
  locked: boolean;
  error: string | null;
  title?: string;
}

export default function PostItemsList({
  post,
  items,
  loading,
  error,
  title,
}: PostItemsListProps) {
  if (loading) return <p>Loading post items...</p>;
  if (error) return <p>Error: {error}</p>;

  // Transform each post item into a TileProps object.
  const tileItems: TileProps[] = items.map((item) => ({
    id: item.id,
    name: post.name,
    slug: `${post.slug}/${item.id}`, // URL for the individual item view
    main_category_slug: post.main_category_slug,
    thumbnail_url: item.thumbnail_url,
    media_type: item.media_type,
    likes_counter: item.likes_counter,
    locked: item.locked,
    has_liked: item.has_liked,
    owner_username: post.owner_username,
    tile_size: item.tile_size,
    entity_type: "media",
    page_type: "post",
  }));

  return (
    <div>
      {title && <h2>{title}</h2>}
      <SharedMasonry>
        {tileItems.map((tile) => (
          <div key={tile.id}>
            <Tile
              key={tile.id}
              item={tile}
            />
          </div>
        ))}
      </SharedMasonry>
    </div>
  );
}
