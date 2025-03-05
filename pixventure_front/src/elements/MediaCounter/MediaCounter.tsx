"use client";

import React from "react";
import styles from "./MediaCounter.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCamera,
  faVideo,
  faFileAlt,
} from "@fortawesome/free-solid-svg-icons";

interface SingleCounter {
  type: "photo" | "video" | "post" | "custom";
  count: number;
  label?: string; // optional custom label if type=custom
}

interface MediaCounterProps {
  counters: SingleCounter[]; // array of counters (photo, video, etc.)
}

const MediaCounter: React.FC<MediaCounterProps> = ({ counters }) => {
  // If no counters at all, don't render
  if (!counters || counters.length === 0) return null;

  // Decide icon/label for each type
  const getIconAndLabel = (type: string, label?: string) => {
    switch (type) {
      case "photo":
        return { icon: faCamera, label: "" };
      case "video":
        return { icon: faVideo, label: "" };
      case "post":
        return { icon: faFileAlt, label: "" };
      case "custom":
        return { icon: faCamera, label: label || "" }; 
      default:
        return { icon: faCamera, label: "" };
    }
  };

  return (
    <div className={styles.counters_container}>
      {counters.map((item, idx) => {
        // skip if count <= 0
        if (item.count <= 0) return null;
        const { icon, label } = getIconAndLabel(item.type, item.label);

        return (
          <div className={styles.counter_row} key={idx}>
            <FontAwesomeIcon icon={icon} className={styles.counter_icon} />
            <span className={styles.counter_text}>
              {item.count}
              {label ? ` ${label}` : ""}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default MediaCounter;
