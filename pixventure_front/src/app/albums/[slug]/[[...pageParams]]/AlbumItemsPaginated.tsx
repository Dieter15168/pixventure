// src/app/albums/[slug]/[[...pageParams]]/AlbumItemsPaginated.tsx

"use client";

import React, { useCallback } from "react";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { usePaginatedData } from "@/hooks/usePaginatedData";
import { useAlbumsAPI } from "@/utils/api/albums";
import Tile, { TileProps } from "@/components/Tile/Tile";
import PaginationComponent from "@/components/Pagination/Pagination";
import LikeButton from "@/elements/LikeButton/LikeButton";
import SharedMasonry from "@/components/common/SharedMasonry";

// Minimal type definitions:
interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked: boolean;
  can_edit: boolean;
  thumbnail_url?: string;
  locked: boolean;
}

interface AlbumElement {
  id: number;
  element_type: number; // 1 = post, 2 = media
  position: number;
  post_data?: {
    id: number;
    name: string;
    slug: string;
    thumbnail_url?: string;
    locked: boolean;
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
    locked: boolean;
    media_type: string;
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    tile_size: "small" | "medium" | "large";
  };
}

interface AlbumItemsPaginatedProps {
  album: Album;
}

export default function AlbumItemsPaginated({
  album,
}: AlbumItemsPaginatedProps) {
  // The base path for album elements pages will be "/albums/{album.slug}".
  const basePath = `/albums/${album.slug}`;
  // Use our custom hook to derive current page from the route's optional catch-all.
  // This hook synchronously computes the current page from useParams.
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);

  const { fetchAlbumElementsBySlug } = useAlbumsAPI();
  const fetchFunction = useCallback(
    async (page: number) => {
      return await fetchAlbumElementsBySlug(album.slug, page);
    },
    [album, fetchAlbumElementsBySlug]
  );

  // Now call the paginated data hook using the derived current page.
  const {
    data: albumElements,
    totalPages,
    loading: elementsLoading,
    error: elementsError,
  } = usePaginatedData<AlbumElement>(fetchFunction, currentPage);

  // Transform album elements into TileProps.
  const transformAlbumElementToTile = (element: AlbumElement): TileProps => {
    if (element.element_type === 1 && element.post_data) {
      const post = element.post_data;
      return {
        id: post.id,
        renderKey: `${element.id}-${post.id}`,
        name: post.name,
        slug: post.slug,
        thumbnail_url: post.thumbnail_url,
        locked: post.locked,
        media_type: post.media_type ?? 1,
        likes_counter: post.likes_counter,
        has_liked: post.has_liked,
        owner_username: post.owner_username,
        tile_size: post.tile_size,
        entity_type: "post",
        page_type: "album",
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
        locked: media.locked,
        media_type: media.media_type,
        likes_counter: media.likes_counter,
        has_liked: media.has_liked,
        owner_username: media.owner_username,
        tile_size: media.tile_size,
        entity_type: "media",
        page_type: "album",
        albumContext: {
          albumSlug: album.slug,
          inAlbum: true,
          albumElementId: element.id,
          can_edit: album.can_edit,
        },
      };
    }
    // Fallback if data is missing:
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

  if (elementsLoading) return <p>Loading album elements...</p>;
  if (elementsError)
    return <p>Error loading album elements: {elementsError}</p>;

  return (
    <div>
      <LikeButton
        entity_type="album"
        targetId={album.id}
        initialLikesCounter={album.likes_counter}
        initialHasLiked={album.has_liked}
      />
      <hr />
      <h2>Album Elements</h2>
      <SharedMasonry>
        {tileItems.map((tile) => (
          <Tile
            key={tile.renderKey}
            item={tile}
          />
        ))}
      </SharedMasonry>
      {totalPages > 1 && (
        <PaginationComponent
          currentPage={currentPage}
          totalPages={totalPages}
          buildPageUrl={buildPageUrl}
        />
      )}
    </div>
  );
}
