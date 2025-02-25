'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import AlbumElementTile from './AlbumElementTile';

interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  // etc.
}

// element_type=1 => post_data, element_type=2 => media_data
interface AlbumElement {
  id: number;
  element_type: number;
  position: number;
  post_data: null | {
    id: number;
    name: string;
    slug: string;
    likes_counter: number;
    has_liked: boolean;
    thumbnail_url: string;
  };
  media_data: null | {
    id: number;
    item_type: number;
    likes_counter: number;
    has_liked: boolean;
    thumbnail_url: string;
  };
  // other fields
}

export default function AlbumDetailPage() {
  const params = useParams();          // e.g. { slug: 'test-album' }
  const slug = params.slug as string;  // dynamic route segment

  const [album, setAlbum] = useState<Album | null>(null);
  const [elements, setElements] = useState<AlbumElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const fetchAlbumDetail = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. http://127.0.0.1:8000/api
        const res = await fetch(`${baseUrl}/albums/${slug}/`);
        if (!res.ok) {
          throw new Error(`Failed to fetch album: ${res.statusText}`);
        }
        const data = await res.json();
        // data = { album: {...}, album_elements: [...], count, next, prev }
        setAlbum(data.album);
        setElements(data.album_elements || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAlbumDetail();
  }, [slug]);

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
