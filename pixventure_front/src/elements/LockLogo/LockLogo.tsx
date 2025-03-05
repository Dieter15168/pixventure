"use client";

import React from "react";
import styles from "./LockLogo.module.scss";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCrown } from "@fortawesome/free-solid-svg-icons";

const LockLogo: React.FC = () => {
  const handleUnlock = () => {
    console.log("Clicked unlock");
  };

  return (
    <div className={styles.lock_logo}>
      <a
        href="#"
        className="rainbow rainbow_text_animated lock-logo-on-preview"
        data-bs-toggle="modal"
        data-bs-target="#upgrade-interstitial"
        onClick={handleUnlock}
      >
        <FontAwesomeIcon icon={faCrown} />
      </a>
    </div>
  );
};

export default LockLogo;
