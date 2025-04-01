// src/elements/LockLogo/LockLogo.tsx
"use client";

import React, { useState } from "react";
import styles from "./LockLogo.module.scss";
import AccessModal from "@/components/AccessModal/AccessModal";

interface LockLogoProps {
  /**
   * The text to be displayed in the modal when this lock logo is clicked.
   */
  modalText?: string;
}

/**
 * LockLogo component displays an animated lock icon.
 * On click, it opens a specialized modal (AccessModal) for the members area.
 */
const LockLogo: React.FC<LockLogoProps> = ({
  modalText = "Members Area",
}) => {
  const [showModal, setShowModal] = useState<boolean>(false);

  /**
   * Handles click event to open the modal.
   */
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setShowModal(true);
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
      {/* Render the specialized AccessModal locally */}
      <AccessModal show={showModal} onHide={() => setShowModal(false)} />
    </div>
  );
};

export default LockLogo;