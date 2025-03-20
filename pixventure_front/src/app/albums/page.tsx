// src/app/albums/page.tsx
"use client";

import React from "react";
import { useAlbumsAPI } from "../../utils/api/albums";
import AlbumsList from "../../components/AlbumsList/AlbumsList";

export default function AlbumsPage() {
  const { fetchAlbums } = useAlbumsAPI();

  return (
    <div>
      <h1>Albums</h1>
      <AlbumsList fetchFunction={fetchAlbums} />
    </div>
  );
}
