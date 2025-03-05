// src/components/ElementMenuOffcanvas.tsx
"use client";

import React from "react";
import { Offcanvas } from "react-bootstrap";
import { useElementMenu } from "../contexts/ElementMenuContext";

export default function ElementMenuOffcanvas() {
  const { showMenu, closeMenu, selectedItem } = useElementMenu();

  if (!selectedItem) return null; 
  // No item => nothing to show (or we can still open an empty menu if you want)

  const {
    item_type,
    name,
    canDelete,
    canAddToAlbum,
    categories = [],
    tags = [],
  } = selectedItem;

  const handleDelete = () => {
    console.log("Deleting item id", selectedItem.id, "of item_type", item_type);
    closeMenu();
  };

  const handleAddToAlbum = () => {
    console.log("Adding to album item id", selectedItem.id);
    closeMenu();
  };

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
        <p><strong>{name}</strong> (item_type: {item_type})</p>

        {/* Show categories/tags if any */}
        {categories.length > 0 && (
          <div className="mb-3">
            <h5>Categories:</h5>
            <div className="d-flex flex-wrap">
              {categories.map((cat, idx) => (
                <div key={idx} className="tag m-1 p-1">
                  {cat.name}
                </div>
              ))}
            </div>
          </div>
        )}

        {tags.length > 0 && (
          <div className="mb-3">
            <h5>Tags:</h5>
            <div className="d-flex flex-wrap">
              {tags.map((tag, idx) => (
                <div key={idx} className="tag m-1 p-1">
                  {tag.name}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Example actions */}
        <div className="mb-2">
          {canAddToAlbum && (
            <p
              className="text_over_image_tile mb-2"
              style={{ cursor: "pointer" }}
              onClick={handleAddToAlbum}
            >
              <i className="fas fa-plus pe-2"></i> Add to album
            </p>
          )}
          {canDelete && (
            <p
              className="text_over_image_tile mb-2 text-danger"
              style={{ cursor: "pointer" }}
              onClick={handleDelete}
            >
              <i className="fas fa-trash pe-2"></i> Delete
            </p>
          )}
        </div>
      </Offcanvas.Body>
    </Offcanvas>
  );
}
