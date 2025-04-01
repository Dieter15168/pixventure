// src/components/ResolutionAccessModal/ResolutionAccessModal.tsx
"use client";

import React from "react";
import BaseModal from "../BaseModal/BaseModal";
import SignUpForm from "../SignUpForm/SignUpForm";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

interface ResolutionAccessModalProps {
  /**
   * Controls the visibility of the modal.
   */
  show: boolean;
  /**
   * Callback to hide the modal.
   */
  onHide: () => void;
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
   * The width of the original (full resolution) image.
   */
  originalWidth: number;
  /**
   * The height of the original (full resolution) image.
   */
  originalHeight: number;
}

/**
 * ResolutionAccessModal displays a paywall message for full resolution image access.
 * - For unauthenticated users, it shows the sign up form.
 * - For authenticated users, it displays a direct link to the payment page.
 *
 * It dynamically calculates the percentage of the original size being served.
 */
const ResolutionAccessModal: React.FC<ResolutionAccessModalProps> = ({
  show,
  onHide,
  servedWidth,
  servedHeight,
  fullWidth,
  fullHeight,
}) => {
  const { isAuthenticated } = useAuth();

  // Calculate the percentage of the original size being served.
  const servedArea = servedWidth * servedHeight;
  const originalArea = fullWidth * fullHeight;
  const servedPercent = Math.round((servedArea / originalArea) * 100);

  return (
    <BaseModal
      show={show}
      onHide={onHide}
      title="Image Resolution Upgrade"
    >
      <div>
        <p>This image is only {servedPercent}% of its original size</p>
        <p>
          <strong>This version:</strong> {servedWidth}x{servedHeight}px
          <br />
          <strong>Full version:</strong> {fullWidth}x{fullHeight}px
        </p>
        <p>With full version of this image you can:</p>
        <ul>
          <li>Zoom closer</li>
          <li>See all details</li>
        </ul>
        {isAuthenticated ? (
          <div style={{ marginTop: "15px", textAlign: "center" }}>
            <Link href="/payment">Become member now</Link>
          </div>
        ) : (
          <>
            <p>Start by registering</p>
            <SignUpForm />
          </>
        )}
      </div>
    </BaseModal>
  );
};

export default ResolutionAccessModal;
