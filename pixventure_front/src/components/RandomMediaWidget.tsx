// src/components/RandomMediaWidget.tsx
"use client";

import React, { useEffect, useState } from "react";
import Tile, { TileProps } from "@/components/Tile/Tile";
import { useMediaAPI } from "@/utils/api/media";

interface RandomMediaItemDTO {
  id: number;
  media_type_str: "photo" | "video" | "unknown";
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url?: string | null;
  locked: boolean;
  tile_size: "small" | "medium" | "large";
  status_str: string;
}

/**
 * RandomMediaWidget fetches a specified number of random published media items 
 * (default 4) and renders each using the Tile component.
 */
const RandomMediaWidget: React.FC<{ count?: number }> = ({ count = 4 }) => {
  const { fetchRandomMedia } = useMediaAPI();
  const [items, setItems] = useState<RandomMediaItemDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRandomMedia() {
      try {
        setLoading(true);
        const data: RandomMediaItemDTO[] = await fetchRandomMedia(count);
        setItems(data);
      } catch (err: any) {
        setError(err.message || "Failed to load random media items.");
      } finally {
        setLoading(false);
      }
    }
    loadRandomMedia();
  }, [fetchRandomMedia, count]);

  if (loading) return <div>Loading random media...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!items.length) return <div>No media items found.</div>;

  // Map each RandomMediaItemDTO to the TileProps required by the Tile component.
  const tileItems: TileProps[] = items.map((dto) => {
    const mediaType: "photo" | "video" =
      dto.media_type_str === "video" ? "video" : "photo";
    return {
      id: dto.id,
      name: `Media ${dto.id}`, // Fallback name if not provided by backend
      slug: `media-${dto.id}`, // Construct a slug using the id
      thumbnail_url: dto.thumbnail_url || "",
      media_type: mediaType,
      likes_counter: dto.likes_counter,
      has_liked: dto.has_liked,
      owner_username: "unknown", // Default value; update if API provides owner info
      locked: dto.locked,
      tile_size: dto.tile_size,
      entity_type: "media",
      page_type: "posts_list", // Use an appropriate page type (or define a dedicated one if needed)
      status: dto.status_str,
    };
  });

  return (
    <div>
      <h2>Random Items</h2>
      <div className="random-media-grid">
        {tileItems.map((item) => (
          <Tile key={item.id} item={item} />
        ))}
      </div>
      <style jsx>{`
        .random-media-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          padding: 1rem;
        }
      `}</style>
    </div>
  );
};

export default RandomMediaWidget;
