// src/app/new-post/Step1MediaSelection.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../../utils/api/media";
import DragDropZone from "./DragDropZone";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";

interface Step1MediaSelectionProps {
  onNextStep: (selectedItems: MinimalMediaItemDTO[]) => void;
  errors: string[];
  setErrors: React.Dispatch<React.SetStateAction<string[]>>;
  showErrorModal: boolean;
  setShowErrorModal: React.Dispatch<React.SetStateAction<boolean>>;
}

/**
 * Step 1 of post creation: 
 *  - fetch existing media
 *  - let user upload new media
 *  - user picks which items to use for this post
 */
export default function Step1MediaSelection({
  onNextStep,
  errors,
  setErrors,
  showErrorModal,
  setShowErrorModal,
}: Step1MediaSelectionProps) {
  const { fetchAvailableMedia, uploadFile } = useMediaAPI();

  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);

  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [uploading, setUploading] = useState(false);

  // The user’s selected item IDs
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  useEffect(() => {
    loadMediaItems();
  }, []);

  async function loadMediaItems() {
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

  // Called by DragDropZone
  function handleFiles(files: FileList) {
    const syntheticEvent = {
      target: { files } as Partial<HTMLInputElement>,
    } as React.ChangeEvent<HTMLInputElement>;

    handleFileChange(syntheticEvent);
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const filesArray = Array.from(e.target.files);

    setTotalFiles(filesArray.length);
    setUploadedCount(0);
    setErrors([]);

    setUploading(true);
    let newErrors: string[] = [];

    for (const file of filesArray) {
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
        newErrors.push(errorMsg);
      }
    }

    setUploading(false);
    setErrors(newErrors);
    if (newErrors.length > 0) {
      setShowErrorModal(true);
    }

    // Reload after uploads
    loadMediaItems();
  };

  // Called by <AvailableMedia> to toggle selection
  function handleTileSelectChange(tileId: number, isSelected: boolean) {
    setSelectedIds((prev) => {
      if (isSelected) return [...prev, tileId];
      return prev.filter((x) => x !== tileId);
    });
  }

  // Press Next Step => pass actual items to parent
  function handleNext() {
    // we have selectedIds. We want the actual item objects.
    const finalSelectedItems = mediaItems.filter((m) => selectedIds.includes(m.id));
    onNextStep(finalSelectedItems);
  }

  return (
    <div>
      <h2>Step 1: Pick Items</h2>
      <DragDropZone onFilesSelected={handleFiles} uploading={uploading} />

      {uploading && (
        <p>
          Uploading... {uploadedCount}/{totalFiles}
        </p>
      )}

      {!uploading && totalFiles > 0 && uploadedCount === totalFiles && errors.length === 0 && (
        <p style={{ color: "green" }}>All files uploaded successfully!</p>
      )}

      <AvailableMedia
        mediaItems={mediaItems}
        loading={loadingMedia}
        selectedMediaIds={selectedIds}
        onSelectChange={handleTileSelectChange}
      />

      <button type="button" className="btn btn-primary mt-3" onClick={handleNext}>
        Next
      </button>
    </div>
  );
}
