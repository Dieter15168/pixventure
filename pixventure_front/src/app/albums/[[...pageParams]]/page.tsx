// src/app/albums/[[...pageParams]]/page.tsx
"use client";

import React from "react";
import { usePaginatedRoute } from "@/hooks/usePaginatedRoute";
import { useAlbumsAPI } from "@/utils/api/albums";
import PaginatedRoute from "@/components/routes/PaginatedRoute";
import AlbumsList from "@/components/AlbumsList/AlbumsList";

export default function AlbumsPage() {
  const basePath = "/albums";
  const { currentPage, buildPageUrl } = usePaginatedRoute(basePath, 1);
  const { fetchAlbums } = useAlbumsAPI();

  const fetchFunction = async (page: number) => {
    return await fetchAlbums(page);
  };

  return (
    <div>
      <h1>Albums</h1>
      <PaginatedRoute
        currentPage={currentPage}
        buildPageUrl={buildPageUrl}
        fetchFunction={fetchFunction}
        title="Albums"
        ListComponent={AlbumsList}
      />
    </div>
  );
}
