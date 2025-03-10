// src/app/albums/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useAlbumsAPI } from "../../utils/api/albums";
import Tile, { TileProps } from "../../components/Tile/Tile";

interface Album {
  id: number;
  name: string;
  slug: string;
  status: number;
  likes_counter: number;
  posts_count: number;
  images_count: number;
  videos_count: number;
  owner_username: string;
  created: string;
  updated: string;
  has_liked?: boolean;
  thumbnail_url?: string;
  tile_size: "small" | "medium" | "large";
  media_type: string;
}

export default function AlbumsPage() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Use our custom hook
  const { fetchAlbums } = useAlbumsAPI();

  useEffect(() => {
    const loadAlbums = async () => {
      try {
        const data = await fetchAlbums();
        setAlbums(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadAlbums();
  }, [fetchAlbums]);

  if (loading) return <p>Loading albums...</p>;
  if (error) return <p>Error: {error}</p>;

  // We'll transform each album to match TileProps
  const tileItems: TileProps[] = albums.map((album) => ({
    id: album.id,
    name: album.name,
    // slug for the album detail route, e.g. "/albums/[slug]"
    slug: `albums/${album.slug}`,
    thumbnail_url: album.thumbnail_url,
    media_type: album.media_type,
    images_count: album.images_count,
    videos_count: album.videos_count,
    posts_count: album.posts_count,
    likes_counter: album.likes_counter,
    has_liked: album.has_liked ?? false,
    owner_username: album.owner_username,
    tile_size: album.tile_size,
    entity_type: "album",
    page_type: "albums_list",
  }));

  return (
    <div>
      <h1>Albums</h1>
      {/* a container that could be .pin_container if you want the masonry layout */}
      <div className="pin_container">
        {tileItems.map((item) => (
          <Tile
            key={item.id}
            item={{ ...item, entity_type: "album" }}
          />
        ))}
      </div>
    </div>
  );
}
