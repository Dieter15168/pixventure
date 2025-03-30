"use client";

import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faThumbsUp,
  faGlasses,
  faFaceFrown,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import styles from "./Tile.module.scss";

/**
 * A small badge that shows the moderation status:
 * - thumbs-up for "Approved"
 * - glasses for "Pending"
 * - frown for "Rejected"
 * - trash can for "Deleted"
 *
 * If the status is "published" or not a valid string, no icon is displayed.
 */
export function ModerationBadge({ statusStr }: { statusStr?: string }) {
  if (!statusStr || typeof statusStr !== "string") return null;

  const normalized = statusStr.toLowerCase();

  // Do not display any icon for published items.
  if (normalized.includes("published")) {
    return null;
  }

  let icon;
  let className;

  if (normalized.includes("approved")) {
    icon = faThumbsUp;
    className = styles.approved_symbol;
  } else if (normalized.includes("rejected")) {
    icon = faFaceFrown;
    className = styles.rejected_symbol;
  } else if (normalized.includes("pending")) {
    icon = faGlasses;
    className = styles.moderation_symbol;
  } else if (normalized.includes("deleted")) {
    icon = faTrash;
    className = styles.deleted_symbol;
  } else {
    return null;
  }

  return (
    <div className={styles.moderation_icon_container}>
      <FontAwesomeIcon icon={icon} className={className} />
    </div>
  );
}
