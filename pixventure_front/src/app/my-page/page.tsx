// src/app/my-page/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { usePostsAPI } from "../../utils/api/posts";
import { useAlbumsAPI } from "../../utils/api/albums";
import Tile, { TileProps } from "../../components/Tile/Tile";
import Link from "next/link";

interface Post {
  id: number;
  name: string;
  slug: string;
  thumbnail_url?: string;
  likes_counter: number;
  has_liked?: boolean; // might be undefined from backend
  owner_username: string;
  tile_size: "small" | "medium" | "large";
}

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
  created: string;
  updated: string;
  has_liked?: boolean; // might be undefined
  thumbnail_url?: string;
  tile_size: "small" | "medium" | "large";
}

export default function MyPage() {
  const { fetchMyPosts } = usePostsAPI();
  const { fetchMyAlbums } = useAlbumsAPI();

  const [myPosts, setMyPosts] = useState<Post[]>([]);
  const [myAlbums, setMyAlbums] = useState<Album[]>([]);
  const [loadingPosts, setLoadingPosts] = useState<boolean>(true);
  const [loadingAlbums, setLoadingAlbums] = useState<boolean>(true);
  const [errorPosts, setErrorPosts] = useState<string | null>(null);
  const [errorAlbums, setErrorAlbums] = useState<string | null>(null);

  useEffect(() => {
    const loadMyPosts = async () => {
      setLoadingPosts(true);
      setErrorPosts(null);
      try {
        const posts = await fetchMyPosts();
        setMyPosts(posts);
      } catch (err: any) {
        setErrorPosts(err.message || "Failed to load posts.");
      } finally {
        setLoadingPosts(false);
      }
    };

    const loadMyAlbums = async () => {
      setLoadingAlbums(true);
      setErrorAlbums(null);
      try {
        const albums = await fetchMyAlbums();
        setMyAlbums(albums);
      } catch (err: any) {
        setErrorAlbums(err.message || "Failed to load albums.");
      } finally {
        setLoadingAlbums(false);
      }
    };

    loadMyPosts();
    loadMyAlbums();
  }, [fetchMyPosts, fetchMyAlbums]);

  // Transform posts into TileProps for reuse with Tile component.
  const postTiles: TileProps[] = myPosts.map((post) => ({
    id: post.id,
    name: post.name,
    slug: post.slug,
    thumbnail_url: post.thumbnail_url,
    item_type: 1, // Set as constant for posts.
    likes_counter: post.likes_counter,
    has_liked: post.has_liked ?? false, // Ensure a boolean.
    owner_username: post.owner_username,
    tile_size: post.tile_size,
    entity_type: "post",
    page_type: "posts_list",
  }));

  // Transform albums into TileProps.
  const albumTiles: TileProps[] = myAlbums.map((album) => ({
    id: album.id,
    name: album.name,
    slug: album.slug,
    likes_counter: album.likes_counter,
    posts_count: album.posts_count,
    images_count: album.images_count,
    videos_count: album.videos_count,
    has_liked: album.has_liked ?? false,
    owner_username: album.owner_username,
    thumbnail_url: album.thumbnail_url,
    tile_size: album.tile_size,
    item_type: 3, // Set as constant for albums.
    entity_type: "album",
    page_type: "albums_list",
  }));

  return (
    <div style={{ padding: "1rem" }}>
      <h1>My Page</h1>

      <section style={{ marginBottom: "2rem" }}>
        <h2>My Posts</h2>
        {loadingPosts && <p>Loading your posts...</p>}
        {errorPosts && <p style={{ color: "red" }}>Error: {errorPosts}</p>}
        {!loadingPosts && myPosts.length === 0 && <p>You have no posts yet.</p>}
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {postTiles.map((tile) => (
            <Tile key={tile.id} item={tile} />
          ))}
        </div>
      </section>

      <section>
        <h2>My Albums</h2>
        {loadingAlbums && <p>Loading your albums...</p>}
        {errorAlbums && <p style={{ color: "red" }}>Error: {errorAlbums}</p>}
        {!loadingAlbums && myAlbums.length === 0 && <p>You have no albums yet.</p>}
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {albumTiles.map((tile) => (
            <Tile key={tile.id} item={tile} />
          ))}
        </div>
        <div style={{ marginTop: "1rem" }}>
          <Link
            href="/albums/new"
            style={{ color: "blue", textDecoration: "underline" }}
          >
            Create a New Album
          </Link>
        </div>
      </section>
    </div>
  );
}
