// src/components/ElementMenuOffcanvas.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Offcanvas } from "react-bootstrap";
import { useElementMenu } from "../contexts/ElementMenuContext";
import { usePostsAPI } from "../utils/api/posts";
import TermDisplay from "./TermDisplay"; // the new component from step #1

interface PostMetaData {
  id: number;
  name: string;
  slug: string;
  owner_username: string | null;
  categories: Array<{
    id: number;
    term_type: number;
    name: string;
    slug: string;
  }>;
  tags: Array<{ id: number; term_type: number; name: string; slug: string }>;
}

export default function ElementMenuOffcanvas() {
  const { showMenu, closeMenu, selectedItem } = useElementMenu();
  const { fetchPostMeta } = usePostsAPI();

  const [postMeta, setPostMeta] = useState<PostMetaData | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!showMenu || !selectedItem) return;

    // if item is a post, fetch meta
    if (selectedItem.entity_type === "post") {
      loadPostMeta(selectedItem.id);
    } else {
      // if not post, optionally reset postMeta
      setPostMeta(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showMenu, selectedItem]);

  const loadPostMeta = async (postId: number) => {
    setLoadingMeta(true);
    setError(null);
    try {
      const data = await fetchPostMeta(postId);
      setPostMeta(data);
    } catch (err: any) {
      console.error("Failed to fetch post meta", err);
      setError(err.message || "Failed to fetch post meta");
    } finally {
      setLoadingMeta(false);
    }
  };

  if (!selectedItem) return null;

  return (
    <Offcanvas
      show={showMenu}
      onHide={closeMenu}
      placement="bottom"
      className="bg-dark text-light"
    >
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Options</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {/* If item is post => show post meta logic */}
        {selectedItem.entity_type === "post" && (
          <div>
            {loadingMeta && <p>Loading post meta...</p>}
            {error && <p className="text-danger">{error}</p>}
            {postMeta && (
              <>
                <p>
                  <strong>{postMeta.name}</strong> (owner:{" "}
                  {postMeta.owner_username})
                </p>
                {/* Use the TermDisplay component for categories/tags */}
                <TermDisplay
                  categories={postMeta.categories}
                  tags={postMeta.tags}
                />
              </>
            )}
          </div>
        )}
        {/* If it's a media or album, etc. => handle differently */}
        {selectedItem.entity_type === "album" && (
          <p>Show album logic here if needed...</p>
        )}
        {selectedItem.entity_type === "media" && (
          <p>Show media logic here if needed...</p>
        )}
        {selectedItem.entity_type === "user" && (
          <p>Show user logic here if needed...</p>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
