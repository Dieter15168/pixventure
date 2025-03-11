// src/app/new-post/page.tsx
"use client";

import React, { useState } from "react";
import { useMediaAPI } from "../../utils/api/media";

/**
 * A minimal /new-post page with a file input for multiple files. 
 * Each file is uploaded to /api/media/new/ using our custom Axios logic.
 */
export default function NewPostPage() {
  const { uploadFile } = useMediaAPI();

  const [uploadedCount, setUploadedCount] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [errors, setErrors] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);

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
        // Attempt to upload the file
        await uploadFile(file);
        setUploadedCount((prev) => prev + 1);
      } catch (err: any) {
        console.error("Upload failed:", err);
        setErrors((prev) => [...prev, `Error uploading ${file.name}: ${err.message || err}`]);
      }
    }

    setUploading(false);
    // Optionally, refresh or fetch "unused" media items here
  };

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
      {!uploading && totalFiles > 0 && uploadedCount === totalFiles && errors.length === 0 && (
        <p style={{ color: "green" }}>
          All files uploaded successfully!
        </p>
      )}
    </div>
  );
}
