// src/components/CustomText/CustomText.tsx

"use client";

import React from "react";

interface CustomTextProps {
  /**
   * The text content to display.
   */
  text: string;
}

/**
 * CustomText renders a paragraph with provided text.
 */
const CustomText: React.FC<CustomTextProps> = ({ text }) => {
  return <p className="custom-text">{text}</p>;
};

export default CustomText;
