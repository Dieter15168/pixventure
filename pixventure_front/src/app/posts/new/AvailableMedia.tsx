// src/app/new-post/AvailableMedia.tsx
"use client";

import React from "react";
import Tile, { TileProps } from "../../../components/Tile/Tile";

export interface MinimalMediaItemDTO {
  id: number;
  media_type: "photo" | "video" | "unknown";
  status: string; // "Pending moderation", "Approved", etc.
  thumbnail_url: string;
  width: number | null;
  height: number | null;
  file_size: number | null;
}

// Map your backend DTO to the tile shape
function mapDTOtoTileProps(
  item: MinimalMediaItemDTO
): Omit<TileProps, "selected" | "onSelectChange"> {
  return {
    id: item.id,
    name: `Media #${item.id}`,
    slug: `media-${item.id}`,
    thumbnail_url: item.thumbnail_url || undefined,
    media_type: item.media_type === "unknown" ? "photo" : item.media_type,

    images_count: 0,
    videos_count: 0,
    posts_count: 0,
    show_likes: false,
    likes_counter: 0,
    has_liked: false,
    owner_username: "",
    locked: false,

    status: item.status,
    tile_size: "medium",
    canAddToAlbum: false,
    entity_type: "media",
    page_type: "post_creation",
    selectMode: "checkbox",
  };
}

interface AvailableMediaProps {
  loading: boolean;
  mediaItems: MinimalMediaItemDTO[];

  // 1) new props from the parent
  selectedMediaIds: number[];
  onSelectChange: (id: number, newVal: boolean) => void;
}

export default function AvailableMedia({
  loading,
  mediaItems,
  selectedMediaIds,
  onSelectChange,
}: AvailableMediaProps) {
  if (loading) {
    return <div>Loading available media...</div>;
  }

  if (!mediaItems || mediaItems.length === 0) {
    return <div>No media items available.</div>;
  }

  return (
    <div className="pin_container">
      {mediaItems.map((item) => {
        const baseProps = mapDTOtoTileProps(item);

        // 2) Now we apply "selected" + "onSelectChange" to complete the TileProps
        const tileProps: TileProps = {
          ...baseProps,
          selected: selectedMediaIds.includes(item.id),
          onSelectChange: (id, isSelected) => onSelectChange(id, isSelected),
        };

        return (
          <Tile
            key={item.id}
            item={tileProps}
          />
        );
      })}
    </div>
  );
}
