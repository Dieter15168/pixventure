"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAlbumsAPI } from "../../../utils/api/albums";
import Tile, { TileProps } from "../../../components/Tile/Tile";

// Example interfaces for album and album element data returned from the API.
interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked?: boolean;
  thumbnail_url?: string;
  // ...other album fields
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
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    // other post fields if needed
  };
  media_data?: {
    id: number;
    name: string;
    slug: string;
    thumbnail_url?: string;
    item_type: number; // e.g. 1 = photo, 2 = video
    likes_counter: number;
    has_liked: boolean;
    owner_username: string;
    images_count?: number;
    videos_count?: number;
    // other media fields if needed
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

  // Helper function to transform an album element to TileProps.
  const transformAlbumElementToTile = (element: AlbumElement): TileProps => {
    // If the element represents a post:
    if (element.element_type === 1 && element.post_data) {
      const post = element.post_data;
      return {
        id: element.id, // You might want to use post.id instead
        name: post.name,
        slug: post.slug, // URL to the post detail page
        thumbnail_url: post.thumbnail_url,
        // We use item_type = 1 for posts
        item_type: 1,
        likes_counter: post.likes_counter,
        has_liked: post.has_liked,
        owner_username: post.owner_username,
        size: "small",
      };
    }
    // If the element represents a media item:
    if (element.element_type === 2 && element.media_data) {
      const media = element.media_data;
      return {
        id: element.id, // Or media.id if preferred
        name: media.name,
        slug: media.slug, // URL to the media detail page
        thumbnail_url: media.thumbnail_url,
        // Use media.item_type (1 = photo, 2 = video)
        item_type: media.item_type as 1 | 2,
        likes_counter: media.likes_counter,
        has_liked: media.has_liked,
        owner_username: media.owner_username,
        images_count: media.images_count,
        videos_count: media.videos_count,
        size: "small",
      };
    }
    // Fallback for unknown elements:
    return {
      id: element.id,
      name: "Unknown element",
      slug: "",
      item_type: 1,
      likes_counter: 0,
      has_liked: false,
      owner_username: "",
      size: "small",
    };
  };

  // Transform all album elements to TileProps
  const tileItems: TileProps[] = elements.map(transformAlbumElementToTile);

  return (
    <div>
      <h1>{album.name}</h1>
      <p>Likes: {album.likes_counter}</p>
      <p>{album.has_liked ? "You liked this album" : "Not liked yet"}</p>
      <hr />
      <h2>Album Elements</h2>
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {tileItems.map((tile) => (
          <Tile
            key={tile.id}
            item={tile}
          />
        ))}
      </div>
    </div>
  );
}
