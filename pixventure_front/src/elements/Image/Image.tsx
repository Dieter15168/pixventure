"use client";

import React from "react";
import styles from "./Image.module.scss";

interface ThumbnailLinkProps {
  name: string;
  thumbnailUrl?: string;
}

const Image: React.FC<ThumbnailLinkProps> = ({
  name,
  thumbnailUrl,
}) => {
  return (
    <img
      src={thumbnailUrl || "/no-preview.jpg"}
      alt={name}
      className={styles.item_image}
      loading="lazy"
    />
  );
};

export default Image;
