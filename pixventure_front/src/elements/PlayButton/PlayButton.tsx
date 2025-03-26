"use client";

import React from "react";
import styles from "./PlayButton.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlayCircle } from "@fortawesome/free-regular-svg-icons";

interface PlayButtonProps {
  slug: string;
}

/**
 * PlayButton renders the play icon without wrapping it in a <Link>.
 * The expectation is that the parent container is already clickable.
 */
const PlayButton: React.FC<PlayButtonProps> = ({ slug }) => {
  return (
    <div className={styles.player_button}>
      <FontAwesomeIcon icon={faPlayCircle} />
    </div>
  );
};

export default PlayButton;
