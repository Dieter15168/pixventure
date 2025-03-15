// src/app/new-post/DragDropZone.tsx
"use client";

import React, { useRef, useState } from "react";

interface DragDropZoneProps {
  onFilesSelected: (files: FileList) => void;
  uploading: boolean;
}

export default function DragDropZone({ onFilesSelected, uploading }: DragDropZoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Trigger the hidden input’s file picker on click
  function handleClick() {
    if (!uploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }

  // Fired when the user chooses files via the browser dialog
  function handleFileInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files || e.target.files.length === 0) return;
    onFilesSelected(e.target.files);
    e.target.value = ""; // reset so user can pick the same file if desired
  }

  // Basic drag over / drag enter / drag leave / drop events
  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (!uploading) {
      setIsDragging(true);
    }
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (uploading) return;

    // The dropped files
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFilesSelected(files);
    }
  }

  return (
    <div
      style={{
        border: "2px dashed #aaa",
        borderRadius: 8,
        padding: "2rem",
        textAlign: "center",
        position: "relative",
        cursor: uploading ? "default" : "pointer",
        backgroundColor: isDragging ? "#f0f0f0" : "transparent",
        transition: "background-color 0.2s ease",
      }}
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragEnter={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <p style={{ margin: 0 }}>
        {uploading
          ? "Uploading in progress..."
          : "Drag & drop files here, or click to select from dialog"}
      </p>

      {/* The hidden input for file-browsing fallback */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: "none" }}
        onChange={handleFileInputChange}
      />
    </div>
  );
}
