'use client';

import { useEffect, useState } from 'react';
import PostTile from '../components/PostTile';
import { fetchPosts } from '../utils/api';

interface Post {
  id: number;
  name: string;
  likes_counter: number;
  images_count: number;
  videos_count: number;
  has_liked: boolean;
  thumbnail_url: string;
  owner_username: string;
}

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getPosts = async () => {
      try {
        const postsData = await fetchPosts();
        setPosts(postsData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    getPosts();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h1>Best Posts</h1>
      <div>
        {posts.map((post) => (
          <PostTile key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
