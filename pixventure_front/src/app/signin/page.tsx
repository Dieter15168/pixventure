// app/signin/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { saveAuthToken } from '../../utils/auth';

export default function SignInPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

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
      // data = { token, id, username, is_active_member }
      saveAuthToken(data.token);
      localStorage.setItem('username', data.username);
      
      // Possibly store is_active_member if you want
      // localStorage.setItem('isActiveMember', data.is_active_member);

      // redirect to home or wherever
      router.push('/');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Sign In</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', width: '300px' }}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit" style={{ marginTop: '10px' }}>Sign In</button>
      </form>
    </div>
  );
}
