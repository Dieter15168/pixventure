// src/components/GlowingResolutionPrompt/GlowingResolutionPrompt.tsx
"use client";

import React, { useState } from "react";
import styles from "./GlowingResolutionPrompt.module.scss";
import ResolutionAccessModal from "../ResolutionAccessModal/ResolutionAccessModal";

interface GlowingResolutionPromptProps {
  /**
   * Optional text for the modal title. (Currently unused but available for future customization.)
   */
  modalText?: string;
  /**
   * The width of the served (preview) version of the image.
   */
  servedWidth: number;
  /**
   * The height of the served (preview) version of the image.
   */
  servedHeight: number;
  /**
   * The width of the full version of the image.
   */
  fullWidth: number;
  /**
   * The height of the full version of the image.
   */
  fullHeight: number;
  /**
   * Child element to be rendered inside the glowing container.
   */
  children: React.ReactNode;
}

/**
 * GlowingResolutionPrompt
 * -------------------------
 * A specialized component that displays a glowing prompt (e.g., "HD") for accessing
 * full resolution images. On click, it opens the ResolutionAccessModal.
 */
const GlowingResolutionPrompt: React.FC<GlowingResolutionPromptProps> = ({
  modalText,
  servedWidth,
  servedHeight,
  fullWidth,
  fullHeight,
  children,
}) => {
  const [showModal, setShowModal] = useState<boolean>(false);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    setShowModal(true);
  };

  return (
    <>
      <div className={styles.promptWrapper} onClick={handleClick}>
        <div className={styles.glowingContent}>{children}</div>
      </div>
      <ResolutionAccessModal
        show={showModal}
        onHide={() => setShowModal(false)}
        servedWidth={servedWidth}
        servedHeight={servedHeight}
        fullWidth={fullWidth}
        fullHeight={fullHeight}
      />
    </>
  );
};

export default GlowingResolutionPrompt;
