// File: app/signout/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext'; // Adjust the import path based on your project structure

/**
 * SignOutPage Component
 *
 * This component handles the user sign-out process. Upon mounting, it:
 *  - Calls the logout function from the AuthContext to update authentication state.
 *  - Clears additional client-side data such as the username.
 *  - Redirects the user to the sign in page.
 */
export default function SignOutPage() {
  const router = useRouter();
  const { logout } = useAuth();

  useEffect(() => {
    // Update the authentication state using the context's logout function
    logout();

    // Optionally, clear any additional user-related data
    localStorage.removeItem('username');

    // Redirect the user to the sign in page after sign out
    router.push('/signin');
  }, [logout, router]);

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Signing Out...</h1>
      <p>You are being logged out. Please wait.</p>
    </div>
  );
}
