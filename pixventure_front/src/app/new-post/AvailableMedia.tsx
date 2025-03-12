// src/app/new-post/AvailableMedia.tsx
"use client";

import React from "react";
import Tile from "../../components/Tile/Tile";
import { TileProps } from "../../components/Tile/Tile";

// This is the same shape you returned from the backend
export interface MinimalMediaItemDTO {
  id: number;
  media_type: "photo" | "video" | "unknown";
  status: string; // e.g. "Pending moderation"
  thumbnail_url: string;
  width: number | null;
  height: number | null;
  file_size: number | null;
}

// Convert the DTO to the `TileProps` shape
function mapDTOtoTileProps(item: MinimalMediaItemDTO): TileProps {
  return {
    id: item.id,
    // If you need a user-friendly name:
    name: `Media #${item.id}`,
    slug: `media-${item.id}`,
    thumbnail_url: item.thumbnail_url || undefined,
    media_type: item.media_type === "unknown" ? "photo" : item.media_type,

    // Hard-coded or zero for fields we don't use here
    images_count: 0,
    videos_count: 0,
    posts_count: 0,
    likes_counter: 0,
    has_liked: false,
    owner_username: "",
    lock_logo: false,
    is_moderation: item.status === "Pending moderation",
    tile_size: "small",
    canAddToAlbum: false,
    entity_type: "media",
    page_type: "posts_list",
  };
}

interface AvailableMediaProps {
  loading: boolean;
  mediaItems: MinimalMediaItemDTO[];
}

export default function AvailableMedia({
  loading,
  mediaItems,
}: AvailableMediaProps) {
  if (loading) {
    return <div>Loading available media...</div>;
  }

  if (!mediaItems || mediaItems.length === 0) {
    return <div>No media items available.</div>;
  }

  return (
    <div>
      <h2>Available Media Items</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {mediaItems.map((item) => {
          const tileProps = mapDTOtoTileProps(item);
          return <Tile key={item.id} item={tileProps} />;
        })}
      </div>
    </div>
  );
}
