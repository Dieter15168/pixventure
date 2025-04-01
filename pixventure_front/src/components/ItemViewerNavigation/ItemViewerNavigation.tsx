// src/components/ItemViewerNavigation/ItemViewerNavigation.tsx
"use client";

import React from "react";
import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, faArrowRight, faArrowCircleLeft, faEllipsisH, faCrown } from "@fortawesome/free-solid-svg-icons";
import { useElementMenu, ElementMenuItem } from "@/contexts/ElementMenuContext";
import LikeButton from "@/elements/LikeButton/LikeButton";
import styles from "./ItemViewerNavigation.module.scss";

interface ItemViewerNavigationProps {
  previousItemUrl?: string;
  nextItemUrl?: string;
  backUrl: string;

  // For the Like button:
  entityType: "post" | "media" | "album" | "user_profile";
  targetId: number;
  initialLikes: number;
  initialHasLiked: boolean;

  // For constructing the element menu:
  itemMenuData?: {
    id: number;
    name?: string;
    entity_type?: "post" | "media" | "album" | string;
    canAddToAlbum?: boolean;
    categories?: Array<any>;
    tags?: Array<any>;
    pageContext?: any;
  };
}

const ItemViewerNavigation: React.FC<ItemViewerNavigationProps> = ({
  previousItemUrl,
  nextItemUrl,
  backUrl,
  entityType,
  targetId,
  initialLikes,
  initialHasLiked,
  itemMenuData,
}) => {
  // Access the menu context.
  const { openMenu } = useElementMenu();

  const handleMenuClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!itemMenuData) return;
    // Convert the passed itemMenuData into an ElementMenuItem
    const menuItem: ElementMenuItem = {
      id: itemMenuData.id,
      name: itemMenuData.name ?? "",
      entity_type: itemMenuData.entity_type ?? "media",
      canAddToAlbum: itemMenuData.canAddToAlbum ?? true,
      categories: itemMenuData.categories ?? [],
      tags: itemMenuData.tags ?? [],
      pageContext: {
        ...(itemMenuData.pageContext ?? {}),
        entityId: itemMenuData.id,
      },
    };

    openMenu(menuItem);
  };

  return (
    <div className={styles.navContainer}>
      {/* Back to Post (top-left) */}
      <div className={styles.backButton}>
        <Link href={backUrl}>
          <FontAwesomeIcon icon={faArrowCircleLeft} size="2x" />
        </Link>
      </div>

      {/* Previous arrow (left center) */}
      {previousItemUrl && (
        <div className={styles.leftArrow}>
          <Link href={previousItemUrl}>
            <FontAwesomeIcon icon={faArrowLeft} size="2x" />
          </Link>
        </div>
      )}

      {/* Next arrow (right center) */}
      {nextItemUrl && (
        <div className={styles.rightArrow}>
          <Link href={nextItemUrl}>
            <FontAwesomeIcon icon={faArrowRight} size="2x" />
          </Link>
        </div>
      )}

      {/* Like Button - bottom-left */}
      <div className={styles.likeButton}>
        <LikeButton
          entity_type={entityType}
          targetId={targetId}
          initialLikesCounter={initialLikes}
          initialHasLiked={initialHasLiked}
        />
      </div>

      {/* Item Menu Button - bottom-right */}
      <div className={styles.menuButton} onClick={handleMenuClick}>
        <FontAwesomeIcon icon={faEllipsisH} size="2x" />
      </div>
    </div>
  );
};

export default ItemViewerNavigation;
