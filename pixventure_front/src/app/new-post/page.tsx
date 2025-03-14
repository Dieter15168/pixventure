// src/app/new-post/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../utils/api/media";
import ErrorModal from "../../components/ErrorModal";
import DragDropZone from "./DragDropZone";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";
import Step2PostFinalization from "./Step2PostFinalization";

/**
 * The main multi-step page for creating a new post.
 * Step 1: pick media items
 * Step 2: finalize & publish
 */
export default function NewPostPage() {
  // Which step are we on? 1 or 2
  const [step, setStep] = useState(1);

  // Global states needed for step 1
  const { fetchAvailableMedia, uploadFile } = useMediaAPI();
  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);

  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [uploading, setUploading] = useState(false);

  // Errors & modal
  const [errors, setErrors] = useState<string[]>([]);
  const [showErrorModal, setShowErrorModal] = useState(false);

  // The set of IDs the user selected in step 1
  const [selectedMediaIds, setSelectedMediaIds] = useState<number[]>([]);

  // ----------------------------------------
  // Step 1 logic
  // ----------------------------------------
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

  // Called by the DragDropZone to handle user selecting or dropping new files
  function handleFiles(files: FileList) {
    // We reuse handleFileChange logic by constructing a synthetic event
    const syntheticEvent = {
      target: { files } as Partial<HTMLInputElement>,
    } as React.ChangeEvent<HTMLInputElement>;

    handleFileChange(syntheticEvent);
  }

  // The existing upload logic
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const filesArray = Array.from(e.target.files);
    setTotalFiles(filesArray.length);
    setUploadedCount(0);

    let newErrors: string[] = [];
    setUploading(true);

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

    // Refresh after uploading
    fetchAllMedia();
  };

  function handleCloseModal() {
    setShowErrorModal(false);
  }

  // Toggling selection of an item in Step 1
  function handleTileSelectChange(tileId: number, isSelected: boolean) {
    setSelectedMediaIds((prev) => {
      if (isSelected) return [...prev, tileId];
      return prev.filter((id) => id !== tileId);
    });
  }

  // Step 1 "Next" click
  function goToStep2() {
    if (selectedMediaIds.length === 0) {
      alert("Please select at least one media item before proceeding.");
      return;
    }
    setStep(2);
  }

  // ----------------------------------------
  // Render: if step=1, we show Step1 UI
  // if step=2, we show Step2PostFinalization
  // ----------------------------------------
  return (
    <div>
      {step === 1 && (
        <>
          <h1>Create a New Post (Step 1)</h1>
          <p>
            Upload new files or select from existing media. Then press "Next".
          </p>

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

          <ErrorModal
            show={showErrorModal && errors.length > 0}
            errors={errors}
            onClose={handleCloseModal}
          />

          <AvailableMedia
            mediaItems={mediaItems}
            loading={loadingMedia}
            selectedMediaIds={selectedMediaIds}
            onSelectChange={handleTileSelectChange}
          />

          <button
            type="button"
            className="btn btn-primary mt-3"
            onClick={goToStep2}
          >
            Next
          </button>
        </>
      )}

      {step === 2 && (
        <Step2PostFinalization
          selectedMediaIds={selectedMediaIds}
          onBack={() => setStep(1)}
        />
      )}
    </div>
  );
}
