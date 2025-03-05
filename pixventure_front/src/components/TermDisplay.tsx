// src/components/TermDisplay.tsx
"use client";

import React from "react";

interface Term {
  id: number;
  name: string;
  slug: string;
  term_type: number; // 1 => tag, 2 => category
}

interface TermDisplayProps {
  categories?: Term[]; 
  tags?: Term[];
}

export default function TermDisplay({ categories = [], tags = [] }: TermDisplayProps) {
  return (
    <div className="mb-3">
      {/* If categories exist */}
      {categories?.length > 0 && (
        <div className="mb-2">
          <h5>Categories:</h5>
          <div className="d-flex flex-wrap">
            {categories.map((cat) => (
              <div key={cat.id} className="tag m-1 p-1 border border-secondary rounded">
                {cat.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* If tags exist */}
      {tags?.length > 0 && (
        <div>
          <h5>Tags:</h5>
          <div className="d-flex flex-wrap">
            {tags.map((tag) => (
              <div key={tag.id} className="tag m-1 p-1 border border-secondary rounded">
                {tag.name}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
