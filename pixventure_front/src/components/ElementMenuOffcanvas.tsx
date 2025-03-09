// src/components/ElementMenuOffcanvas.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Offcanvas } from "react-bootstrap";
import { useElementMenu } from "../contexts/ElementMenuContext";
import { usePostsAPI } from "../utils/api/posts";
import TermDisplay from "./TermDisplay";
import PostMenuActions from "./PostMenuActions";
import SelectAlbumMenu from "./SelectAlbumMenu";

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
 * Shows meta data for items and renders entity-specific action components.
 */
export default function ElementMenuOffcanvas() {
  const { showMenu, closeMenu, selectedItem } = useElementMenu();
  const { fetchPostMeta } = usePostsAPI();

  const [postMeta, setPostMeta] = useState<PostMetaData | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSelectAlbumModal, setShowSelectAlbumModal] = useState(false);

  useEffect(() => {
    if (!showMenu || !selectedItem) return;

    if (selectedItem.entity_type === "post") {
      loadPostMeta(selectedItem.id);
    } else {
      setPostMeta(null);
    }
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

  // Callback to open the universal SelectAlbumMenu modal.
  const handleOpenSelectAlbum = () => {
    setShowSelectAlbumModal(true);
  };

  const handleCloseSelectAlbum = () => {
    setShowSelectAlbumModal(false);
  };

  if (!selectedItem) return null;

  return (
    <>
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
          {selectedItem.entity_type === "post" && (
            <>
              {loadingMeta && <p>Loading post meta...</p>}
              {error && <p className="text-danger">{error}</p>}
              {postMeta && (
                <div>
                  <p>
                    <strong>{postMeta.name}</strong> (owner:{" "}
                    {postMeta.owner_username})
                  </p>
                  <TermDisplay
                    categories={postMeta.categories}
                    tags={postMeta.tags}
                  />
                </div>
              )}
              <PostMenuActions
                postId={selectedItem.id}
                canEdit={postMeta?.can_edit}
                // Pass album context if available (for example, when viewing an album)
                albumContext={selectedItem.pageContext}
                onSaveToAlbum={handleOpenSelectAlbum}
              />
            </>
          )}
          {selectedItem.entity_type === "media" && (
            <>
              {/* For media items, similar logic would apply */}
              <p>Media item details go here...</p>
              <PostMenuActions
                postId={selectedItem.id}
                onSaveToAlbum={handleOpenSelectAlbum}
              />
            </>
          )}
          {selectedItem.entity_type === "album" && (
            <p>Album actions go here...</p>
          )}
          {selectedItem.entity_type === "user" && (
            <p>User actions go here...</p>
          )}
        </Offcanvas.Body>
      </Offcanvas>
      {/* Render the universal SelectAlbumMenu modal for posts and media */}
      {showSelectAlbumModal &&
        selectedItem &&
        (selectedItem.entity_type === "post" ||
          selectedItem.entity_type === "media") && (
          <SelectAlbumMenu
            entityId={selectedItem.id}
            entityType={selectedItem.entity_type as "post" | "media"}
            onClose={handleCloseSelectAlbum}
            onSuccess={closeMenu}
          />
        )}
    </>
  );
}
