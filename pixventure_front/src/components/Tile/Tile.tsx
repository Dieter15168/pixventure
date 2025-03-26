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

// ---------- Type Definitions ----------

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
    | "post_creation"
    | "moderation";
  status?: string;
  selected?: boolean;
  onSelectChange?: (id: number, newVal: boolean) => void;
  selectMode?: "checkbox" | "radio";
  albumContext?: AlbumContext;
}

// ---------- Helper Types for Link Behavior ----------

type LinkAction = "none" | "sameTab" | "newTab";

interface TileLinkInfo {
  finalHref: string;
  linkAction: LinkAction;
}

// ---------- Helper Function: computeTileLink ----------

/**
 * Computes the final URL and link action for a tile based on its page_type and entity_type.
 *
 * - For page_type "post_creation": no link is applied.
 * - For "random_items_list": uses a media redirect route and opens in a new tab.
 * - For "moderation" and "album": opens in a new tab.
 * - Otherwise, navigates in the same tab.
 *
 * The URL is built using entity_type:
 * - For "post": "/{main_category_slug}/{slug}"
 * - For "media": "/{main_category_slug}/{slug}"
 * - For "album": "/{slug}" (with additional album-specific logic if needed)
 *
 * @param item The tile properties.
 * @returns An object containing the finalHref and linkAction.
 */
function computeTileLink(item: TileProps): TileLinkInfo {
  const { id, slug, main_category_slug, entity_type, page_type } = item;
  const catSlug = main_category_slug || "general";

  if (page_type === "post_creation") {
    return { finalHref: "", linkAction: "none" };
  }
  if (page_type === "random_items_list") {
    return { finalHref: `/media-redirect/${id}`, linkAction: "newTab" };
  }
    if (page_type === "album" && entity_type === "media") {
    return { finalHref: `/media-redirect/${id}`, linkAction: "newTab" };
  }
  if (page_type === "moderation" || page_type === "album") {
    let href = "#";
    switch (entity_type) {
      case "post":
        href = `/${catSlug}/${slug}`;
        break;
      case "album":
        href = `/${slug}`;
        break;
      case "media":
        href = `/${catSlug}/${slug}`;
        break;
      default:
        href = "#";
    }
    return { finalHref: href, linkAction: "newTab" };
  }
  let href = "#";
  switch (entity_type) {
    case "post":
      href = `/${catSlug}/${slug}`;
      break;
    case "album":
      href = `/${slug}`;
      break;
    case "media":
      href = `/${catSlug}/${slug}`;
      break;
    default:
      href = "#";
  }
  return { finalHref: href, linkAction: "sameTab" };
}

// ---------- Helper Component: TileContainer ----------

/**
 * TileContainer conditionally renders a <label> if page_type is post_creation,
 * otherwise it renders a standard <div>.
 */
const TileContainer: React.FC<
  React.HTMLAttributes<HTMLElement> & { page_type: TileProps["page_type"] }
> = ({ page_type, children, ...rest }) => {
  if (page_type === "post_creation") {
    return <label {...rest}>{children}</label>;
  }
  return <div {...rest}>{children}</div>;
};

// ---------- Main Tile Component ----------

const Tile: React.FC<{ item: TileProps }> = ({ item }) => {
  const {
    id,
    name,
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

  // Build counters for media counts.
  const counters = [];
  if (images_count > 0) counters.push({ type: "photo", count: images_count });
  if (videos_count > 0) counters.push({ type: "video", count: videos_count });
  if (posts_count > 0) counters.push({ type: "post", count: posts_count });

  const showLikeButton = show_likes && page_type !== "post_creation";

  const checkboxId = `select-item-${id}`;

  // Compute link details.
  const { finalHref, linkAction } = computeTileLink(item);
  const wrapInLink = linkAction !== "none";
  const linkProps = linkAction === "newTab" ? { target: "_blank" } : {};

  // Add conditional class for radio selection.
  const cardClasses = `${styles.inline_card} ${cardClass} ${
    selectMode === "radio" && selected ? styles.featured_tile : ""
  } mb-2`;

  const cardContent = (
    <div className={cardClasses}>
      {media_type === "photo" || thumbnail_url ? (
        <Image
          name={name}
          thumbnailUrl={thumbnail_url}
        />
      ) : media_type === "video" && !thumbnail_url ? (
        <RenderingPlaceholder />
      ) : null}
      {media_type === "video" && thumbnail_url && (
        <PlayButton slug={item.slug} />
      )}
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
  );

  const bottomContent = (
    <div className="ps-2 d-flex">
      {entity_type !== "media" ? (
        <div className="w-100">
          <p className={`${styles.truncate} mb-0`}>
            {wrapInLink ? (
              <Link
                href={finalHref}
                {...linkProps}
              >
                {name}
              </Link>
            ) : (
              name
            )}
          </p>
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
  );

  // Render using TileContainer for post_creation mode.
  if (page_type === "post_creation") {
    return (
      <TileContainer
        page_type={page_type}
        htmlFor={selectMode === "checkbox" ? checkboxId : undefined}
        className={`${styles.item_container} ${containerClass}`}
        style={{ cursor: "pointer", display: "block", position: "relative" }}
        onClick={() => {
          if (selectMode === "radio" && onSelectChange) {
            onSelectChange(id, true);
          }
        }}
      >
        {cardContent}
        {bottomContent}
      </TileContainer>
    );
  }

  // Normal mode: render container as a <div>.
  return (
    <div className={styles.item_container}>
      {wrapInLink ? (
        <Link
          href={finalHref}
          {...linkProps}
        >
          {cardContent}
        </Link>
      ) : (
        cardContent
      )}
      {bottomContent}
    </div>
  );
};

export default Tile;
