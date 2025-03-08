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
import { useElementMenu, ElementMenuItem } from "../../contexts/ElementMenuContext";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEllipsisH } from "@fortawesome/free-solid-svg-icons";

export type TileItemType = 1 | 2 | 3;

export interface TileProps {
  id: number;
  name: string;
  slug: string;
  thumbnail_url?: string;
  item_type: TileItemType;
  images_count?: number;
  videos_count?: number;
  posts_count?: number;
  likes_counter: number;
  has_liked: boolean;
  owner_username: string;
  lock_logo?: boolean;
  is_moderation?: boolean;
  tile_size?: "small" | "medium" | "large";
  canDelete?: boolean;
  canAddToAlbum?: boolean;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  entity_type: "post" | "media" | "album";
}

const Tile: React.FC<{ item: TileProps }> = ({ item }) => {
  const {
    id,
    name,
    slug,
    thumbnail_url,
    item_type,
    images_count = 0,
    videos_count = 0,
    posts_count = 0,
    likes_counter,
    has_liked,
    owner_username,
    lock_logo,
    is_moderation,
    tile_size = "small",
    categories,
    tags,
    canDelete=false,
    canAddToAlbum=true,
    entity_type,
  } = item;

  const { openMenu } = useElementMenu();

  const handleMenuClick = () => {
    const item: ElementMenuItem = {
      id,
      name,
      entity_type,
      canDelete,
      canAddToAlbum,
      categories,
      tags,
    };
    openMenu(item);
  };

  // Sizing logic
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

  if (images_count > 0) {
    counters.push({ type: "photo", count: images_count });
  }
  if (videos_count > 0) {
    counters.push({ type: "video", count: videos_count });
  }
  if (videos_count > 0) {
    counters.push({ type: "post", count: posts_count });
  }

  return (
    <div className={styles.pin_container}>
      <div
        className={`${styles.item_container} ${containerClass}`}
        id={`object-${id}-2`}
      >
        <div className={`${styles.inline_card} ${cardClass} mb-2`}>
          {/* If item_type=1 or there's a thumbnail => show an image. Otherwise, if item_type=2 + no thumbnail => “rendering” */}
          {item_type === 1 || thumbnail_url ? (
            <Link href={`/${slug}`}>
              <Image
                name={name}
                thumbnailUrl={thumbnail_url}
              />
            </Link>
          ) : item_type === 2 && !thumbnail_url ? (
            <RenderingPlaceholder />
          ) : null}

          {/* If item_type=2 & we have a thumbnail => show “play” icon */}
          {item_type === 2 && thumbnail_url && <PlayButton slug={slug} />}

          {/* If totalItems > 1 => show a camera icon + count. We do that in the MediaCounter subcomponent. */}
          <MediaCounter counters={counters} />

          {/* The like button & like counter */}
          <div className={styles.like_button}>
            <LikeButton
              entity_type={entity_type}
              targetId={id}
              initialLikesCounter={likes_counter}
              initialHasLiked={has_liked}
            />
          </div>

          {/* Lock logo if needed */}
          {lock_logo && <LockLogo />}
        </div>

        {/* The bottom row (name + user + ellipsis) */}
        <div className="ps-2 d-flex">
          <div className="w-100">
            <p className={`${styles.truncate} mb-0`}>
              <Link href={`/${slug}`}>{name}</Link>
            </p>
            <p className={`${styles.truncate} mt-0`}>{owner_username}</p>
          </div>
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
