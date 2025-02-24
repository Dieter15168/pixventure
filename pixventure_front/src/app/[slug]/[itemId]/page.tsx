// app/[slug]/[itemId]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface ItemDetail {
  item_id: number;
  likes_counter: number;
  has_liked: boolean;
  previous_item_id: number | null;
  next_item_id: number | null;
  item_url: string;
  // add other fields if needed
}

interface Post {
  id: number;
  slug: string;
  // ...
}

export default function ItemViewerPage() {
  const params = useParams();
  const slug = params.slug;       // e.g. "test-post"
  const itemIdParam = params.itemId; // e.g. "2"
  
  const [post, setPost] = useState<Post | null>(null);
  const [itemDetail, setItemDetail] = useState<ItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug || !itemIdParam) return;

    const fetchData = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. "http://127.0.0.1:8000/api"
        
        // 1) Fetch the post using slug
        const postRes = await fetch(`${baseUrl}/posts/?slug=${slug}`);
        if (!postRes.ok) {
          throw new Error(`Failed to fetch post for slug ${slug}`);
        }
        const postData = await postRes.json();
        const foundPost = postData.results[0];
        if (!foundPost) {
          throw new Error(`No post found for slug: ${slug}`);
        }
        setPost(foundPost);

        // 2) Using foundPost.id, fetch the item detail
        const postId = foundPost.id;
        const itemId = parseInt(itemIdParam, 10);
        const itemRes = await fetch(`${baseUrl}/posts/${postId}/items/${itemId}/`);
        if (!itemRes.ok) {
          throw new Error(`Failed to fetch item ${itemId}`);
        }
        const detailData: ItemDetail = await itemRes.json();
        setItemDetail(detailData);

      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [slug, itemIdParam]);

  if (loading) return <p>Loading item...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!post || !itemDetail) return <p>No data found</p>;

  const { item_id, previous_item_id, next_item_id, item_url } = itemDetail;

  return (
    <div>
      <h2>Viewing Item #{item_id} of Post “{post.slug}”</h2>
      
      <div style={{ margin: '10px 0' }}>
        <img src={item_url} alt={`Item ${item_id}`} style={{ maxWidth: '400px' }} />
      </div>

      <div style={{ marginTop: '20px' }}>
        {previous_item_id && (
          <Link href={`/${slug}/${previous_item_id}`}>
            <button>Previous</button>
          </Link>
        )}

        {next_item_id && (
          <Link href={`/${slug}/${next_item_id}`}>
            <button style={{ marginLeft: '10px' }}>Next</button>
          </Link>
        )}
      </div>
    </div>
  );
}
