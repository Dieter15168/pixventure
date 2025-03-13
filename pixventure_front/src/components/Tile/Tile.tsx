// src/components/Tile/Tile.tsx
"use client";

import React from "react";
import styles from "./Tile.module.scss";

import Image from "../../elements/Image/Image";
import RenderingPlaceholder from "../../elements/PreviewPlaceholder/PreviewPlaceholder";
import PlayButton from "../../elements/PlayButton/PlayButton";
import MediaCounter from "../../elements/MediaCounter/MediaCounter";
import LikeButton from "../../elements/LikeButton/LikeButton";
import LockLogo from "../../elements/LockLogo/LockLogo";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEllipsisH } from "@fortawesome/free-solid-svg-icons";

import {
  useElementMenu,
  ElementMenuItem,
} from "../../contexts/ElementMenuContext";
import { ModerationBadge } from "./TileSubcomponents";

export interface AlbumContext {
  albumSlug: string;
  inAlbum: boolean;
  albumElementId?: number;
  can_edit?: boolean;
}

export type MediaItemType = "photo" | "video";

export interface TileProps {
  id: number;
  name: string;
  slug: string;
  thumbnail_url?: string;
  media_type: MediaItemType;

  images_count?: number;
  videos_count?: number;
  posts_count?: number;

  show_likes?: boolean;
  likes_counter: number;
  has_liked: boolean;
  owner_username: string;
  lock_logo?: boolean;
  tile_size?: "small" | "medium" | "large";
  canAddToAlbum?: boolean;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  entity_type: "post" | "media" | "album";
  page_type: "posts_list" | "albums_list" | "post" | "album" | "post_creation";

  /**
   * e.g. "Approved", "Pending moderation", "Rejected"
   */
  status?: string;
  /**
   * If in post_creation, we can allow user to select the tile with a big checkmark
   */
  selected?: boolean;
  onSelectChange?: (id: number, newVal: boolean) => void;

  albumContext?: AlbumContext;
}

const Tile: React.FC<{ item: TileProps }> = ({ item }) => {
  const {
    id,
    name,
    slug,
    thumbnail_url,
    media_type,
    images_count = 0,
    videos_count = 0,
    posts_count = 0,
    show_likes = true,
    likes_counter,
    has_liked,
    owner_username,
    lock_logo,
    tile_size = "small",
    categories,
    tags,
    canAddToAlbum = true,
    entity_type,
    page_type,
    status,
    selected,
    onSelectChange,
    albumContext,
  } = item;

  const { openMenu } = useElementMenu();

  const handleMenuClick = (e: React.MouseEvent) => {
    // If in post_creation, we don't want clicking "..." to toggle the checkbox.
    e.preventDefault();
    e.stopPropagation();

    const menuItem: ElementMenuItem = {
      id,
      name,
      entity_type,
      canAddToAlbum,
      categories,
      tags,
      pageContext: {
        page_type,
        entityId: id,
        ...(albumContext || {}),
      },
    };
    openMenu(menuItem);
  };

  // Container classes
  const containerClass =
    tile_size === "large"
      ? styles.container_large
      : tile_size === "medium"
      ? styles.container_medium
      : styles.container_small;

  // Card classes
  const cardClass =
    tile_size === "large"
      ? styles.card_large
      : tile_size === "medium"
      ? styles.card_medium
      : styles.card_small;

  // Counters
  const counters = [];
  if (images_count > 0) counters.push({ type: "photo", count: images_count });
  if (videos_count > 0) counters.push({ type: "video", count: videos_count });
  if (posts_count > 0) counters.push({ type: "post", count: posts_count });

  // Only show like button if not in post_creation
  const showLikeButton = show_likes && page_type !== "post_creation";

  // The ID for the checkbox. If you want each tile to have a unique label, do `id + '-checkbox'`
  const checkboxId = `select-item-${id}`;

  // --------------- POST CREATION MODE ---------------
  if (page_type === "post_creation") {
    return (
      <label
        htmlFor={checkboxId}
        className={`${styles.item_container} ${containerClass}`}
      >
        {/* The main tile UI */}
        <div className={`${styles.inline_card} ${cardClass} mb-2`}>
          {/* Image not a link, so we don't navigate away */}
          {media_type === "photo" || thumbnail_url ? (
            <Image
              name={name}
              thumbnailUrl={thumbnail_url}
            />
          ) : media_type === "video" && !thumbnail_url ? (
            <RenderingPlaceholder />
          ) : null}

          {media_type === "video" && thumbnail_url && (
            <PlayButton slug={slug} />
          )}
          <MediaCounter counters={counters} />
          {lock_logo && <LockLogo />}

          {/* If we have a moderation status, show the badge */}
          {status && <ModerationBadge statusStr={status} />}

          {/* The checkbox, absolutely positioned in bottom-left. */}
          <input
            type="checkbox"
            id={checkboxId}
            className="pick-item-checkbox"
            checked={!!selected}
            onChange={(e) => onSelectChange?.(id, e.target.checked)}
          />
        </div>

        {/* Title, owner, etc. */}
        <div className="ps-2 d-flex">
          {entity_type !== "media" ? (
            <div className="w-100">
              <p className={`${styles.truncate} mb-0`}>{name}</p>
              <p className={`${styles.truncate} mt-0`}>{owner_username}</p>
            </div>
          ) : (
            <div className="w-100"></div>
          )}
          <div
            className="flex-shrink-1"
            onClick={handleMenuClick}
          >
            <FontAwesomeIcon
              icon={faEllipsisH}
              className="text_over_image_tile"
            />
          </div>
        </div>
      </label>
    );
  }

  // --------------- NORMAL MODE (all other page types) ---------------
  return (
    <div
      className={`${styles.item_container} ${containerClass}`}
    >
      <div className={`${styles.inline_card} ${cardClass} mb-2`}>
        {/* Normal link or anchor for non-post_creation */}
        {media_type === "photo" || thumbnail_url ? (
          <a href={`/${slug}`}>
            <Image
              name={name}
              thumbnailUrl={thumbnail_url}
            />
          </a>
        ) : media_type === "video" && !thumbnail_url ? (
          <RenderingPlaceholder />
        ) : null}

        {media_type === "video" && thumbnail_url && <PlayButton slug={slug} />}
        <MediaCounter counters={counters} />

        {showLikeButton && (
          <div className={styles.like_button}>
            <LikeButton
              entity_type={entity_type}
              targetId={id}
              initialLikesCounter={likes_counter}
              initialHasLiked={has_liked}
            />
          </div>
        )}

        {lock_logo && <LockLogo />}
      </div>

      <div className="ps-2 d-flex">
        {entity_type !== "media" ? (
          <div className="w-100">
            <p className={`${styles.truncate} mb-0`}>
              <a href={`/${slug}`}>{name}</a>
            </p>
            <p className={`${styles.truncate} mt-0`}>{owner_username}</p>
          </div>
        ) : (
          <div className="w-100"></div>
        )}
        <div className="flex-shrink-1">
          <FontAwesomeIcon
            icon={faEllipsisH}
            className="text_over_image_tile"
            onClick={handleMenuClick}
          />
        </div>
      </div>
    </div>
  );
};

export default Tile;
