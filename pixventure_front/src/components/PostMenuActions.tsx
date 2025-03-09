// src/components/PostMenuActions.tsx
"use client";

import React, { useState } from "react";
import { usePostsAPI } from "../utils/api/posts";
import { useAlbumElementsAPI } from "../utils/api/albumElements";
import { useElementMenu } from "../contexts/ElementMenuContext";
import SelectAlbumMenu from "./SelectAlbumMenu";

interface PostMenuActionsProps {
  postId: number;
  canEdit?: boolean;
  /**
   * Optional album context data if the post is being viewed in an album.
   */
  albumContext?: {
    albumSlug: string;
    inAlbum: boolean;
    albumElementId?: number;
  };
}

/**
 * Renders action buttons for a post in the item context menu.
 * It allows adding/removing a post from an album and deleting the post (if the user can edit it).
 */
export default function PostMenuActions({
  postId,
  canEdit,
  albumContext,
}: PostMenuActionsProps) {
  const { closeMenu } = useElementMenu();
  const { deletePost } = usePostsAPI();
  const { addEntityToAlbum, removeEntityFromAlbum } = useAlbumElementsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAlbumModal, setShowAlbumModal] = useState(false);

  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    try {
      await deletePost(postId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to delete post.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddToAlbum = async () => {
    if (!albumContext || !albumContext.albumSlug) return;
    setLoading(true);
    setError(null);
    try {
      await addEntityToAlbum(albumContext.albumSlug, "post", postId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to add post to album.");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromAlbum = async () => {
    if (!albumContext || !albumContext.albumSlug || !albumContext.albumElementId) return;
    setLoading(true);
    setError(null);
    try {
      await removeEntityFromAlbum(albumContext.albumSlug, albumContext.albumElementId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to remove post from album.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-menu-actions">
      {albumContext && albumContext.albumSlug ? (
        <>
          {albumContext.inAlbum ? (
            <button onClick={handleRemoveFromAlbum} disabled={loading}>
              Remove from Album
            </button>
          ) : (
            <button onClick={handleAddToAlbum} disabled={loading}>
              Add to Album
            </button>
          )}
        </>
      ) : (
        <button onClick={() => setShowAlbumModal(true)} disabled={loading}>
          Save to Album
        </button>
      )}
      {canEdit && (
        <button onClick={handleDelete} disabled={loading}>
          Delete Post
        </button>
      )}
      {error && <p className="error text-danger">{error}</p>}
      {showAlbumModal && (
        <SelectAlbumMenu
          entityId={postId}
          entityType="post"
          onClose={() => setShowAlbumModal(false)}
          onSuccess={closeMenu}
        />
      )}
    </div>
  );
}
