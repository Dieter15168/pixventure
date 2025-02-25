'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getAuthToken } from '../utils/auth';

interface UserState {
  username: string;
  isActiveMember: boolean;
}

export default function Header() {
  const [user, setUser] = useState<UserState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return; // Not logged in
    }

    // If we have a token, call /api/check-auth/ to verify
    const checkAuth = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. http://127.0.0.1:8000/api
        const res = await fetch(`${baseUrl}/accounts/check-auth/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          // data might contain { is_active_member: true } or more fields
          // We also might want the username from the login response or store it in localStorage
          // For demonstration, assume we store it in localStorage from /login
          const userName = data.username || 'Unknown';
          setUser({
            username: userName,
            isActiveMember: !!data.is_active_member,
          });
        } else {
          // if token invalid, remove it
          localStorage.removeItem('authToken');
          localStorage.removeItem('username');
        }
      } catch (e) {
        console.error('Auth check failed:', e);
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  if (loading) {
    return (
      <nav style={{ background: '#eee', padding: '10px' }}>
        <p>Checking auth...</p>
      </nav>
    );
  }

  // If user is not logged in, show sign-in / sign-up
  if (!user) {
    return (
      <nav style={{ background: '#eee', padding: '10px' }}>
        <Link href="/signin" style={{ marginRight: '10px' }}>
          Sign In
        </Link>
        <Link href="/signup">Sign Up</Link>
      </nav>
    );
  }

  // If user is logged in, display username
  const userStyle = {
    color: user.isActiveMember ? 'green' : 'black',
    fontWeight: 'bold',
    marginLeft: '10px'
  };

  return (
    <nav style={{ background: '#eee', padding: '10px' }}>
      <span style={{ float: 'right' }}>
        Logged in as:
        <span style={userStyle}>{user.username}</span>
      </span>
    </nav>
  );
}
