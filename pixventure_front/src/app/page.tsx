// src/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import PostTile from "../components/Tile/Tile";
import { usePostsAPI } from "../utils/api/posts";

interface Post {
  id: number;
  name: string;
  likes_counter: number;
  has_liked: boolean;
  slug: string;
}

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { fetchPosts } = usePostsAPI();

  useEffect(() => {
    const getPosts = async () => {
      try {
        const data = await fetchPosts();
        setPosts(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    getPosts();
  }, [fetchPosts]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="pin_container">
      {posts.map((post) => (
        <PostTile
          key={post.id}
          item={{
            ...post,
            entity_type: "post",
            page_type: "posts_list",
          }}
        />
      ))}
    </div>
  );
}
