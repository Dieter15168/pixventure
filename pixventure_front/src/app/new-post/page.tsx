// src/app/new-post/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../utils/api/media";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";
import ErrorModal from "../../components/ErrorModal";

export default function NewPostPage() {
  const { fetchAvailableMedia, uploadFile } = useMediaAPI();

  // 1) State for the media items from backend
  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);

  // 2) State for which items are selected
  const [selectedMediaIds, setSelectedMediaIds] = useState<number[]>([]);

  // --- (unchanged) error handling, uploading states, etc. ---
  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [showErrorModal, setShowErrorModal] = useState(false);

  useEffect(() => {
    fetchAllMedia();
  }, []);

  async function fetchAllMedia() {
    setLoadingMedia(true);
    try {
      const data = await fetchAvailableMedia();
      setMediaItems(data);
    } catch (error) {
      console.error("Failed to fetch available media:", error);
    } finally {
      setLoadingMedia(false);
    }
  }

  // 3) Helper to toggle an item in selectedMediaIds
  function handleTileSelectChange(tileId: number, isSelected: boolean) {
    setSelectedMediaIds((prev) => {
      if (isSelected) {
        // add this ID if not present
        return [...prev, tileId];
      } else {
        // remove this ID
        return prev.filter((id) => id !== tileId);
      }
    });
  }

  // 4) The existing upload logic is unchanged
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const filesArray = Array.from(e.target.files);
    setTotalFiles(filesArray.length);
    setUploadedCount(0);
    setErrors([]);
    setUploading(true);

    for (let i = 0; i < filesArray.length; i++) {
      const file = filesArray[i];
      try {
        await uploadFile(file);
        setUploadedCount((prev) => prev + 1);
      } catch (err: any) {
        console.error("Upload failed:", err);

        let errorMsg = `Error uploading ${file.name}: `;
        if (err.response?.data?.detail) {
          errorMsg += err.response.data.detail;
        } else if (err.message) {
          errorMsg += err.message;
        } else {
          errorMsg += String(err);
        }
        setErrors((prev) => [...prev, errorMsg]);
      }
    }

    setUploading(false);
    if (errors.length > 0) {
      setShowErrorModal(true);
    }

    fetchAllMedia();
  };

  function handleCloseModal() {
    setShowErrorModal(false);
  }

  // 5) We pass selectedMediaIds and handleTileSelectChange down to AvailableMedia
  return (
    <div>
      <h1>Create a New Post</h1>
      <p>Select multiple files to upload.</p>

      {/* The file input. We allow multiple selection. */}
      <input
        type="file"
        multiple
        onChange={handleFileChange}
      />

      {/* Show upload progress */}
      {uploading && (
        <p>
          Uploading... {uploadedCount}/{totalFiles}
        </p>
      )}

      {/* If everything was successful */}
      {!uploading &&
        totalFiles > 0 &&
        uploadedCount === totalFiles &&
        errors.length === 0 && <p>All files uploaded successfully!</p>}

      {/* Show or hide the error modal */}
      <ErrorModal
        show={showErrorModal && errors.length > 0}
        errors={errors}
        onClose={handleCloseModal}
      />

      {/* Pass selectedMediaIds + callback */}
      <AvailableMedia
        mediaItems={mediaItems}
        loading={loadingMedia}
        selectedMediaIds={selectedMediaIds}
        onSelectChange={handleTileSelectChange}
      />
    </div>
  );
}
