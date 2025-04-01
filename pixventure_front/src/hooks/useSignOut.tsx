// src/hooks/useSignOut.tsx
"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

/**
 * useSignOut
 *
 * A custom hook to handle user sign-out.
 * It updates the authentication state, clears client-side data,
 * and redirects the user to the sign-in page.
 *
 * @returns {() => void} signOut - A function that signs out the user.
 */
export default function useSignOut() {
  const router = useRouter();
  const { logout } = useAuth();

  const signOut = useCallback(() => {
    // Update the authentication state using the context's logout function
    logout();

    // Clear any additional user-related data from local storage
    localStorage.removeItem("username");

    // Redirect the user to the sign-in page after signing out
    router.push("/signin");
  }, [logout, router]);

  return signOut;
}
