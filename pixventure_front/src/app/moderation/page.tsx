"use client";

import React, { useEffect, useState } from "react";
import { Tabs, Tab, Badge } from "react-bootstrap";
import { useModerationAPI, ModerationDashboardData } from "../../utils/api/moderation";
import ModerationRejectModal from "../../components/ModerationRejectModal";
import ModerationMediaTile from "../../components/ModerationMediaTile";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/free-solid-svg-icons";
import { useNotification } from "../../contexts/NotificationContext";
import { getStatusStyle } from "../../utils/moderationHelpers";

/**
 * This component displays the main Moderation Dashboard with three tabs:
 *   1) Posts (pending moderation)
 *   2) Orphan Media (not attached to any post)
 *   3) Duplicate Clusters (grouped by shared hash)
 *
 * The code reuses existing logic for approving/rejecting posts and orphan media,
 * and adds a new tab for handling duplicates. Each duplicate cluster includes:
 *   - A list of items with resolution (width x height), file size, and an is_best_item boolean.
 *   - A 'BEST' label on the item that the system has selected as best.
 */
export default function ModerationDashboard() {
  const { fetchDashboard, performModerationAction } = useModerationAPI();
  const { addNotification } = useNotification();

  // State for fetched data, loading/error flags
  const [data, setData] = useState<ModerationDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for rejection modal
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [currentEntity, setCurrentEntity] = useState<{ type: "post" | "media"; id: number } | null>(null);

  // Which tab is active: "posts", "orphan", or "duplicates"
  const [activeKey, setActiveKey] = useState("posts");

  /**
   * Load moderation data (posts, orphan media, duplicate clusters) from the API.
   */
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
   * Locally update the moderation status for a post or media item after an approval or rejection.
   * Also updates statuses inside duplicate clusters to keep everything consistent.
   */
  function updateModerationStatus(entityType: "post" | "media", entityId: number, newStatus: string) {
    setData((prevData) => {
      if (!prevData) return prevData;

      if (entityType === "post") {
        // Update the post's status_display
        const updatedPosts = prevData.posts.map((post) =>
          post.id === entityId ? { ...post, status_display: newStatus } : post
        );
        return { ...prevData, posts: updatedPosts };

      } else if (entityType === "media") {
        // 1) Update media inside posts
        const updatedPosts = prevData.posts.map((post) => ({
          ...post,
          media_items: post.media_items.map((media: any) =>
            media.id === entityId ? { ...media, status: newStatus } : media
          ),
        }));

        // 2) Update orphan media
        const updatedOrphanMedia = prevData.orphan_media.map((media) =>
          media.id === entityId ? { ...media, status: newStatus } : media
        );

        // 3) Update items in duplicate clusters
        const updatedClusters = prevData.duplicate_clusters.map((cluster) => ({
          ...cluster,
          items: cluster.items.map((item) =>
            item.id === entityId ? { ...item, status: newStatus } : item
          ),
        }));

        return {
          ...prevData,
          posts: updatedPosts,
          orphan_media: updatedOrphanMedia,
          duplicate_clusters: updatedClusters,
        };
      }

      return prevData;
    });
  }

  /**
   * Send a moderation "approve" action for either a post or media item.
   */
  function handleApprove(entityType: "post" | "media", entityId: number) {
    performModerationAction({ entity_type: entityType, entity_id: entityId, action: "approve" })
      .then(() => {
        addNotification("Content approved successfully", "success");
        updateModerationStatus(entityType, entityId, "Approved");
      })
      .catch((err) => {
        console.error("Approval error", err);
        addNotification("Failed to approve content", "error");
      });
  }

  /**
   * Approves a post as "featured" content.
   */
  function handleApproveFeatured(postId: number) {
    performModerationAction({ entity_type: "post", entity_id: postId, action: "approve", is_featured_post: true })
      .then(() => {
        addNotification("Content approved as featured successfully", "success");
        updateModerationStatus("post", postId, "Featured");
      })
      .catch((err) => {
        console.error("Featured approval error", err);
        addNotification("Failed to approve as featured", "error");
      });
  }

  /**
   * Opens the rejection modal for a specific post or media item.
   */
  function openRejectModal(entityType: "post" | "media", entityId: number) {
    setCurrentEntity({ type: entityType, id: entityId });
    setRejectModalOpen(true);
  }

  /**
   * Called by the rejection modal to finalize the rejection action on an entity.
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
      .then(() => {
        addNotification("Content rejected successfully", "success");
        setRejectModalOpen(false);
        updateModerationStatus(currentEntity.type, currentEntity.id, "Rejected");
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
        {/* ===================== Posts Moderation Tab ===================== */}
        <Tab
          eventKey="posts"
          title={
            <span>
              Posts Moderation{" "}
              <Badge bg="secondary">{data?.posts ? data.posts.length : 0}</Badge>
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
                  {post.name} (Status: {post.status_display || "Pending moderation"})
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
                    className="btn btn-success btn-sm me-2"
                    onClick={() => handleApproveFeatured(post.id)}
                  >
                    <FontAwesomeIcon icon={faCheck} /> Approve as Featured
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => openRejectModal("post", post.id)}
                  >
                    <FontAwesomeIcon icon={faTimes} /> Reject Post
                  </button>
                </div>
                <hr style={{ margin: "1rem 0" }} />
                <h4>Media Items Moderation</h4>
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  {post.media_items.map((item: any) => (
                    <ModerationMediaTile
                      key={item.id}
                      item={{
                        id: item.id,
                        name: item.original_filename || `Media #${item.id}`,
                        thumbnail_url: item.thumbnail_url,
                        media_type: item.media_type || "photo",
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
                      }}
                      onApprove={() => handleApprove("media", item.id)}
                      onReject={() => openRejectModal("media", item.id)}
                    />
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p>No posts pending moderation.</p>
          )}
        </Tab>

        {/* ===================== Orphan Media Moderation Tab ===================== */}
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
              {data.orphan_media.map((item) => (
                <ModerationMediaTile
                  key={item.id}
                  item={{
                    id: item.id,
                    name: item.original_filename || `Media #${item.id}`,
                    thumbnail_url: item.thumbnail_url,
                    media_type: item.media_type || "photo",
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
                  }}
                  onApprove={() => handleApprove("media", item.id)}
                  onReject={() => openRejectModal("media", item.id)}
                />
              ))}
            </div>
          ) : (
            <p>No orphan media items pending moderation.</p>
          )}
        </Tab>

        {/* ===================== Duplicate Clusters Tab ===================== */}
        <Tab
          eventKey="duplicates"
          title={
            <span>
              Duplicate Clusters{" "}
              <Badge bg="secondary">
                {data?.duplicate_clusters ? data.duplicate_clusters.length : 0}
              </Badge>
            </span>
          }
        >
          {data?.duplicate_clusters && data.duplicate_clusters.length > 0 ? (
            data.duplicate_clusters.map((cluster) => (
              <div
                key={cluster.id}
                style={{
                  border: "1px solid #ccc",
                  marginBottom: "1rem",
                  padding: "1rem",
                }}
              >
                <h3>
                  Duplicate Cluster #{cluster.id} | Hash: {cluster.hash_value} |{" "}
                  Hash Type: {cluster.hash_type_name}
                </h3>
                <p>Status (numeric or custom): {cluster.status}</p>
                <p>
                  Best Item ID:{" "}
                  {cluster.best_item_id ? cluster.best_item_id : "None"}
                </p>

                {/* Display each item in the cluster with resolution/file_size info. 
                    Also highlight the best item visually using a "BEST" label or custom styling. */}
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  {cluster.items.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        position: "relative",
                        border: item.is_best_item ? "2px solid gold" : "1px solid #ccc",
                        padding: "1rem",
                        borderRadius: "4px",
                      }}
                    >
                      {/* If it's the best item, add a small label on top-right */}
                      {item.is_best_item && (
                        <span
                          style={{
                            position: "absolute",
                            top: 0,
                            right: 0,
                            backgroundColor: "gold",
                            color: "#000",
                            fontWeight: "bold",
                            padding: "2px 6px",
                            borderRadius: "0 0 0 4px",
                          }}
                        >
                          BEST
                        </span>
                      )}

                      {/* Render the tile as usual */}
                      <ModerationMediaTile
                        item={{
                          id: item.id,
                          name: item.original_filename || `Media #${item.id}`,
                          thumbnail_url: item.thumbnail_url,
                          media_type: item.media_type || "photo",
                          show_likes: false,
                          likes_counter: 0,
                          has_liked: false,
                          owner_username: "",
                          locked: false,
                          status: item.status,
                          tile_size: "small",
                          canAddToAlbum: false,
                          entity_type: "media",
                          page_type: "duplicates",
                        }}
                        onApprove={() => handleApprove("media", item.id)}
                        onReject={() => openRejectModal("media", item.id)}
                      />

                      {/* Resolution and file size displayed near the tile */}
                      <div style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
                        Resolution:{" "}
                        {item.width && item.height
                          ? `${item.width} x ${item.height}`
                          : "N/A"}
                        <br />
                        File Size:{" "}
                        {item.file_size !== null
                          ? `${item.file_size} bytes`
                          : "N/A"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p>No duplicate clusters pending moderation.</p>
          )}
        </Tab>
      </Tabs>

      {/* Rejection modal for finalizing rejections of posts or media */}
      <ModerationRejectModal
        show={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        onSubmit={handleRejectSubmit}
      />
    </div>
  );
}
