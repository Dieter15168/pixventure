// src/components/SelectAlbumMenu.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Modal, Button, ListGroup } from "react-bootstrap";
import { useAlbumsAPI } from "../utils/api/albums";
import { useAlbumElementsAPI } from "../utils/api/albumElements";

interface Album {
  id: number;
  name: string;
  slug: string;
  likes_counter: number;
  owner_username: string | null;
}

interface SelectAlbumMenuProps {
  entityId: number;
  entityType: "post" | "media";
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * A modal component that displays the current user's albums (from /api/albums/mine/)
 * and allows the user to select one to add the entity.
 */
export default function SelectAlbumMenu({
  entityId,
  entityType,
  onClose,
  onSuccess,
}: SelectAlbumMenuProps) {
  // Use fetchMyAlbums instead of fetchAlbums
  const { fetchMyAlbums } = useAlbumsAPI();
  const { addEntityToAlbum } = useAlbumElementsAPI();
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState<number | null>(null);

  // Helper function to extract error messages
  const extractErrorMessage = (err: any) => {
    return err.response?.data?.detail || err.response?.data || err.message || "An unknown error occurred.";
  };

  useEffect(() => {
    const loadAlbums = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchMyAlbums();
        setAlbums(data);
      } catch (err: any) {
        setError(extractErrorMessage(err) || "Failed to load albums");
      } finally {
        setLoading(false);
      }
    };
    loadAlbums();
  }, [fetchMyAlbums]);

  const handleAlbumClick = async (albumSlug: string, albumId: number) => {
    setAdding(albumId);
    try {
      await addEntityToAlbum(albumSlug, entityType, entityId);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(extractErrorMessage(err) || "Failed to add item to album");
    } finally {
      setAdding(null);
    }
  };

  return (
    <Modal show onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Select Album</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && <p>Loading albums...</p>}
        {error && <p className="text-danger">{error}</p>}
        {!loading && !error && albums.length === 0 && <p>No albums found.</p>}
        <ListGroup>
          {albums.map((album) => (
            <ListGroup.Item key={album.id}>
              <Button
                variant="outline-primary"
                onClick={() => handleAlbumClick(album.slug, album.id)}
                disabled={adding === album.id}
              >
                {album.name} {adding === album.id && "(Saving...)"}
              </Button>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
