// src/app/albums/page.tsx
'use client';

import { useEffect, useState } from 'react';
import AlbumTile from './AlbumTile';
import { useAlbumsAPI } from '../../utils/api/albums';

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
  show_creator_to_others: boolean;
  created: string;
  updated: string;
  has_liked?: boolean;
  thumbnail_url?: string;
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

  return (
    <div>
      <h1>Albums</h1>
      <div style={{ display: 'grid', gap: '10px' }}>
        {albums.map((album) => (
          <AlbumTile key={album.id} album={album} />
        ))}
      </div>
    </div>
  );
}
