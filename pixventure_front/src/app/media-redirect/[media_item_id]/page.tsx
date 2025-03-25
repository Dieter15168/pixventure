"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { usePostsAPI } from "@/utils/api/posts";

interface MediaRedirectMeta {
  post_id: number;
  post_slug: string;
  main_category_slug: string;
}

export default function MediaRedirectPage() {
  const { media_item_id } = useParams();
  const router = useRouter();
  const { fetchMediaRedirectMeta } = usePostsAPI();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function redirect() {
      try {
        const data: MediaRedirectMeta = await fetchMediaRedirectMeta(parseInt(media_item_id));
        // Construct URL in the usual format: /<main_category_slug>/<post_slug>/<media_item_id>
        const url = `/${data.main_category_slug}/${data.post_slug}/${media_item_id}`;
        router.push(url); // Use client-side navigation
      } catch (err: any) {
        setError(err.message || "Failed to fetch redirect information.");
      }
    }
    redirect();
  }, [media_item_id, fetchMediaRedirectMeta, router]);

  if (error) return <div>Error: {error}</div>;
  return <div>Redirecting...</div>;
}
