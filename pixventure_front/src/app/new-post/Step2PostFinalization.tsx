// src/app/new-post/Step2PostFinalization.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Tile, { TileProps } from "../../components/Tile/Tile";
// This is hypothetical. We'll define or mock it.
import { usePostsAPI } from "../../utils/api/posts";

interface Step2Props {
  selectedMediaIds: number[];
  onBack: () => void;
}

/**
 * Step 2: Finalize & Publish
 */
export default function Step2PostFinalization({ selectedMediaIds, onBack }: Step2Props) {
  const router = useRouter();
  const { createPost } = usePostsAPI();

  // The fetched media items for the selected IDs
  const [selectedItems, setSelectedItems] = useState<any[]>([]);
  const [featuredId, setFeaturedId] = useState<number | null>(null);

  // The post name
  const [postName, setPostName] = useState("");

  // For categories/tags (just placeholders):
  const [allCategories, setAllCategories] = useState<any[]>([]);
  const [allTags, setAllTags] = useState<any[]>([]);
  const [selectedCatIds, setSelectedCatIds] = useState<number[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);

  useEffect(() => {
    // 1. If no items, maybe user came here by mistake
    if (selectedMediaIds.length === 0) {
      alert("No items selected. Going back.");
      onBack();
      return;
    }

    // 2. fetch or mock the item details for these IDs
    fetchSelectedMediaDetails(selectedMediaIds).then((data) => {
      setSelectedItems(data);
      if (data.length > 0) {
        setFeaturedId(data[0].id); // default to first
      }
    });

    // 3. fetch or mock categories and tags
    fetchAllTerms().then(({ categories, tags }) => {
      setAllCategories(categories);
      setAllTags(tags);
    });
  }, [selectedMediaIds, onBack]);

  function toggleCategory(catId: number) {
    setSelectedCatIds((prev) =>
      prev.includes(catId) ? prev.filter((x) => x !== catId) : [...prev, catId]
    );
  }
  function toggleTag(tagId: number) {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((x) => x !== tagId) : [...prev, tagId]
    );
  }

  // The final step: publish
  async function handlePublishPost() {
    if (!postName) {
      alert("Please enter a post name.");
      return;
    }
    if (!featuredId) {
      alert("Please pick a featured item.");
      return;
    }

    // We send the data to createPost
    try {
      const payload = {
        name: postName,
        items: selectedMediaIds,   // array of media IDs
        featured_item: featuredId,
        category_ids: selectedCatIds,
        tag_ids: selectedTagIds,
      };
      const result = await createPost(payload);
      console.log("Post created successfully:", result);
      // redirect to /my-page or wherever
      router.push("/my-page");
    } catch (err: any) {
      console.error("Failed to create post:", err);
      alert(`Error: ${err.message || err}`);
    }
  }

  return (
    <div>
      <h2>Create a New Post (Step 2)</h2>
      <p>Selected items: {selectedMediaIds.join(", ")}</p>

      <label className="d-block mb-2">
        <strong>Post Name:</strong>
        <input
          type="text"
          className="form-control"
          value={postName}
          onChange={(e) => setPostName(e.target.value)}
        />
      </label>

      <hr />

      <h5>Selected Items:</h5>
      <div style={{ display: "flex", gap: 8 }}>
        {selectedItems.map((item) => {
          const isFeatured = item.id === featuredId;
          const tileProps: TileProps = {
            id: item.id,
            name: `Media #${item.id}`,
            slug: `media-${item.id}`,
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
            page_type: "posts_list", // or "post_creation"
          };

          return (
            <div key={item.id} style={{ border: isFeatured ? "3px solid green" : "1px solid #ccc" }}>
              <Tile item={tileProps} />
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={() => setFeaturedId(item.id)}
              >
                {isFeatured ? "Featured" : "Set as Featured"}
              </button>
            </div>
          );
        })}
      </div>

      <hr />

      <h5>Pick Categories</h5>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {allCategories.map((cat) => {
          const isSelected = selectedCatIds.includes(cat.id);
          return (
            <label
              key={cat.id}
              style={{
                border: isSelected ? "2px solid blue" : "1px solid #ccc",
                padding: "4px 6px",
                borderRadius: 4,
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

      <h5>Pick Tags</h5>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {allTags.map((tag) => {
          const isSelected = selectedTagIds.includes(tag.id);
          return (
            <label
              key={tag.id}
              style={{
                border: isSelected ? "2px solid green" : "1px solid #ccc",
                padding: "4px 6px",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                style={{ display: "none" }}
                checked={isSelected}
                onChange={() => toggleTag(tag.id)}
              />
              {tag.name}
            </label>
          );
        })}
      </div>

      <hr />

      <button className="btn btn-secondary me-2" onClick={onBack}>
        Back
      </button>
      <button className="btn btn-success" onClick={handlePublishPost}>
        Publish Post
      </button>
    </div>
  );
}

// Some mocked fetch calls. Replace with real ones in your code:
async function fetchSelectedMediaDetails(ids: number[]) {
  // pretend we fetch details for each item ID
  return ids.map((id) => ({
    id,
    media_type: "photo",
    status: "Pending moderation",
    thumbnail_url: `https://fakecdn.com/thumbs/${id}.jpg`,
  }));
}

async function fetchAllTerms() {
  return {
    categories: [
      { id: 101, name: "Animals" },
      { id: 102, name: "Landscape" },
    ],
    tags: [
      { id: 201, name: "Nature" },
      { id: 202, name: "HDR" },
      { id: 203, name: "Night" },
    ],
  };
}
