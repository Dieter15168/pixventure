// src/contexts/ElementMenuContext.tsx
"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

/**
 * Shape of the item data (post, album, media, user) used in the item menu.
 */
export type ElementMenuItem = {
  entity_type: "post" | "album" | "media" | "user";
  id: number;
  name: string;
  categories?: Array<{ name: string; slug: string }>;
  tags?: Array<{ name: string; slug: string }>;
  // Removed canDelete in favor of API-provided permission (can_edit).
  // Optional property provided later by the API:
  canEdit?: boolean;
  canAddToAlbum?: boolean;
  /**
   * Page context contains the current view's information.
   * It includes:
   * - page_type: "posts_list" | "albums_list" | "post" | "album"
   * - entityId: the ID of the entity as displayed on that page.
   * Optionally, in album views, additional info (albumSlug, inAlbum, albumElementId) can be provided.
   */
  pageContext?: {
    page_type: "posts_list" | "albums_list" | "post" | "album";
    entityId: number;
    albumSlug?: string;
    inAlbum?: boolean;
    albumElementId?: number;
  };
};

/**
 * Shape of the context value.
 */
interface ElementMenuContextValue {
  showMenu: boolean;
  selectedItem: ElementMenuItem | null;
  openMenu: (item: ElementMenuItem) => void;
  closeMenu: () => void;
}

/**
 * Create the context (must be used within a provider)
 */
const ElementMenuContext = createContext<ElementMenuContextValue | undefined>(undefined);

/**
 * Provider component for the Element Menu context.
 */
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

  const value: ElementMenuContextValue = { showMenu, selectedItem, openMenu, closeMenu };

  return <ElementMenuContext.Provider value={value}>{children}</ElementMenuContext.Provider>;
}

/**
 * Custom hook to access the Element Menu context.
 */
export function useElementMenu() {
  const context = useContext(ElementMenuContext);
  if (!context) {
    throw new Error("useElementMenu must be used within an ElementMenuProvider");
  }
  return context;
}
