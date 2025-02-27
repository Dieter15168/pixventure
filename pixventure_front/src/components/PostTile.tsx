'use client';

import { useState } from 'react';
import { useSocialAPI } from '../utils/api/social';

interface Post {
  id: number;
  name: string;
  likes_counter: number;
  has_liked: boolean;
  thumbnail_url: string;
  owner_username: string;
  // add other fields as needed
}

export default function PostTile({ post }: { post: Post }) {
  const [localPost, setLocalPost] = useState<Post>(post);

  const { toggleLike } = useSocialAPI();

  const handleToggleLike = async () => {
    try {
      const action = localPost.has_liked ? 'unlike' : 'like';
      const response = await toggleLike('post', localPost.id, action);

      // If the backend returns updated likes_counter and has_liked
      if (response.likes_counter !== undefined && response.has_liked !== undefined) {
        setLocalPost({
          ...localPost,
          likes_counter: response.likes_counter,
          has_liked: response.has_liked,
        });
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  return (
    <div style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
      <img src={localPost.thumbnail_url} alt={localPost.name} style={{ width: '100px' }} />
      <h2>{localPost.name}</h2>
      <p>Owner: {localPost.owner_username}</p>
      <p>Likes: {localPost.likes_counter}</p>
      <button onClick={handleToggleLike}>
        {localPost.has_liked ? 'Unlike' : 'Like'}
      </button>
    </div>
  );
}
