// src/components/PostMenuActions.tsx
"use client";

import React, { useState } from "react";
import { usePostsAPI } from "../utils/api/posts";
import { useAlbumElementsAPI } from "../utils/api/albumElements";
import { useElementMenu } from "../contexts/ElementMenuContext";

interface PostMenuActionsProps {
  postId: number;
  canEdit?: boolean;
  /**
   * Optional album context data if the item is viewed inside an album.
   */
  albumContext?: {
    albumSlug: string;
    inAlbum: boolean;
    albumElementId?: number;
  };
  /**
   * Callback to open the universal "Save to Album" modal.
   */
  onSaveToAlbum?: () => void;
}

/**
 * Renders action buttons for an item (post or media) in the item context menu.
 * Allows adding/removing the item from an album and deletion (if permitted).
 */
export default function PostMenuActions({
  postId,
  canEdit,
  albumContext,
  onSaveToAlbum,
}: PostMenuActionsProps) {
  const { closeMenu } = useElementMenu();
  const { deletePost } = usePostsAPI();
  const { addEntityToAlbum, removeEntityFromAlbum } = useAlbumElementsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    try {
      await deletePost(postId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to delete item.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddToAlbum = async () => {
    if (!albumContext || !albumContext.albumSlug) return;
    setLoading(true);
    setError(null);
    try {
      // Here, entityType is "post"; for media items, adjust accordingly.
      await addEntityToAlbum(albumContext.albumSlug, "post", postId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to add item to album.");
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
      setError(err.message || "Failed to remove item from album.");
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
        // When no album context exists, use the callback to open the universal modal.
        <button onClick={onSaveToAlbum} disabled={loading}>
          Save to Album
        </button>
      )}
      {canEdit && (
        <button onClick={handleDelete} disabled={loading}>
          Delete Item
        </button>
      )}
      {error && <p className="error text-danger">{error}</p>}
    </div>
  );
}
