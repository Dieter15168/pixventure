// src/app/new-post/Step1MediaSelection.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../../utils/api/media";
import DragDropZone from "./DragDropZone";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";
import NavigationBar, {
  NavigationButton,
} from "@/components/NavigationBar/NavigationBar";

interface Step1MediaSelectionProps {
  onNextStep: (selectedItems: MinimalMediaItemDTO[]) => void;
  errors: string[];
  setErrors: React.Dispatch<React.SetStateAction<string[]>>;
  showErrorModal: boolean;
  setShowErrorModal: React.Dispatch<React.SetStateAction<boolean>>;
}

/**
 * Step 1: User picks media items.
 *  - Fetches available media.
 *  - Allows file uploads.
 *  - Lets user select items with added "Check All" and "Uncheck All" options.
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
  // Selected media item IDs.
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

  // Handle file uploads via DragDropZone.
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
    // Reload media items after uploads.
    loadMediaItems();
  };

  // Toggle selection for an individual tile.
  function handleTileSelectChange(tileId: number, isSelected: boolean) {
    setSelectedIds((prev) => {
      if (isSelected) return [...prev, tileId];
      return prev.filter((x) => x !== tileId);
    });
  }

  // Select all available media.
  function handleCheckAll() {
    const allIds = mediaItems.map((item) => item.id);
    setSelectedIds(allIds);
  }

  // Unselect all media.
  function handleUncheckAll() {
    setSelectedIds([]);
  }

  // Handle navigation to the next step.
  function handleNext() {
    const finalSelectedItems = mediaItems.filter((m) =>
      selectedIds.includes(m.id)
    );
    if (finalSelectedItems.length === 0) {
      alert("Please select at least one media item!");
      return;
    }
    onNextStep(finalSelectedItems);
  }

  // Define button groups for NavigationBar.
  const leftButtons: NavigationButton[] = [
    { label: "Check All", onClick: handleCheckAll, variant: "secondary" },
    { label: "Uncheck All", onClick: handleUncheckAll, variant: "secondary" },
  ];
  const rightButtons: NavigationButton[] = [
    { label: "Next", onClick: handleNext, variant: "primary" },
  ];

  return (
    <div>
      <h2>Step 1: Pick Items</h2>
      <NavigationBar
        leftButtons={leftButtons}
        rightButtons={rightButtons}
      />

      <DragDropZone
        onFilesSelected={handleFiles}
        uploading={uploading}
      />

      {uploading && (
        <p>
          Uploading... {uploadedCount}/{totalFiles}
        </p>
      )}

      {!uploading &&
        totalFiles > 0 &&
        uploadedCount === totalFiles &&
        errors.length === 0 && (
          <p style={{ color: "green" }}>All files uploaded successfully!</p>
        )}

      <AvailableMedia
        mediaItems={mediaItems}
        loading={loadingMedia}
        selectedMediaIds={selectedIds}
        onSelectChange={handleTileSelectChange}
      />
    </div>
  );
}
