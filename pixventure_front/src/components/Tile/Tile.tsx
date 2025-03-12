// src/components/Tile/Tile.tsx
"use client";

import React from "react";
import Link from "next/link";
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
  is_moderation?: boolean;
  tile_size?: "small" | "medium" | "large";
  canAddToAlbum?: boolean;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  entity_type: "post" | "media" | "album";
  page_type: "posts_list" | "albums_list" | "post" | "album" | "post_creation";
  /**
   * Optional album context if this tile is rendered within an album page.
   */
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
    albumContext,
  } = item;

  const { openMenu } = useElementMenu();

  const handleMenuClick = () => {
    const menuItem: ElementMenuItem = {
      id,
      name,
      entity_type,
      canAddToAlbum,
      categories,
      tags,
      // Include basic page context and merge album context if provided.
      pageContext: {
        page_type,
        entityId: id,
        ...(albumContext || {}),
      },
    };
    openMenu(menuItem);
  };

  // Determine container and card classes based on tile_size.
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

  return (
    <div className={styles.pin_container}>
      <div
        className={`${styles.item_container} ${containerClass}`}
        id={`object-${id}-2`}
      >
        <div className={`${styles.inline_card} ${cardClass} mb-2`}>
          {media_type === "photo" || thumbnail_url ? (
            <Link href={`/${slug}`}>
              <Image
                name={name}
                thumbnailUrl={thumbnail_url}
              />
            </Link>
          ) : media_type === "video" && !thumbnail_url ? (
            <RenderingPlaceholder />
          ) : null}
          {media_type === "video" && thumbnail_url && (
            <PlayButton slug={slug} />
          )}
          <MediaCounter counters={counters} />
          {show_likes && (
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
                <Link href={`/${slug}`}>{name}</Link>
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
    </div>
  );
};

export default Tile;
