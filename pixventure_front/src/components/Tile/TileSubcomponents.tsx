// src/components/Tile/TileSubcomponents.tsx
"use client";

import React, { useCallback } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faThumbsUp,
  faGlasses,
  faFaceFrown,
} from "@fortawesome/free-solid-svg-icons";
import styles from "./Tile.module.scss";

/**
 * A small badge that shows the moderation status:
 * - thumbs-up for "Approved"
 * - glasses for "Pending"
 * - frown for "Rejected"
 */
export function ModerationBadge({ statusStr }: { statusStr: string }) {
  if (!statusStr) return null;

  const normalized = statusStr.toLowerCase();
  let icon = faGlasses; // Default for pending
  let className = styles.moderation_symbol; // Default color or style

  if (normalized.includes("approved")) {
    icon = faThumbsUp;
    className = styles.approved_symbol;
  } else if (normalized.includes("rejected")) {
    icon = faFaceFrown;
    className = styles.rejected_symbol;
  } else if (normalized.includes("pending")) {
    icon = faGlasses;
    className = styles.moderation_symbol;
  }

  return (
    <div className={styles.moderation_icon_container}>
      <FontAwesomeIcon icon={icon} className={className} />
    </div>
  );
}

/**
 * A large checkbox for selecting a tile in the "post_creation" page type.
 */
export function SelectCheckbox({
  id,
  selected = false,
  onChange,
}: {
  id: number;
  selected?: boolean;
  onChange?: (newVal: boolean) => void;
}) {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.checked);
    },
    [onChange]
  );

  const checkboxId = `select-item-${id}`;

  return (
    <>
      <input
        type="checkbox"
        id={checkboxId}
        className="pick-item-checkbox" // We'll define this styling in Tile.module.scss or a global CSS
        checked={selected}
        onChange={handleChange}
      />
      {/* 
        The label with class "term-check" is placed immediately after.
        Your custom CSS will show a big checkmark if it's checked.
      */}
      <label className="term-check" htmlFor={checkboxId} />
    </>
  );
}
