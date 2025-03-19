// src/app/albums/[slug]/page.tsx
"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import PaginationComponent from "../../../components/Pagination/Pagination";
import { useAlbumsAPI } from "../../../utils/api/albums";
import { usePaginatedData } from "../../../hooks/usePaginatedData";
import Tile, { TileProps } from "../../../components/Tile/Tile";
import LikeButton from "../../../elements/LikeButton/LikeButton";

// Minimal types for clarity
interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked: boolean;
  can_edit: boolean;
  thumbnail_url?: string;
}

interface AlbumElement {
  id: number;
  element_type: number; // 1=post, 2=media
  position: number;
  post_data?: {
    id: number;
    name: string;
    slug: string;
    thumbnail_url?: string;
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    tile_size: "small" | "medium" | "large";
    media_type?: number;
  };
  media_data?: {
    id: number;
    name: string;
    slug: string;
    thumbnail_url?: string;
    media_type: string;
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    tile_size: "small" | "medium" | "large";
  };
}

export default function AlbumDetailPage() {
  const { slug } = useParams() as { slug: string };
  const { fetchAlbumBySlug, fetchAlbumElementsBySlug } = useAlbumsAPI();

  // 1) Load the album metadata
  const [album, setAlbum] = useState<Album | null>(null);
  const [albumLoading, setAlbumLoading] = useState<boolean>(true);
  const [albumError, setAlbumError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    const loadAlbum = async () => {
      setAlbumLoading(true);
      try {
        const albumData = await fetchAlbumBySlug(slug);
        setAlbum(albumData);
      } catch (err: any) {
        setAlbumError(err.message ?? "Error loading album");
      } finally {
        setAlbumLoading(false);
      }
    };
    loadAlbum();
  }, [slug, fetchAlbumBySlug]);

  // 2) Define a function for fetching album elements (paginated)
  // If album is not yet loaded, return an empty structure to avoid errors or loops
  const fetchAlbumElements = useCallback(
    async (page: number) => {
      if (!album) {
        return {
          results: [],
          current_page: 1,
          total_pages: 1,
        };
      }
      return await fetchAlbumElementsBySlug(album.slug, page);
    },
    [album, fetchAlbumElementsBySlug]
  );

  // 3) Use the pagination hook for album elements
  const {
    data: albumElements,
    page,
    totalPages,
    loading: elementsLoading,
    error: elementsError,
    setPage,
  } = usePaginatedData<AlbumElement>(fetchAlbumElements);

  // 4) Basic checks
  if (albumLoading) return <p>Loading album...</p>;
  if (albumError) return <p>Error: {albumError}</p>;
  if (!album) return <p>No album found for slug: {slug}</p>;

  // If the album is loaded, but elements are still fetching
  if (elementsLoading && albumElements.length === 0) {
    return <p>Loading album elements...</p>;
  }
  if (elementsError) {
    return <p>Error loading album elements: {elementsError}</p>;
  }

  // 5) Transform each album element -> TileProps
  const transformAlbumElementToTile = (element: AlbumElement): TileProps => {
    // Check whether it's referencing a post or media
    if (element.element_type === 1 && element.post_data) {
      const post = element.post_data;
      return {
        id: post.id,
        renderKey: `${element.id}-${post.id}`,
        name: post.name,
        slug: post.slug,
        thumbnail_url: post.thumbnail_url,
        media_type: post.media_type ?? 1,
        likes_counter: post.likes_counter,
        has_liked: post.has_liked,
        owner_username: post.owner_username,
        tile_size: post.tile_size,
        entity_type: "post",
        albumContext: {
          albumSlug: album.slug,
          inAlbum: true,
          albumElementId: element.id,
          can_edit: album.can_edit,
        },
      };
    }
    if (element.element_type === 2 && element.media_data) {
      const media = element.media_data;
      return {
        id: media.id,
        renderKey: `${element.id}-${media.id}`,
        name: media.name,
        slug: media.slug,
        thumbnail_url: media.thumbnail_url,
        media_type: media.media_type,
        likes_counter: media.likes_counter,
        has_liked: media.has_liked,
        owner_username: media.owner_username,
        tile_size: media.tile_size,
        entity_type: "media",
        albumContext: {
          albumSlug: album.slug,
          inAlbum: true,
          albumElementId: element.id,
          can_edit: album.can_edit,
        },
      };
    }
    // fallback
    return {
      id: element.id,
      renderKey: String(element.id),
      name: "Unknown element",
      slug: "",
      media_type: 1,
      likes_counter: 0,
      has_liked: false,
      owner_username: "",
      tile_size: "small",
      entity_type: "post",
      albumContext: {
        albumSlug: album.slug,
        inAlbum: true,
        albumElementId: element.id,
        can_edit: album.can_edit,
      },
    };
  };

  const tileItems: TileProps[] = albumElements.map(transformAlbumElementToTile);

  return (
    <div>
      <h1>{album.name}</h1>
      <LikeButton
        entity_type="album"
        targetId={album.id}
        initialLikesCounter={album.likes_counter}
        initialHasLiked={album.has_liked}
      />

      <hr />
      <h2>Album Elements</h2>

      <div className="pin_container">
        {tileItems.map((tile) => (
          <Tile
            key={tile.renderKey}
            item={tile}
          />
        ))}
      </div>

      {/* PAGINATION UI if multiple pages */}
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
