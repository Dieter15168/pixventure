// src/components/ItemViewerNavigation/ItemViewerNavigation.tsx
"use client";

import React from "react";
import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, faArrowRight, faArrowCircleLeft } from "@fortawesome/free-solid-svg-icons";
import styles from "./ItemViewerNavigation.module.scss";

interface ItemViewerNavigationProps {
  previousItemUrl?: string;
  nextItemUrl?: string;
  backUrl: string; // or null if you want conditional display
}

const ItemViewerNavigation: React.FC<ItemViewerNavigationProps> = ({
  previousItemUrl,
  nextItemUrl,
  backUrl,
}) => {
  return (
    <div className={styles.navContainer}>
      {/* Back to Post Button - top left */}
      <div className={styles.backButton}>
        <Link href={backUrl}>
          <FontAwesomeIcon icon={faArrowCircleLeft} size="2x" />
        </Link>
      </div>

      {/* Previous Arrow - left center */}
      {previousItemUrl && (
        <div className={styles.leftArrow}>
          <Link href={previousItemUrl}>
            <FontAwesomeIcon icon={faArrowLeft} size="2x" />
          </Link>
        </div>
      )}

      {/* Next Arrow - right center */}
      {nextItemUrl && (
        <div className={styles.rightArrow}>
          <Link href={nextItemUrl}>
            <FontAwesomeIcon icon={faArrowRight} size="2x" />
          </Link>
        </div>
      )}
    </div>
  );
};

export default ItemViewerNavigation;
