"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAlbumsAPI } from "../../../utils/api/albums";
import Tile, { TileProps } from "../../../components/Tile/Tile";
import LikeButton from "../../../elements/LikeButton/LikeButton";

// Example interfaces for album and album element data returned from the API.
interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url?: string;
  // ...other album fields
}

interface AlbumElement {
  id: number; // ID of the album element wrapper
  element_type: number; // 1 = post, 2 = media
  position: number;
  // The actionable entity data is nested here:
  post_data?: {
    id: number; // Actual post ID to be used for like and navigation
    name: string;
    slug: string;
    thumbnail_url?: string;
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    tile_size: "small" | "medium" | "large";
  };
  media_data?: {
    id: number; // Actual media item ID to be used for like and navigation
    name: string;
    slug: string;
    thumbnail_url?: string;
    item_type: number; // e.g. 1 = photo, 2 = video
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    images_count?: number;
    videos_count?: number;
    tile_size: "small" | "medium" | "large";
  };
}

export default function AlbumDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [album, setAlbum] = useState<Album | null>(null);
  const [elements, setElements] = useState<AlbumElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { fetchAlbumBySlug } = useAlbumsAPI();

  useEffect(() => {
    if (!slug) return;

    const loadAlbumDetail = async () => {
      try {
        const data = await fetchAlbumBySlug(slug);
        // Expected data: { album: {...}, album_elements: [...] }
        setAlbum(data.album);
        setElements(data.album_elements || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadAlbumDetail();
  }, [slug, fetchAlbumBySlug]);

  if (loading) return <p>Loading album...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!album) return <p>No album found for slug: {slug}</p>;

  /**
   * Transform an album element into TileProps.
   *
   * IMPORTANT:
   * - The outer album element is a wrapper and has its own id.
   * - The actionable entity (post or media) is nested inside as post_data or media_data.
   * - We use the inner entity's id for like toggling and navigation.
   * - To ensure that each rendered tile has a unique React key,
   *   we create a composite key combining the wrapper's id and the inner entity's id.
   */
  const transformAlbumElementToTile = (element: AlbumElement): TileProps => {
    if (element.element_type === 1 && element.post_data) {
      const post = element.post_data;
      return {
        // Use the inner post id for actionable purposes...
        id: post.id,
        // ...but use a composite key for rendering to ensure uniqueness.
        renderKey: `${element.id}-${post.id}`,
        name: post.name,
        slug: post.slug,
        thumbnail_url: post.thumbnail_url,
        item_type: 1, // posts
        likes_counter: post.likes_counter,
        has_liked: post.has_liked,
        owner_username: post.owner_username,
        tile_size: post.tile_size,
        targetType: "post",
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
        item_type: media.item_type as 1 | 2,
        likes_counter: media.likes_counter,
        has_liked: media.has_liked,
        owner_username: media.owner_username,
        images_count: media.images_count,
        videos_count: media.videos_count,
        tile_size: media.tile_size,
        targetType: "media",
      };
    }
    // Fallback if element data is missing:
    return {
      id: element.id,
      renderKey: String(element.id),
      name: "Unknown element",
      slug: "",
      item_type: 1,
      likes_counter: 0,
      has_liked: false,
      owner_username: "",
      tile_size: "small",
      targetType: "post",
    };
  };

  // Transform all album elements into TileProps.
  // Use the composite key for rendering.
  const tileItems: TileProps[] = elements.map(transformAlbumElementToTile);

  return (
    <div>
      <h1>{album.name}</h1>
      <LikeButton
        targetType={"album"}
        targetId={album.id}
        initialLikesCounter={album.likes_counter}
        initialHasLiked={album.has_liked}
      />
      <hr />
      <h2>Album Elements</h2>
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {tileItems.map((tile) => (
          <Tile
            key={tile.renderKey || tile.id}
            item={tile}
          />
        ))}
      </div>
    </div>
  );
}
