// src/contexts/ElementMenuContext.tsx
"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

// The shape of your item data (post, album, etc.)
export type ElementMenuItem = {
  entity_type: "post" | "album" | "media" | "user";
  id: number;
  name: string;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  canDelete?: boolean;
  canAddToAlbum?: boolean;
};

// The shape of the context value
interface ElementMenuContextValue {
  showMenu: boolean;
  selectedItem: ElementMenuItem | null;
  openMenu: (item: ElementMenuItem) => void;
  closeMenu: () => void;
}

// Create the context (no default value needed if always used within provider)
const ElementMenuContext = createContext<ElementMenuContextValue | undefined>(
  undefined
);

// The provider
export function ElementMenuProvider({ children }: { children: ReactNode }) {
  const [showMenu, setShowMenu] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ElementMenuItem | null>(null);

  const openMenu = (item: ElementMenuItem) => {
    setSelectedItem(item);
    setShowMenu(true);
  };

  const closeMenu = () => {
    setShowMenu(false);
    setSelectedItem(null);
  };

  const value: ElementMenuContextValue = {
    showMenu,
    selectedItem,
    openMenu,
    closeMenu,
  };

  return (
    <ElementMenuContext.Provider value={value}>
      {children}
    </ElementMenuContext.Provider>
  );
}

// A helper hook
export function useElementMenu() {
  const context = useContext(ElementMenuContext);
  if (!context) {
    throw new Error(
      "useElementMenu must be used within an ElementMenuProvider"
    );
  }
  return context;
}
