// src/components/common/SharedMasonry.tsx
"use client"; // required for Next.js client-side components

import React from "react";
import Masonry from "react-masonry-css";
import "./SharedMasonry.scss"; // optional, if you store CSS here

interface SharedMasonryProps {
  children: React.ReactNode;
}

// Single place to define your column breakpoints:
const breakpointColumnsObj = {
  default: 5, // e.g. 5 columns at extra large widths
  1200: 3,    // 3 columns if width < 1200px
  900: 2,     // 2 columns if width < 900px
  600: 1,     // 1 column if width < 600px
};

export default function SharedMasonry({ children }: SharedMasonryProps) {
  return (
    <Masonry
      breakpointCols={breakpointColumnsObj}
      // These class names can be anything, but must match your global or module CSS:
      className="masonry-grid"
      columnClassName="masonry-column"
    >
      {children}
    </Masonry>
  );
}
