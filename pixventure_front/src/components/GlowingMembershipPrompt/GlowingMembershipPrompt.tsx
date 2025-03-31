// src/components/GlowingMembershipPrompt/GlowingMembershipPrompt.tsx
"use client";

import React from "react";
import styles from "./GlowingMembershipPrompt.module.scss";
import { useModal } from "@/contexts/ModalContext";

interface GlowingMembershipPromptProps {
  /**
   * The text to be displayed in the modal when this element is clicked.
   */
  modalText?: string;
  /**
   * Child element to be rendered inside the glowing container.
   */
  children: React.ReactNode;
}

/**
 * GlowingMembershipPrompt
 * -------------------------
 * A generic component that wraps its child(ren) with a glowing style and
 * opens the membership modal when clicked. The glowing style is applied automatically,
 * ensuring that any passed child (e.g., "HD") is styled consistently.
 */
const GlowingMembershipPrompt: React.FC<GlowingMembershipPromptProps> = ({
  modalText = "Please sign up for membership to access premium features.",
  children,
}) => {
  const { showModal } = useModal();

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    showModal(modalText);
  };

  return (
    <div className={styles.membershipPromptWrapper} onClick={handleClick}>
      <div className={styles.glowingContent}>
        {children}
      </div>
    </div>
  );
};

export default GlowingMembershipPrompt;
