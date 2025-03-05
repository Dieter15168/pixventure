"use client";

import React from "react";
import Link from "next/link";

interface SiteLogoProps {
  brandName: string;
}

export default function SiteLogo({ brandName }: SiteLogoProps) {
  return (
    <Link href="/" className="navbar-brand">
      {brandName}
    </Link>
  );
}
