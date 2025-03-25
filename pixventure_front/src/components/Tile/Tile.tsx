"use client";

import React from "react";
import styles from "./Tile.module.scss";
import Link from "next/link";
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
import { ModerationBadge, SelectCheckbox } from "./TileSubcomponents";

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
  main_category_slug?: string;
  thumbnail_url?: string;
  media_type: MediaItemType;
  images_count?: number;
  videos_count?: number;
  posts_count?: number;
  show_likes?: boolean;
  likes_counter: number;
  has_liked: boolean;
  owner_username: string;
  locked?: boolean;
  tile_size?: "small" | "medium" | "large";
  canAddToAlbum?: boolean;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  entity_type: "post" | "media" | "album";
  page_type:
    | "posts_list"
    | "albums_list"
    | "random_items_list"
    | "post"
    | "album"
    | "post_creation";
  status?: string;
  selected?: boolean;
  onSelectChange?: (id: number, newVal: boolean) => void;
  selectMode?: "checkbox" | "radio";
  albumContext?: AlbumContext;
}

const Tile: React.FC<{ item: TileProps }> = ({ item }) => {
  const {
    id,
    name,
    slug,
    main_category_slug,
    thumbnail_url,
    media_type,
    images_count = 0,
    videos_count = 0,
    posts_count = 0,
    show_likes = true,
    likes_counter,
    has_liked,
    owner_username,
    locked = false,
    tile_size = "small",
    categories,
    tags,
    canAddToAlbum = true,
    entity_type,
    page_type,
    status,
    selected,
    onSelectChange,
    selectMode,
    albumContext,
  } = item;

  const { openMenu } = useElementMenu();

  const handleMenuClick = (e: React.MouseEvent) => {
    // Prevent selection toggling when clicking the menu icon.
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

  const containerClass =
    tile_size === "large"
      ? styles.container_large
      : tile_size === "medium"
      ? styles.container_medium
      : styles.container_small;

  const cardClass =
    tile_size === "large"
      ? styles.card_large
      : tile_size === "medium"
      ? styles.card_medium
      : styles.card_small;

  const counters = [];
  if (images_count > 0) counters.push({ type: "photo", count: images_count });
  if (videos_count > 0) counters.push({ type: "video", count: videos_count });
  if (posts_count > 0) counters.push({ type: "post", count: posts_count });

  const showLikeButton = show_likes && page_type !== "post_creation";

  const checkboxId = `select-item-${id}`;

  // Determine finalHref based on page_type.
  let finalHref = "#"; // fallback
  if (page_type === "random_items_list") {
    // For random items, use the media redirect path.
    finalHref = `/media-redirect/${id}`;
  } else {
    // Use standard logic for constructing the URL.
    const catSlug = main_category_slug || "general";
    if (entity_type === "post") {
      finalHref = `/${catSlug}/${slug}`;
    } else if (entity_type === "album") {
      finalHref = `/${slug}`;
    } else if (entity_type === "media") {
      finalHref = `/${catSlug}/${slug}`;
    }
  }

  // In post_creation mode, adjust the selection UI.
  if (page_type === "post_creation") {
    return (
      // Use a label as the container so the entire tile is clickable.
      <label
        htmlFor={selectMode === "checkbox" ? checkboxId : undefined}
        className={`${styles.item_container} ${containerClass}`}
        style={{
          cursor: "pointer",
          display: "block",
          position: "relative",
        }}
        onClick={() => {
          if (selectMode === "radio" && onSelectChange) {
            onSelectChange(id, true);
          }
        }}
      >
        <div
          className={`${styles.inline_card} ${cardClass} ${
            selectMode === "radio" && selected ? styles.featured_tile : ""
          } mb-2`}
        >
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
          {locked && <LockLogo />}
          {status && <ModerationBadge statusStr={status} />}
          {selectMode === "checkbox" && (
            <input
              type="checkbox"
              id={checkboxId}
              className="pick-item-checkbox"
              checked={!!selected}
              onChange={(e) => onSelectChange?.(id, e.target.checked)}
            />
          )}
        </div>
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
    <div className={styles.item_container}>
      <div className={`${styles.inline_card} ${cardClass} mb-2`}>
        {/* For non-post_creation mode, render a Link.
            When on a random_items_list page, open the link in a new tab */}
        {media_type === "photo" || thumbnail_url ? (
          <Link
            href={finalHref}
            {...(page_type === "random_items_list" ? { target: "_blank" } : {})}
          >
            <Image
              name={name}
              thumbnailUrl={thumbnail_url}
            />
          </Link>
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
        {locked && <LockLogo />}
      </div>
      <div className="ps-2 d-flex">
        {entity_type !== "media" ? (
          <div className="w-100">
            <p className={`${styles.truncate} mb-0`}>
              <Link
                href={finalHref}
                {...(page_type === "random_items_list"
                  ? { target: "_blank" }
                  : {})}
              >
                {name}
              </Link>
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
