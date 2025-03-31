// src/components/ModerationMediaTile.tsx
"use client";

import React from "react";
import Tile, { TileProps } from "./Tile/Tile";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/free-solid-svg-icons";
import { getStatusStyle } from "../utils/moderationHelpers";

interface ModerationMediaTileProps {
  item: TileProps;
  onApprove: () => void;
  onReject: () => void;
}

/**
 * ModerationMediaTile Component
 *
 * Wraps the Tile component with dedicated approve/reject buttons for an individual media item.
 * It displays a status badge to indicate whether the item is pending, approved, or rejected.
 *
 * @param {ModerationMediaTileProps} props - Component properties.
 * @returns {JSX.Element}
 */
export default function ModerationMediaTile({
  item,
  onApprove,
  onReject,
}: ModerationMediaTileProps) {
  // Determine badge text – default to "Pending moderation" if status is empty.
  const statusText = item.status ? item.status : "Pending moderation";

  return (
    <div style={{ position: "relative", ...getStatusStyle(item.status) }}>
      <Tile item={item} />
      {/* Status badge overlay */}
      <div
        style={{
          position: "absolute",
          top: 4,
          left: 4,
          padding: "2px 6px",
          backgroundColor: "rgba(0,0,0,0.6)",
          color: "white",
          fontSize: "0.75rem",
          borderRadius: "4px",
        }}
      >
        {statusText}
      </div>
      <div style={{ marginTop: "0.5rem" }}>
        <button className="btn btn-success btn-sm me-2" onClick={onApprove}>
          <FontAwesomeIcon icon={faCheck} /> Approve
        </button>
        <button className="btn btn-danger btn-sm" onClick={onReject}>
          <FontAwesomeIcon icon={faTimes} /> Reject
        </button>
      </div>
    </div>
  );
}
