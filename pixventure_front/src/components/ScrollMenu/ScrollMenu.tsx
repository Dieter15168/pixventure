// components/ScrollMenu.tsx
"use client";

import Link from "next/link";
import styles from "./ScrollMenu.module.scss";

export default function ScrollMenu() {
  return (
    <div className={`${styles.scrollmenu} bg-dark text-light sticky-top`}>
      <Link href="/" className="p-3 d-inline-block">
        Best Posts
      </Link>
      <Link href="/posts/all" className="p-3 d-inline-block">
        All Posts
      </Link>
      <Link href="/albums" className="p-3 d-inline-block">
        Albums
      </Link>
      <Link href="/best-users" className="p-3 d-inline-block">
        Best Users
      </Link>
      <Link href="/send-content" className="p-3 d-inline-block">
        Submit Content
      </Link>
      {/* Staff only links if user.is_staff */}
    </div>
  );
}
