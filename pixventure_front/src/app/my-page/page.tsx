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
  has_liked: boolean;
  owner_username: string;
  // other fields as needed
}

interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  owner_username: string | null;
  // You might add additional fields like thumbnail_url if available.
}

export default function MyPage() {
  const { fetchMyPosts } = usePostsAPI();
  const { fetchMyAlbums } = useAlbumsAPI();

  const [myPosts, setMyPosts] = useState<Post[]>([]);
  const [myAlbums, setMyAlbums] = useState<Album[]>([]);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [loadingAlbums, setLoadingAlbums] = useState(true);
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
    item_type: 1, // posts
    likes_counter: post.likes_counter,
    has_liked: post.has_liked,
    owner_username: post.owner_username,
    tile_size: "medium",
    entity_type: "post",
    page_type: "my-page",
  }));

  // Transform albums into TileProps.
  const albumTiles: TileProps[] = myAlbums.map((album) => ({
    id: album.id,
    name: album.name,
    slug: album.slug,
    // You may provide a thumbnail URL if available
    likes_counter: album.likes_counter,
    has_liked: false, // Or fetch if available.
    owner_username: album.owner_username || "",
    tile_size: "medium",
    entity_type: "album",
    page_type: "my-page",
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
            <Tile
              key={tile.id}
              item={tile}
            />
          ))}
        </div>
      </section>

      <section>
        <h2>My Albums</h2>
        {loadingAlbums && <p>Loading your albums...</p>}
        {errorAlbums && <p style={{ color: "red" }}>Error: {errorAlbums}</p>}
        {!loadingAlbums && myAlbums.length === 0 && (
          <p>You have no albums yet.</p>
        )}
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {albumTiles.map((tile) => (
            <Tile
              key={tile.id}
              item={tile}
            />
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
