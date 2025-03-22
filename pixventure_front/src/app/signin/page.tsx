// File: app/signin/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext'; // Adjust the import path as needed

/**
 * SignInPage Component
 *
 * This component handles user sign-in. Upon successful login:
 * - It updates the global authentication state using the AuthContext's login function.
 * - It saves additional user info if needed.
 * - It redirects the user to the home page.
 */
export default function SignInPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { login } = useAuth(); // Retrieve the login method from AuthContext

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL; // e.g. http://127.0.0.1:8000/api
      const res = await fetch(`${baseUrl}/accounts/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        throw new Error('Invalid credentials or server error');
      }
      const data = await res.json();
      // Update the authentication state using the AuthContext's login function.
      login(data.token);
      // Optionally, store additional user info for later use.
      localStorage.setItem('username', data.username);
      
      // Redirect to the home page after successful login.
      router.push('/');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Sign In</h1>
      <form
        onSubmit={handleSubmit}
        style={{ display: 'flex', flexDirection: 'column', width: '300px' }}
      >
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit" style={{ marginTop: '10px' }}>
          Sign In
        </button>
      </form>
    </div>
  );
}
