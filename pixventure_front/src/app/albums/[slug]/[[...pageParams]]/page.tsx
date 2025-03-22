// src/app/albums/[slug]/[[...pageParams]]/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useAlbumsAPI } from "@/utils/api/albums";
import AlbumItemsPaginated from "./AlbumItemsPaginated";

export default function AlbumDetailPage() {
  const { slug } = useParams() as { slug: string };
  const { fetchAlbumBySlug } = useAlbumsAPI();

  const [album, setAlbum] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    (async () => {
      setLoading(true);
      try {
        const albumData = await fetchAlbumBySlug(slug);
        setAlbum(albumData);
      } catch (err: any) {
        setError(err.message || "Error loading album");
      } finally {
        setLoading(false);
      }
    })();
  }, [slug, fetchAlbumBySlug]);

  if (loading) return <p>Loading album...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!album) return <p>No album found for slug: {slug}</p>;

  return (
    <div>
      <h1>{album.name}</h1>
      {/* Render any album meta here (e.g. LikeButton, etc.) */}
      <AlbumItemsPaginated album={album} />
    </div>
  );
}