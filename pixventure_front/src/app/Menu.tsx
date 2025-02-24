// app/Menu.tsx
'use client';

import Link from 'next/link';

export default function Menu() {
  return (
    <nav
      style={{
        backgroundColor: '#f0f0f0',
        padding: '10px',
        marginBottom: '20px',
      }}
    >
      <Link href="/" style={{ marginRight: '15px' }}>
        Best Posts
      </Link>
      <Link href="/albums">Albums</Link>
    </nav>
  );
}
