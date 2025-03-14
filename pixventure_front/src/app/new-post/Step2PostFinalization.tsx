"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Tile, { TileProps } from "../../components/Tile/Tile";
import { MinimalMediaItemDTO } from "./AvailableMedia";
import { usePostsAPI } from "../../utils/api/posts";
import { useTermsAPI, Term } from "../../utils/api/terms";

interface Step2Props {
  selectedItems: MinimalMediaItemDTO[]; // from Step 1
  onBack: () => void;
}

export default function Step2PostFinalization({
  selectedItems,
  onBack,
}: Step2Props) {
  const router = useRouter();
  const { createPost } = usePostsAPI();
  const { fetchAllTerms } = useTermsAPI();

  // Basic post info
  const [postName, setPostName] = useState("");
  const [featuredId, setFeaturedId] = useState<number | null>(null);

  // We store categories & tags separately
  const [allCategories, setAllCategories] = useState<Term[]>([]);
  const [allTags, setAllTags] = useState<Term[]>([]);

  // The user’s chosen categories/tags
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);

  useEffect(() => {
    if (selectedItems.length === 0) {
      alert("No items selected. Going back.");
      onBack();
      return;
    }
    setFeaturedId(selectedItems[0].id);

    loadTermsFromBackend();
  }, [selectedItems, onBack]);

  // Suppose the backend returns an object with { categories: Term[], tags: Term[] }
  async function loadTermsFromBackend() {
    try {
      const data = await fetchAllTerms(); // e.g. { categories: [Term], tags: [Term] }
      setAllCategories(data.categories);
      setAllTags(data.tags);
    } catch (err) {
      console.error("Failed to load terms:", err);
    }
  }

  // Toggle a category in selectedCategoryIds
  function toggleCategory(catId: number) {
    setSelectedCategoryIds((prev) =>
      prev.includes(catId) ? prev.filter((x) => x !== catId) : [...prev, catId]
    );
  }

  // Toggle a tag in selectedTagIds
  function toggleTag(tagId: number) {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((x) => x !== tagId) : [...prev, tagId]
    );
  }

  async function handlePublish() {
    if (!postName) {
      alert("Please provide a post name.");
      return;
    }
    if (!featuredId) {
      alert("Please pick a featured item.");
      return;
    }

    try {
      // Combine selectedCategoryIds + selectedTagIds into one array
      const combinedTermIds = [...selectedCategoryIds, ...selectedTagIds];

      const payload = {
        name: postName,
        // The IDs of the selected items from Step 1
        items: selectedItems.map((it) => it.id),
        featured_item: featuredId,
        // Single "terms" field containing both categories & tags
        terms: combinedTermIds,
      };

      const newPost = await createPost(payload);
      console.log("Created post:", newPost);
      router.push("/my-page");
    } catch (err: any) {
      console.error("Failed to create post:", err);
      alert(`Error creating post: ${err.message || err}`);
    }
  }

  return (
    <div>
      <h2>Finalize Your Post (Step 2)</h2>
      <button
        onClick={onBack}
        className="btn btn-secondary mb-3"
      >
        &laquo; Back
      </button>

      <div className="mb-3">
        <label>
          <strong>Post Name</strong>
          <input
            type="text"
            className="form-control"
            value={postName}
            onChange={(e) => setPostName(e.target.value)}
          />
        </label>
      </div>

      <h4>Chosen Media Items</h4>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {selectedItems.map((item) => {
          const isFeatured = item.id === featuredId;
          const tileProps: TileProps = {
            id: item.id,
            name: `Media #${item.id}`,
            thumbnail_url: item.thumbnail_url,
            media_type: item.media_type,
            show_likes: false,
            likes_counter: 0,
            has_liked: false,
            owner_username: "",
            lock_logo: false,
            status: item.status,
            tile_size: "small",
            canAddToAlbum: false,
            entity_type: "media",
            page_type: "post_creation",
          };

          return (
            <div
              key={item.id}
              style={{
                border: isFeatured ? "3px solid green" : "1px solid #ddd",
              }}
            >
              <Tile item={tileProps} />
              <button
                className="btn btn-sm btn-link"
                onClick={() => setFeaturedId(item.id)}
              >
                {isFeatured ? "Featured (Selected)" : "Set as Featured"}
              </button>
            </div>
          );
        })}
      </div>

      <hr />

      <h4>Select Categories</h4>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {allCategories.map((cat) => {
          const isSelected = selectedCategoryIds.includes(cat.id);
          return (
            <label
              key={cat.id}
              style={{
                border: isSelected ? "2px solid blue" : "1px solid #ccc",
                borderRadius: 4,
                padding: "4px 8px",
                backgroundColor: isSelected ? "#ccf" : "white",
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                style={{ display: "none" }}
                checked={isSelected}
                onChange={() => toggleCategory(cat.id)}
              />
              {cat.name}
            </label>
          );
        })}
      </div>

      <h4 className="mt-3">Select Tags</h4>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {allTags.map((tg) => {
          const isSelected = selectedTagIds.includes(tg.id);
          return (
            <label
              key={tg.id}
              style={{
                border: isSelected ? "2px solid green" : "1px solid #ccc",
                borderRadius: 4,
                padding: "4px 8px",
                backgroundColor: isSelected ? "#cfc" : "white",
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                style={{ display: "none" }}
                checked={isSelected}
                onChange={() => toggleTag(tg.id)}
              />
              {tg.name}
            </label>
          );
        })}
      </div>

      <hr />

      <button
        onClick={handlePublish}
        className="btn btn-success"
      >
        Publish Post
      </button>
    </div>
  );
}
