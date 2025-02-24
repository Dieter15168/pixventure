'use client';

import { useEffect, useState } from 'react';
import AlbumTile from './AlbumTile';

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
}

export default function AlbumsPage() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. http://127.0.0.1:8000/api
        const res = await fetch(`${apiUrl}/albums/`);
        if (!res.ok) {
          throw new Error(`Error fetching albums: ${res.statusText}`);
        }
        const data = await res.json();
        setAlbums(data.results);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAlbums();
  }, []);

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
