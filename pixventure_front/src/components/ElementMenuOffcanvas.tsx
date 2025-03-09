// src/components/ElementMenuOffcanvas.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Offcanvas } from "react-bootstrap";
import { useElementMenu } from "../contexts/ElementMenuContext";
import { usePostsAPI } from "../utils/api/posts";
import TermDisplay from "./TermDisplay"; // displays categories/tags
import PostMenuActions from "./PostMenuActions";

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
  can_edit: boolean;
}

/**
 * Offcanvas component that displays the item context menu.
 * It shows meta data for posts and renders entity-specific action components.
 */
export default function ElementMenuOffcanvas() {
  const { showMenu, closeMenu, selectedItem } = useElementMenu();
  const { fetchPostMeta } = usePostsAPI();

  const [postMeta, setPostMeta] = useState<PostMetaData | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!showMenu || !selectedItem) return;

    // If the item is a post, fetch its metadata (which now includes can_edit)
    if (selectedItem.entity_type === "post") {
      loadPostMeta(selectedItem.id);
    } else {
      setPostMeta(null);
    }
  }, [showMenu, selectedItem]);

  /**
   * Loads metadata for a given post.
   * @param postId The ID of the post.
   */
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
    <Offcanvas show={showMenu} onHide={closeMenu} placement="bottom" className="bg-dark text-light">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Options</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {selectedItem.entity_type === "post" && (
          <>
            {loadingMeta && <p>Loading post meta...</p>}
            {error && <p className="text-danger">{error}</p>}
            {postMeta && (
              <div>
                <p>
                  <strong>{postMeta.name}</strong> (owner: {postMeta.owner_username})
                </p>
                <TermDisplay categories={postMeta.categories} tags={postMeta.tags} />
              </div>
            )}
            <PostMenuActions
              postId={selectedItem.id}
              canEdit={postMeta?.can_edit}
              // Pass the pageContext received from the tile.
              albumContext={selectedItem.pageContext}
            />
          </>
        )}
        {selectedItem.entity_type === "album" && <p>Show album logic here if needed...</p>}
        {selectedItem.entity_type === "media" && <p>Show media logic here if needed...</p>}
        {selectedItem.entity_type === "user" && <p>Show user logic here if needed...</p>}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
