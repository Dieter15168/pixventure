// src/app/my-page/page.tsx
"use client";

import React from "react";
import { usePostsAPI } from "../../utils/api/posts";
import { useAlbumsAPI } from "../../utils/api/albums";
import PostsList from "../../components/PostsList/PostsList";
import AlbumsList from "../../components/AlbumsList/AlbumsList";
import Link from "next/link";

export default function MyPage() {
  const { fetchMyPostsPaginated } = usePostsAPI();
  const { fetchMyAlbumsPaginated } = useAlbumsAPI();

  return (
    <div>
      <h1>My Page</h1>

      <section>
        <h2>My Posts</h2>
        <PostsList fetchFunction={fetchMyPostsPaginated} />
      </section>

      <section>
        <h2>My Albums</h2>
        <AlbumsList fetchFunction={fetchMyAlbumsPaginated} />
        <div style={{ marginTop: "1rem" }}>
          <Link href="/albums/new">Create a New Album</Link>
        </div>
      </section>
    </div>
  );
}
