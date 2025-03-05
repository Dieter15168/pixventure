"use client";

import React from "react";
import styles from "./PreviewPlaceholder.module.scss";

const PreviewPlaceholder: React.FC = () => {
  return <p className={styles.no_preview_text}>Video is rendering</p>;
};

export default PreviewPlaceholder;
