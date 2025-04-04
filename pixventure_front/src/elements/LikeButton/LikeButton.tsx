// src/elements/LikeButton/LikeButton.tsx
"use client";

import React, { useState } from "react";
import styles from "./LikeButton.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeart } from "@fortawesome/free-solid-svg-icons";
import { useSocialAPI } from "../../utils/api/social";
import { useModal } from "../../contexts/ModalContext";

interface LikeButtonProps {
  entity_type: "post" | "media" | "album" | "user_profile";
  targetId: number;
  initialLikesCounter: number;
  initialHasLiked: boolean;
}

const LikeButton: React.FC<LikeButtonProps> = ({
  entity_type,
  targetId,
  initialLikesCounter,
  initialHasLiked,
}) => {
  const { toggleLike } = useSocialAPI();
  const { showModal } = useModal();
  const [likesCounter, setLikesCounter] = useState<number>(initialLikesCounter);
  const [hasLiked, setHasLiked] = useState<boolean>(initialHasLiked);
  const [loading, setLoading] = useState(false);

  /**
   * Handles the like toggle action.
   * Prevents event propagation and default link navigation.
   * If the user is not authenticated (401 response), shows the sign in modal.
   */
  const handleToggleLike = async (e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();
    e.preventDefault(); // Prevent default anchor navigation

    if (loading) return; // Prevent duplicate clicks
    setLoading(true);

    // Store current state to revert in case of error
    const oldLikes = likesCounter;
    const oldHasLiked = hasLiked;

    // Determine action based on current state
    const action: "like" | "unlike" = hasLiked ? "unlike" : "like";

    // Immediately update state optimistically
    if (action === "like") {
      setHasLiked(true);
      setLikesCounter(oldLikes + 1);
    } else {
      setHasLiked(false);
      setLikesCounter(oldLikes - 1);
    }

    try {
      const response = await toggleLike(entity_type, targetId, action);
      // Use updated values from backend if provided; otherwise, keep our optimistic update.
      if (response.likes_counter !== undefined) {
        setLikesCounter(response.likes_counter);
      }
      if (response.has_liked !== undefined) {
        setHasLiked(response.has_liked);
      }
    } catch (error: any) {
      // If unauthorized, revert state and show sign in modal.
      if (error.response && error.response.status === 401) {
        setLikesCounter(oldLikes);
        setHasLiked(oldHasLiked);
        showModal("Please sign in to like this content.");
        return;
      }
      // On other errors, revert to previous state.
      setLikesCounter(oldLikes);
      setHasLiked(oldHasLiked);
      console.error("Failed to toggle like:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={styles.like_button_container}
      onClick={handleToggleLike}
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
