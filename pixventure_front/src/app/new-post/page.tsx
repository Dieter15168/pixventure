// src/app/new-post/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useMediaAPI } from "../../utils/api/media";
import AvailableMedia, { MinimalMediaItemDTO } from "./AvailableMedia";

export default function NewPostPage() {
  const { fetchAvailableMedia, uploadFile } = useMediaAPI();

  const [mediaItems, setMediaItems] = useState<MinimalMediaItemDTO[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);

  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [errors, setErrors] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);

  // 1. Fetch "available" items on mount
  useEffect(() => {
    fetchAllMedia();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  // 2. Upload each file, then either re-fetch or directly insert into local state
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
        // Attempt to upload the file, which returns data from the backend
        // e.g. { media_item_id: number, thumbnail_url: string, ... }
        const uploadResponse = await uploadFile(file);

        // We can either do a full re-fetch after all uploads
        // or directly parse `uploadResponse` into a MinimalMediaItemDTO
        // and push it to local state. For simplicity, let's re-fetch afterwards.
        setUploadedCount((prev) => prev + 1);
      } catch (err: any) {
        console.error("Upload failed:", err);

        // 3. Make use of error details from the backend if present
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

    // 4. Re-fetch to see new items (only if no errors, or do it anyway)
    // This ensures newly uploaded items appear immediately
    fetchAllMedia();
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h1>Create a New Post</h1>
      <p>Select multiple files to upload.</p>

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

      {/* Show errors if any */}
      {errors.length > 0 && (
        <div style={{ color: "red" }}>
          <h3>Errors:</h3>
          <ul>
            {errors.map((err, idx) => (
              <li key={idx}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {/* If everything was successful */}
      {!uploading &&
        totalFiles > 0 &&
        uploadedCount === totalFiles &&
        errors.length === 0 && (
          <p style={{ color: "green" }}>All files uploaded successfully!</p>
        )}

      <AvailableMedia mediaItems={mediaItems} loading={loadingMedia} />
    </div>
  );
}
