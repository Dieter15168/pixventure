"use client";

import React, { useEffect, useState } from "react";
import {
  useModerationAPI,
  ModerationDashboardData,
} from "../../utils/api/moderation";
import ModerationRejectModal from "../../components/ModerationRejectModal";
import Tile, { TileProps } from "../../components/Tile/Tile";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/free-solid-svg-icons";
import { useNotification } from "../../contexts/NotificationContext";

/**
 * Returns style modifications based on the moderation status.
 *
 * @param {string | undefined} status - The moderation status of the element.
 * @returns {React.CSSProperties} - The style modifications for the element.
 */
function getStatusStyle(status?: string): React.CSSProperties {
  // If status is undefined or empty, return no additional style.
  if (!status) return {};

  switch (status.toLowerCase()) {
    case "approved":
      return { borderLeft: "4px solid green", backgroundColor: "#e6ffe6" };
    case "rejected":
      return { borderLeft: "4px solid red", backgroundColor: "#ffe6e6" };
    default:
      return {};
  }
}

/**
 * ModerationDashboard Component
 *
 * This component displays posts and orphan media items pending moderation.
 * It allows the moderator to approve or reject items. After an action is performed,
 * the element is visually marked as processed using the updated local state.
 *
 * Best practices followed:
 * - Separation of concerns with helper functions.
 * - Well-documented code for maintainability.
 * - Modular design to facilitate extendability.
 */
export default function ModerationDashboard() {
  const { fetchDashboard, performModerationAction } = useModerationAPI();
  const { addNotification } = useNotification();
  const [data, setData] = useState<ModerationDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [currentEntity, setCurrentEntity] = useState<{
    type: "post" | "media";
    id: number;
  } | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const dashboardData = await fetchDashboard();
        setData(dashboardData);
      } catch (err: any) {
        setError(err.message || "Failed to load moderation data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [fetchDashboard]);

  /**
   * Updates the local moderation status for a given entity.
   *
   * @param {"post" | "media"} entityType - The type of the moderated entity.
   * @param {number} entityId - The ID of the moderated entity.
   * @param {string} newStatus - The new moderation status ("Approved" or "Rejected").
   */
  function updateModerationStatus(
    entityType: "post" | "media",
    entityId: number,
    newStatus: string
  ) {
    setData((prevData) => {
      if (!prevData) return prevData;
      if (entityType === "post") {
        const updatedPosts = prevData.posts.map((post) =>
          post.id === entityId ? { ...post, status_display: newStatus } : post
        );
        return { ...prevData, posts: updatedPosts };
      } else if (entityType === "media") {
        const updatedMedia = prevData.orphan_media.map((media) =>
          media.id === entityId
            ? { ...media, status_display: newStatus }
            : media
        );
        return { ...prevData, orphan_media: updatedMedia };
      }
      return prevData;
    });
  }

  /**
   * Handles the approval action for a given entity.
   *
   * @param {"post" | "media"} entityType - The type of the entity.
   * @param {number} entityId - The ID of the entity.
   */
  function handleApprove(entityType: "post" | "media", entityId: number) {
    performModerationAction({
      entity_type: entityType,
      entity_id: entityId,
      action: "approve",
    })
      .then((resData) => {
        addNotification("Content approved successfully", "success");
        console.log("Approved", resData);
        // Update the local status to "Approved"
        updateModerationStatus(entityType, entityId, "Approved");
      })
      .catch((err) => {
        console.error("Approval error", err);
        addNotification("Failed to approve content", "error");
      });
  }

  /**
   * Opens the rejection modal for a given entity.
   *
   * @param {"post" | "media"} entityType - The type of the entity.
   * @param {number} entityId - The ID of the entity.
   */
  function openRejectModal(entityType: "post" | "media", entityId: number) {
    setCurrentEntity({ type: entityType, id: entityId });
    setRejectModalOpen(true);
  }

  /**
   * Handles the submission of a rejection action with reasons and a comment.
   *
   * @param {number[]} reasonIds - Array of selected rejection reason IDs.
   * @param {string} comment - Additional comment provided by the moderator.
   */
  function handleRejectSubmit(reasonIds: number[], comment: string) {
    if (!currentEntity) return;
    performModerationAction({
      entity_type: currentEntity.type,
      entity_id: currentEntity.id,
      action: "reject",
      rejection_reason: reasonIds,
      comment,
    })
      .then((resData) => {
        addNotification("Content rejected successfully", "success");
        console.log("Rejected", resData);
        setRejectModalOpen(false);
        // Update the local status to "Rejected"
        updateModerationStatus(
          currentEntity.type,
          currentEntity.id,
          "Rejected"
        );
      })
      .catch((err) => {
        console.error("Rejection error", err);
        addNotification("Failed to reject content", "error");
      });
  }

  if (loading) return <div>Loading moderation dashboard...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Moderation Dashboard</h1>

      {/* Moderated Posts Section */}
      <section style={{ marginBottom: "2rem" }}>
        <h2>Posts Pending Moderation</h2>
        {data?.posts && data.posts.length > 0 ? (
          data.posts.map((post) => (
            <div
              key={post.id}
              style={{
                border: "1px solid #ccc",
                marginBottom: "1rem",
                padding: "1rem",
                ...getStatusStyle(post.status_display),
              }}
            >
              <h3>
                {post.name} (Status: {post.status_display || "Pending"})
              </h3>
              <p>Slug: {post.slug}</p>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {post.media_items.map((item: any) => {
                  const tileProps: TileProps = {
                    id: item.id,
                    name: item.original_filename || `Media #${item.id}`,
                    thumbnail_url: item.thumbnail_url,
                    media_type: "photo", // Adjust if needed
                    show_likes: false,
                    likes_counter: 0,
                    has_liked: false,
                    owner_username: "",
                    locked: false,
                    status: item.status_display,
                    tile_size: "small",
                    canAddToAlbum: false,
                    entity_type: "media",
                    page_type: "posts_list",
                  };
                  return (
                    <Tile
                      key={item.id}
                      item={tileProps}
                    />
                  );
                })}
              </div>
              <div style={{ marginTop: "0.5rem" }}>
                <button
                  className="btn btn-success btn-sm me-2"
                  onClick={() => handleApprove("post", post.id)}
                >
                  <FontAwesomeIcon icon={faCheck} /> Approve
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => openRejectModal("post", post.id)}
                >
                  <FontAwesomeIcon icon={faTimes} /> Reject
                </button>
              </div>
            </div>
          ))
        ) : (
          <p>No posts pending moderation.</p>
        )}
      </section>

      {/* Orphan Media Section */}
      <section>
        <h2>Orphan Media Pending Moderation</h2>
        {data?.orphan_media && data.orphan_media.length > 0 ? (
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {data.orphan_media.map((item) => {
              const tileProps: TileProps = {
                id: item.id,
                name: item.original_filename || `Media #${item.id}`,
                thumbnail_url: item.thumbnail_url,
                media_type: "photo",
                show_likes: false,
                likes_counter: 0,
                has_liked: false,
                owner_username: "",
                locked: false,
                status: item.status_display,
                tile_size: "small",
                canAddToAlbum: false,
                entity_type: "media",
                page_type: "posts_list",
              };
              return (
                <div
                  key={item.id}
                  style={{
                    position: "relative",
                    ...getStatusStyle(item.status_display),
                  }}
                >
                  <Tile item={tileProps} />
                  <div style={{ marginTop: "0.5rem" }}>
                    <button
                      className="btn btn-success btn-sm me-2"
                      onClick={() => handleApprove("media", item.id)}
                    >
                      <FontAwesomeIcon icon={faCheck} /> Approve
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => openRejectModal("media", item.id)}
                    >
                      <FontAwesomeIcon icon={faTimes} /> Reject
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p>No orphan media items pending moderation.</p>
        )}
      </section>

      <ModerationRejectModal
        show={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        onSubmit={handleRejectSubmit}
      />
    </div>
  );
}
