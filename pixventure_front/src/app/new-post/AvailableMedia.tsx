// src/app/new-post/AvailableMedia.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI, MinimalMediaItemDTO } from "../../utils/api/media";
import Tile from "../../components/Tile/Tile";
import { TileProps } from "../../components/Tile/Tile";

/**
 * Maps the data from MinimalMediaItemDTO into the shape Tile expects.
 * We only fill the props we care about for this scenario.
 */
function mapDTOtoTileProps(item: MinimalMediaItemDTO): TileProps {
  return {
    id: item.id,
    // For "name" & "slug", you can adapt to your business logic.
    // If your MediaItem has no name/slug, you can just do placeholders or pass item.id.
    name: `Media #${item.id}`,
    slug: `media-${item.id}`,
    thumbnail_url: item.thumbnail_url ?? undefined,
    media_type: item.media_type_str === "unknown" ? "photo" : item.media_type_str,

    // Hard-coded or zero for fields we don't use here
    images_count: 0,
    videos_count: 0,
    posts_count: 0,
    likes_counter: 0,
    has_liked: false,
    owner_username: "",
    lock_logo: false,
    is_moderation: item.status_str === "Pending moderation",
    tile_size: "small",
    canAddToAlbum: false,
    entity_type: "media",
    page_type: "posts_list",
  };
}

export default function AvailableMedia() {
  const { fetchAvailableMedia } = useMediaAPI();
  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await fetchAvailableMedia();
        setMediaItems(data);
      } catch (err) {
        console.error("Failed to fetch available media:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [fetchAvailableMedia]);

  if (loading) {
    return <div>Loading available media...</div>;
  }

  if (mediaItems.length === 0) {
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
