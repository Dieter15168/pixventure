// src/app/new-post/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../utils/api/media";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";
import ErrorModal from "../../components/ErrorModal";

export default function NewPostPage() {
  const { fetchAvailableMedia, uploadFile } = useMediaAPI();

  // Existing states
  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);
  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [uploading, setUploading] = useState(false);

  // Error-related states
  const [errors, setErrors] = useState<string[]>([]);
  const [showErrorModal, setShowErrorModal] = useState(false);

  useEffect(() => {
    fetchAllMedia();
  }, []);

  // Reusable fetch
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

  // Upload handling
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const filesArray = Array.from(e.target.files);
    setTotalFiles(filesArray.length);
    setUploadedCount(0);
    setErrors([]); // clear old errors
    setUploading(true);

    for (let i = 0; i < filesArray.length; i++) {
      const file = filesArray[i];
      try {
        const uploadResponse = await uploadFile(file);
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

    // If we got new errors, open the modal
    if (errors.length > 0) {
      setShowErrorModal(true);
    }

    // Refresh items
    fetchAllMedia();
  };

  // Closes the modal
  function handleCloseModal() {
    setShowErrorModal(false);
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h1>Create a New Post</h1>
      <p>Select multiple files to upload.</p>

      {/* The file input. We allow multiple selection. */}
      <input type="file" multiple onChange={handleFileChange} />

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
        errors.length === 0 && (
          <p style={{ color: "green" }}>All files uploaded successfully!</p>
        )}

      {/* Show or hide the error modal */}
      <ErrorModal
        show={showErrorModal && errors.length > 0}
        errors={errors}
        onClose={handleCloseModal}
      />

      {/* Display existing or newly uploaded media */}
      <AvailableMedia mediaItems={mediaItems} loading={loadingMedia} />
    </div>
  );
}
