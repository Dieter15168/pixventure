// src/components/AlbumsList/AlbumsList.tsx
"use client";

import React from "react";
import { usePaginatedData } from "@/hooks/usePaginatedData";
import PaginationComponent from "../Pagination/Pagination";
import Tile, { TileProps } from "../Tile/Tile";
import SharedMasonry from "../common/SharedMasonry";

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
  locked?: boolean;
  owner_username: string;
  created: string;
  updated: string;
  has_liked?: boolean;
  thumbnail_url?: string;
  tile_size: "small" | "medium" | "large";
  media_type: string;
}

interface AlbumsListProps {
  fetchFunction: (page: number) => Promise<any>;
  title?: string;
}

export default function AlbumsList({ fetchFunction, title }: AlbumsListProps) {
  // Use our pagination hook
  const {
    data: albums,
    page,
    totalPages,
    loading,
    error,
    setPage,
  } = usePaginatedData<Album>(fetchFunction);

  if (loading) return <p>Loading albums...</p>;
  if (error) return <p>Error: {error}</p>;

  // Transform each album into TileProps
  const tileItems: TileProps[] = albums.map((album) => ({
    id: album.id,
    name: album.name,
    // Build the slug for linking to single album
    slug: `albums/${album.slug}`,
    thumbnail_url: album.thumbnail_url,
    media_type: album.media_type,
    images_count: album.images_count,
    videos_count: album.videos_count,
    posts_count: album.posts_count,
    locked: album.locked,
    likes_counter: album.likes_counter,
    has_liked: album.has_liked ?? false,
    owner_username: album.owner_username,
    tile_size: album.tile_size,
    entity_type: "album",
    page_type: "albums_list",
  }));

  return (
    <div>
      {title && <h2>{title}</h2>}
      <SharedMasonry>
        {tileItems.map((item) => (
          <Tile
            key={item.id}
            item={item}
          />
        ))}
      </SharedMasonry>

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
