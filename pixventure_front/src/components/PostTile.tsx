'use client';

import React from 'react';
import Link from 'next/link';

type PostTileProps = {
  post: {
    id: number;
    name: string;
    likes_counter: number;
    images_count: number;
    videos_count: number;
    has_liked: boolean;
    thumbnail_url: string;
    owner_username: string;
    slug: string;
  };
};

const PostTile: React.FC<PostTileProps> = ({ post }) => {
  return (
    <div style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
      <Link href={`/${post.slug}`}>
        <div>
          <img src={post.thumbnail_url} alt={post.name} style={{ width: '100px', height: '100px' }} />
        </div>
      </Link>
      <div>
        <h3>{post.name}</h3>
        <p>Owner: {post.owner_username}</p>
        <p>Likes: {post.likes_counter}</p>
        <p>Images: {post.images_count}</p>
        <p>Videos: {post.videos_count}</p>
        <p>Has Liked: {post.has_liked ? 'Yes' : 'No'}</p>
      </div>
    </div>
  );
};

export default PostTile;