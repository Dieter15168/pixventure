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
export default function PostMenuActions({ postId, canEdit, albumContext }: PostMenuActionsProps) {
  const { closeMenu } = useElementMenu();
  const { deletePost } = usePostsAPI();
  const { addPostToAlbum, removePostFromAlbum } = useAlbumElementsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles deletion of a post.
   */
  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    try {
      await deletePost(postId);
      // Optionally refresh the list or notify the user.
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to delete post.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles adding a post to an album.
   */
  const handleAddToAlbum = async () => {
    if (!albumContext || !albumContext.albumSlug) return;
    setLoading(true);
    setError(null);
    try {
      await addPostToAlbum(albumContext.albumSlug, postId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to add post to album.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles removing a post from an album.
   */
  const handleRemoveFromAlbum = async () => {
    if (!albumContext || !albumContext.albumSlug || !albumContext.albumElementId) return;
    setLoading(true);
    setError(null);
    try {
      await removePostFromAlbum(albumContext.albumSlug, albumContext.albumElementId);
      closeMenu();
    } catch (err: any) {
      setError(err.message || "Failed to remove post from album.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-menu-actions">
      {albumContext && albumContext.albumSlug && (
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
      )}
      {canEdit && (
        <button onClick={handleDelete} disabled={loading}>
          Delete Post
        </button>
      )}
      {error && <p className="error text-danger">{error}</p>}
    </div>
  );
}
