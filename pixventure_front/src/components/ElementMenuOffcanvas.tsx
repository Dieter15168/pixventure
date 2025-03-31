// src/components/ElementMenuOffcanvas.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Offcanvas } from "react-bootstrap";
import { useElementMenu } from "../contexts/ElementMenuContext";
import { usePostsAPI } from "../utils/api/posts";
import ElementContextMenuContent from "@/components/ElementContextMenuContent/ElementContextMenuContent";
import SelectAlbumMenu from "./SelectAlbumMenu";
import { useRouter } from "next/navigation";

export default function ElementMenuOffcanvas() {
  const { showMenu, closeMenu, selectedItem } = useElementMenu();
  const { fetchPostMeta, deletePost } = usePostsAPI();
  const router = useRouter();

  const [postMeta, setPostMeta] = useState<any>(null);
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

  // Open the "Save to Album" modal.
  const handleOpenSelectAlbum = () => {
    setShowSelectAlbumModal(true);
  };

  const handleCloseSelectAlbum = () => {
    setShowSelectAlbumModal(false);
  };

  // Delete the post and refresh the view.
  const handleDelete = async () => {
    if (!selectedItem) return;
    try {
      await deletePost(selectedItem.id);
      closeMenu();
      router.refresh(); // Refresh the page to update the list after deletion.
    } catch (err: any) {
      console.error("Deletion failed", err);
      setError(err.message || "Failed to delete item.");
    }
  };

  // Navigate to the edit page for the post.
  const handleEdit = () => {
    if (!postMeta) return;
    router.push(`/edit-post/${postMeta.id}`);
    closeMenu();
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
          {loadingMeta && <p>Loading post meta...</p>}
          {error && <p className="text-danger">{error}</p>}
          <ElementContextMenuContent
            postMeta={postMeta}
            onSaveToAlbum={handleOpenSelectAlbum}
            onDelete={handleDelete}
            onEdit={handleEdit}
          />
        </Offcanvas.Body>
      </Offcanvas>
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
