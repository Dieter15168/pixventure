// app/albums/AlbumTile.tsx

"use client"

import Link from "next/link";

interface Album {
  id: number;
  name: string;
  slug: string;
  thumbnail_url: string;
  likes_counter: number;
  has_liked: boolean;
  status: number;
  posts_count: number;
  images_count: number;
  videos_count: number;
  owner_username: string;
  show_creator_to_others: boolean;
  created: string;
  updated: string;

  // Additional fields if needed
}

export default function AlbumTile({ album }: { album: Album }) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 10 }}>
      <Link href={`/albums/${album.slug}`}>
        <img
          src={album.thumbnail_url}
          alt={album.name}
          style={{ width: "200px", height: "auto", cursor: "pointer" }}
        />
      </Link>
      <h3>{album.name}</h3>
      <p>Owner: {album.owner_username}</p>
      <p>Likes: {album.likes_counter}</p>
      <p>Posts: {album.posts_count}</p>
      <p>
        Images: {album.images_count}, Videos: {album.videos_count}
      </p>
      <p>Created: {new Date(album.created).toLocaleString()}</p>
      <p>{album.has_liked ? "You liked this album" : "Not liked yet"}</p>
    </div>
  );
}
