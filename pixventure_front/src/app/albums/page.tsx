// src/app/albums/page.tsx
"use client";

import React from "react";
import { useAlbumsAPI } from "../../utils/api/albums";
import Tile, { TileProps } from "../../components/Tile/Tile";
import PaginationComponent from "../../components/Pagination/Pagination";
import { usePaginatedData } from "../../hooks/usePaginatedData";

// The type for each album
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
  const { fetchAlbums } = useAlbumsAPI();

  // 1) Use our custom pagination hook
  const {
    data: albums,
    page,
    totalPages,
    loading,
    error,
    setPage,
  } = usePaginatedData<Album>(fetchAlbums);

  if (loading) return <p>Loading albums...</p>;
  if (error) return <p>Error: {error}</p>;

  // 2) Transform each album to match TileProps
  const tileItems: TileProps[] = albums.map((album) => ({
    id: album.id,
    name: album.name,
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
      <div className="pin_container">
        {tileItems.map((item) => (
          <Tile key={item.id} item={{ ...item, entity_type: "album" }} />
        ))}
      </div>

      {/* 3) Render pagination UI */}
      <PaginationComponent
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
}
