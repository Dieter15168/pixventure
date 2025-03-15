// src/app/moderation/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useModerationAPI, ModerationDashboardData } from "../../utils/api/moderation";
import ModerationRejectModal from "../../components/ModerationRejectModal";
import Tile, { TileProps } from "../../components/Tile/Tile";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes, faEllipsisH } from "@fortawesome/free-solid-svg-icons";

export default function ModerationDashboard() {
  const { fetchDashboard, performModerationAction } = useModerationAPI();
  const [data, setData] = useState<ModerationDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [currentEntity, setCurrentEntity] = useState<{ type: "post" | "media"; id: number } | null>(null);

  // Load dashboard data on mount.
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

  // Approve action: call moderation API.
  function handleApprove(entityType: "post" | "media", entityId: number) {
    performModerationAction({
      entity_type: entityType,
      entity_id: entityId,
      action: "approve",
    })
      .then((data) => {
        console.log("Approved", data);
        // Optionally refresh dashboard data.
      })
      .catch((err) => console.error("Approval error", err));
  }

  // Open reject modal for given entity.
  function openRejectModal(entityType: "post" | "media", entityId: number) {
    setCurrentEntity({ type: entityType, id: entityId });
    setRejectModalOpen(true);
  }

  // Handle rejection submission from the modal.
  function handleRejectSubmit(reasonId: number, comment: string) {
    if (!currentEntity) return;
    performModerationAction({
      entity_type: currentEntity.type,
      entity_id: currentEntity.id,
      action: "reject",
      rejection_reason: reasonId,
      comment,
    })
      .then((data) => {
        console.log("Rejected", data);
        setRejectModalOpen(false);
        // Optionally refresh dashboard data here.
      })
      .catch((err) => console.error("Rejection error", err));
  }

  if (loading) return <div>Loading moderation dashboard...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "1rem" }}>
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
              }}
            >
              <h3>
                {post.name} (Status: {post.status_display})
              </h3>
              <p>Slug: {post.slug}</p>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {post.media_items.map((item: any) => {
                  const tileProps: TileProps = {
                    id: item.id,
                    name: item.original_filename || `Media #${item.id}`,
                    thumbnail_url: item.thumbnail_url,
                    media_type: "photo", // Adjust if necessary
                    show_likes: false,
                    likes_counter: 0,
                    has_liked: false,
                    owner_username: "", // Not needed for moderation
                    lock_logo: false,
                    status: item.status_display,
                    tile_size: "small",
                    canAddToAlbum: false,
                    entity_type: "media",
                    page_type: "posts_list",
                  };
                  return <Tile key={item.id} item={tileProps} />;
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
                media_type: "photo", // adjust as needed
                show_likes: false,
                likes_counter: 0,
                has_liked: false,
                owner_username: "",
                lock_logo: false,
                status: item.status_display,
                tile_size: "small",
                canAddToAlbum: false,
                entity_type: "media",
                page_type: "posts_list",
              };
              return (
                <div key={item.id} style={{ position: "relative" }}>
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

      {/* Moderation Reject Modal */}
      <ModerationRejectModal
        show={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        onSubmit={handleRejectSubmit}
      />
    </div>
  );
}
