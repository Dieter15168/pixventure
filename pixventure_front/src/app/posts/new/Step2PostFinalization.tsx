// src/app/new-post/Step2PostFinalization.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Tile, { TileProps } from "@/components/Tile/Tile";
import { MinimalMediaItemDTO } from "./AvailableMedia";
import { usePostsAPI } from "@/utils/api/posts";
import { useTermsAPI, Term } from "@/utils/api/terms";
import SharedMasonry from "@/components/common/SharedMasonry";
import NavigationBar, {
  NavigationButton,
} from "@/components/NavigationBar/NavigationBar";

interface Step2Props {
  selectedItems: MinimalMediaItemDTO[];
  onBack: () => void;
}

/**
 * Step 2: Finalize the post details.
 *  - Allows the user to set the post name, featured item, and select terms.
 *  - Uses a NavigationBar for uniform navigation.
 */
export default function Step2PostFinalization({
  selectedItems,
  onBack,
}: Step2Props) {
  const router = useRouter();
  const { createPost } = usePostsAPI();
  const { fetchAllTerms } = useTermsAPI();

  // Basic post information.
  const [postName, setPostName] = useState("");
  const [featuredId, setFeaturedId] = useState<number | null>(null);

  // Terms data.
  const [allCategories, setAllCategories] = useState<Term[]>([]);
  const [allTags, setAllTags] = useState<Term[]>([]);

  // Selected term IDs.
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);

  useEffect(() => {
    if (selectedItems.length === 0) {
      alert("No items selected. Going back.");
      onBack();
      return;
    }
    setFeaturedId(selectedItems[0].id);
    loadTerms();
  }, [selectedItems, onBack]);

  async function loadTerms() {
    try {
      const data = await fetchAllTerms(); // Expected to return { categories: Term[], tags: Term[] }
      setAllCategories(data.categories);
      setAllTags(data.tags);
    } catch (err) {
      console.error("Failed to load terms:", err);
    }
  }

  function toggleCategory(catId: number) {
    setSelectedCategoryIds((prev) =>
      prev.includes(catId) ? prev.filter((x) => x !== catId) : [...prev, catId]
    );
  }

  function toggleTag(tagId: number) {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((x) => x !== tagId) : [...prev, tagId]
    );
  }

  async function handlePublish() {
    if (!postName) {
      alert("Please enter a post name.");
      return;
    }
    if (!featuredId) {
      alert("Please pick a featured item.");
      return;
    }
    try {
      // Merge category and tag IDs into a single terms array.
      const combinedTermIds = [...selectedCategoryIds, ...selectedTagIds];
      const payload = {
        name: postName,
        items: selectedItems.map((it) => it.id),
        featured_item: featuredId,
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

  // Define NavigationBar button groups.
  const leftButtons: NavigationButton[] = [
    { label: "Back", onClick: onBack, variant: "secondary" },
  ];
  const rightButtons: NavigationButton[] = [
    { label: "Publish Post", onClick: handlePublish, variant: "success" },
  ];

  return (
    <div>
      <h2>Finalize Your Post (Step 2)</h2>
      <NavigationBar
        leftButtons={leftButtons}
        rightButtons={rightButtons}
      />

      <div className="mb-3">
        <label>
          <strong>Post Name:</strong>
          <input
            type="text"
            className="form-control"
            value={postName}
            onChange={(e) => setPostName(e.target.value)}
          />
        </label>
      </div>

      <h4>Chosen Media Items</h4>
      <p>Click a tile to mark it as the featured item.</p>
      <SharedMasonry>
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
            locked: false,
            status: item.status,
            tile_size: "medium",
            canAddToAlbum: false,
            entity_type: "media",
            page_type: "post_creation",
            selectMode: "radio",
            selected: isFeatured,
            onSelectChange: (id, newVal) => {
              if (newVal) {
                setFeaturedId(id);
              }
            },
          };
          return (
            <Tile
              key={item.id}
              item={tileProps}
            />
          );
        })}
      </SharedMasonry>

      <hr />

      <h4>Select Categories</h4>
      <div>
        {allCategories.map((cat) => {
          const isSelected = selectedCategoryIds.includes(cat.id);
          return (
            <label
              key={cat.id}
              style={{
                border: isSelected ? "1px solid blue" : "1px solid #ccc",
                borderRadius: 4,
                padding: "4px 8px",
                backgroundColor: isSelected ? "hotpink" : "black",
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
      <div>
        {allTags.map((tg) => {
          const isSelected = selectedTagIds.includes(tg.id);
          return (
            <label
              key={tg.id}
              style={{
                border: isSelected ? "1px solid green" : "1px solid #ccc",
                borderRadius: 4,
                padding: "4px 8px",
                backgroundColor: isSelected ? "hotpink" : "black",
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
    </div>
  );
}
