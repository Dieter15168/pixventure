/// src/elements/LockLogo/LockLogo.tsx

"use client";

import React from "react";
import styles from "./LockLogo.module.scss";
import { useModal } from "../../contexts/ModalContext";

interface LockLogoProps {
  /**
   * The text to be displayed in the modal when this lock logo is clicked.
   */
  modalText?: string;
}

/**
 * LockLogo component displays an animated lock icon.
 * On click, it triggers the global sign in modal via the context.
 */
const LockLogo: React.FC<LockLogoProps> = ({
  modalText = "Please sign in to unlock this content.",
}) => {
  const { showModal } = useModal();

  /**
   * Handles click event to open the global modal with the specified text.
   */
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    showModal(modalText);
  };

  return (
    <div className={styles.lock_logo}>
      <button
        type="button"
        className={styles.lock_logo_link}
        onClick={handleClick}
      >
        <span className={styles.rainbow_text_animated}>
          <i className="fas fa-crown"></i>
        </span>
      </button>
    </div>
  );
};

export default LockLogo;
