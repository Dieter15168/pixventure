// src/app/albums/new/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAlbumsAPI } from "../../../utils/api/albums";

export default function CreateAlbumPage() {
  const [name, setName] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [showCreator, setShowCreator] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { createAlbum } = useAlbumsAPI();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    try {
      const album = await createAlbum({ 
        name, 
        is_public: isPublic, 
        show_creator_to_others: isPublic ? showCreator : false 
      });
      router.push(`/my/`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to create album.");
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "1rem" }}>
      <h1>Create a New Album</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="albumName" style={{ display: "block", marginBottom: "0.5rem" }}>
            Album Name:
          </label>
          <input
            id="albumName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Album Visibility:</label>
          <div>
            <label>
              <input
                type="radio"
                name="visibility"
                value="private"
                checked={!isPublic}
                onChange={() => setIsPublic(false)}
              />
              Private
            </label>
          </div>
          <div>
            <label>
              <input
                type="radio"
                name="visibility"
                value="public"
                checked={isPublic}
                onChange={() => setIsPublic(true)}
              />
              Public (will be moderated)
            </label>
          </div>
        </div>
        {isPublic && (
          <div style={{ marginBottom: "1rem" }}>
            <label>
              <input
                type="checkbox"
                checked={showCreator}
                onChange={(e) => setShowCreator(e.target.checked)}
              />
              Show my name to other users
            </label>
          </div>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Create Album
        </button>
      </form>
    </div>
  );
}
