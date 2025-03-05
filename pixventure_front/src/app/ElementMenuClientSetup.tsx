// src/app/ElementMenuClientSetup.tsx
"use client";

import React from "react";
import { ElementMenuProvider } from "../contexts/ElementMenuContext";
import ElementMenuOffcanvas from "../components/ElementMenuOffcanvas";

// This wrapper provides the context and also renders the single global menu offcanvas
export default function ElementMenuClientSetup({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ElementMenuProvider>
      {children}
      <ElementMenuOffcanvas />
    </ElementMenuProvider>
  );
}
