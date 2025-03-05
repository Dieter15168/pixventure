"use client";

import React from "react";
import styles from "./LikeButton.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeart } from "@fortawesome/free-solid-svg-icons";

interface LikeButtonProps {
  itemId: number;
  likesCounter: number;
  hasLiked: boolean;
}

const LikeButton: React.FC<LikeButtonProps> = ({
  itemId,
  likesCounter,
  hasLiked,
}) => {
  const handleLike = () => {
    alert(`Liking item id=${itemId}. Already liked? ${hasLiked}`);
  };

  return (
    <div
      onClick={handleLike}
    >
      <FontAwesomeIcon
        icon={faHeart}
        className={`${styles.like_icon} ${hasLiked ? "text-danger" : ""}`}
      />
      <span className={styles.like_counter}>
        {likesCounter > 0 ? likesCounter : ""}
      </span>
    </div>
  );
};

export default LikeButton;
