"use client";

import React, { useEffect, useState } from "react";
import { Tabs, Tab, Badge } from "react-bootstrap";
import {
  useModerationAPI,
  ModerationDashboardData,
} from "../../utils/api/moderation";
import ModerationRejectModal from "../../components/ModerationRejectModal";
import ModerationMediaTile from "../../components/ModerationMediaTile";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/free-solid-svg-icons";
import { useNotification } from "../../contexts/NotificationContext";
import { getStatusStyle } from "../../utils/moderationHelpers";

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
  // Default active tab key: "posts" or "orphan"
  const [activeKey, setActiveKey] = useState("posts");

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
   * Updates the moderation status for the given entity (post or media).
   * For posts, we update "status_display" and for media items we update "status".
   *
   * @param {"post" | "media"} entityType - The type of the entity.
   * @param {number} entityId - The ID of the entity.
   * @param {string} newStatus - The new status ("Approved" or "Rejected").
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
        // For media items, update the "status" property
        const updateMediaItems = (items: any[]) =>
          items.map((media: any) =>
            media.id === entityId ? { ...media, status: newStatus } : media
          );
        return {
          ...prevData,
          posts: prevData.posts.map((post) => ({
            ...post,
            media_items: updateMediaItems(post.media_items),
          })),
          orphan_media: updateMediaItems(prevData.orphan_media),
        };
      }
      return prevData;
    });
  }

  /**
   * Handles approval of the specified entity.
   */
  function handleApprove(entityType: "post" | "media", entityId: number) {
    performModerationAction({
      entity_type: entityType,
      entity_id: entityId,
      action: "approve",
    })
      .then((resData) => {
        addNotification("Content approved successfully", "success");
        updateModerationStatus(entityType, entityId, "Approved");
      })
      .catch((err) => {
        console.error("Approval error", err);
        addNotification("Failed to approve content", "error");
      });
  }

  /**
   * Opens the rejection modal for the specified entity.
   */
  function openRejectModal(entityType: "post" | "media", entityId: number) {
    setCurrentEntity({ type: entityType, id: entityId });
    setRejectModalOpen(true);
  }

  /**
   * Handles the submission of the rejection action.
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
        setRejectModalOpen(false);
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
      <Tabs
        activeKey={activeKey}
        onSelect={(k) => setActiveKey(k || "posts")}
        className="mb-3"
      >
        {/* Posts Moderation Tab */}
        <Tab
          eventKey="posts"
          title={
            <span>
              Posts Moderation{" "}
              <Badge bg="secondary">
                {data?.posts ? data.posts.length : 0}
              </Badge>
            </span>
          }
        >
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
                  {post.name} (Status:{" "}
                  {post.status_display || "Pending moderation"})
                </h3>
                <p>Slug: {post.slug}</p>
                {/* Post-level moderation controls */}
                <div style={{ marginBottom: "1rem" }}>
                  <button
                    className="btn btn-success btn-sm me-2"
                    onClick={() => handleApprove("post", post.id)}
                  >
                    <FontAwesomeIcon icon={faCheck} /> Approve Post
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => openRejectModal("post", post.id)}
                  >
                    <FontAwesomeIcon icon={faTimes} /> Reject Post
                  </button>
                </div>
                {/* Divider and media items section */}
                <hr style={{ margin: "1rem 0" }} />
                <h4>Media Items Moderation</h4>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  {post.media_items.map((item: any) => {
                    const tileProps = {
                      id: item.id,
                      name: item.original_filename || `Media #${item.id}`,
                      thumbnail_url: item.thumbnail_url,
                      media_type: "photo",
                      show_likes: false,
                      likes_counter: 0,
                      has_liked: false,
                      owner_username: "",
                      locked: false,
                      status: item.status,
                      tile_size: "small",
                      canAddToAlbum: false,
                      entity_type: "media",
                      page_type: "posts_list",
                    };
                    return (
                      <ModerationMediaTile
                        key={item.id}
                        item={tileProps}
                        onApprove={() => handleApprove("media", item.id)}
                        onReject={() => openRejectModal("media", item.id)}
                      />
                    );
                  })}
                </div>
              </div>
            ))
          ) : (
            <p>No posts pending moderation.</p>
          )}
        </Tab>

        {/* Orphan Media Moderation Tab */}
        <Tab
          eventKey="orphan"
          title={
            <span>
              Orphan Media Moderation{" "}
              <Badge bg="secondary">
                {data?.orphan_media ? data.orphan_media.length : 0}
              </Badge>
            </span>
          }
        >
          {data?.orphan_media && data.orphan_media.length > 0 ? (
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {data.orphan_media.map((item) => {
                const tileProps = {
                  id: item.id,
                  name: item.original_filename || `Media #${item.id}`,
                  thumbnail_url: item.thumbnail_url,
                  media_type: "photo",
                  show_likes: false,
                  likes_counter: 0,
                  has_liked: false,
                  owner_username: "",
                  locked: false,
                  status: item.status,
                  tile_size: "small",
                  canAddToAlbum: false,
                  entity_type: "media",
                  page_type: "posts_list",
                };
                return (
                  <ModerationMediaTile
                    key={item.id}
                    item={tileProps}
                    onApprove={() => handleApprove("media", item.id)}
                    onReject={() => openRejectModal("media", item.id)}
                  />
                );
              })}
            </div>
          ) : (
            <p>No orphan media items pending moderation.</p>
          )}
        </Tab>
      </Tabs>

      <ModerationRejectModal
        show={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        onSubmit={handleRejectSubmit}
      />
    </div>
  );
}
