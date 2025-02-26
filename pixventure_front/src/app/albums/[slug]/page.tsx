// src/app/album/[slug]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import AlbumElementTile from './AlbumElementTile';
import { useAlbumsAPI } from '../../../utils/api/albums';

interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked?: boolean;
  thumbnail_url?: string;
  // ...
}

// from your existing code
interface AlbumElement {
  id: number;
  element_type: number;
  position: number;
  post_data?: {
    // ...
  };
  media_data?: {
    // ...
  };
}

export default function AlbumDetailPage() {
  const params = useParams(); // e.g. { slug: 'test-album' }
  const slug = params.slug as string;

  const [album, setAlbum] = useState<Album | null>(null);
  const [elements, setElements] = useState<AlbumElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // custom hook
  const { fetchAlbumBySlug } = useAlbumsAPI();

  useEffect(() => {
    if (!slug) return;

    const loadAlbumDetail = async () => {
      try {
        const data = await fetchAlbumBySlug(slug);
        // data = { album: {...}, album_elements: [...], count, next, prev }
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

  return (
    <div>
      <h1>{album.name}</h1>
      <p>Likes: {album.likes_counter}</p>
      <p>{album.has_liked ? 'You liked this album' : 'Not liked yet'}</p>
      <hr />
      <h2>Album Elements</h2>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {elements.map((element) => (
          <AlbumElementTile key={element.id} element={element} />
        ))}
      </div>
    </div>
  );
}
