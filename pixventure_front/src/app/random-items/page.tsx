// src/app/random-items/page.tsx
"use client";

import React, { useState } from "react";
import RandomMediaWidget from "@/components/RandomMediaWidget";

export default function RandomItemsPage() {
  // Use a key to force re-mounting the widget for re-fetching items.
  const [refreshKey, setRefreshKey] = useState(Date.now());

  // When re-roll is clicked, update the key and scroll to top.
  const handleReroll = () => {
    setRefreshKey(Date.now());
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div>
      {/* Header with page title and back link */}
      <h2>Random Items</h2>

      {/* RandomMediaWidget with 20 items; key forces re-mount on re-roll */}
      <RandomMediaWidget
        count={20}
        key={refreshKey}
      />

      {/* Re-roll button using Bootstrap styling */}
      <div className="d-flex justify-content-center mt-4">
        <button
          className="btn btn-primary"
          onClick={handleReroll}
        >
          Re-roll
        </button>
      </div>
    </div>
  );
}
