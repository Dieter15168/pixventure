// src/components/NavigationBar.tsx
"use client";

import React from "react";
import styles from "./NavigationBar.module.scss";

/**
 * Defines a navigation button.
 */
export interface NavigationButton {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "success" | "default";
}

/**
 * Props for the NavigationBar component.
 * It renders left and right button groups.
 */
interface NavigationBarProps {
  leftButtons: NavigationButton[];
  rightButtons: NavigationButton[];
}

const NavigationBar: React.FC<NavigationBarProps> = ({
  leftButtons,
  rightButtons,
}) => {
  return (
    <div className={styles.navBar}>
      <div className={styles.leftButtons}>
        {leftButtons.map((button, index) => (
          <button
            key={index}
            onClick={button.onClick}
            className={`${styles.navButton} ${styles[button.variant || "default"]}`}
          >
            {button.label}
          </button>
        ))}
      </div>
      <div className={styles.rightButtons}>
        {rightButtons.map((button, index) => (
          <button
            key={index}
            onClick={button.onClick}
            className={`${styles.navButton} ${styles[button.variant || "default"]}`}
          >
            {button.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default NavigationBar;
