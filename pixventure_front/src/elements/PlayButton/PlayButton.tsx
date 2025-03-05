"use client";

import Link from "next/link";
import React from "react";
import styles from "./PlayButton.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlayCircle } from "@fortawesome/free-regular-svg-icons";

interface PlayButtonProps {
  slug: string;
}

const PlayButton: React.FC<PlayButtonProps> = ({ slug }) => {
  return (
    <Link href={`/${slug}`} className={styles.player_button}>
      <FontAwesomeIcon icon={faPlayCircle} />
    </Link>
  );
};

export default PlayButton;
