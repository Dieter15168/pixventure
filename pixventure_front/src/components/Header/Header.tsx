// src/components/Header.tsx
"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext"; // Adjust the import path as needed
import OffCanvasSearch from "../OffCanvasSearch/OffCanvasSearch";
import ScrollMenu from "../ScrollMenu/ScrollMenu";
import SiteLogo from "./SiteLogo";
import SearchToggle from "./SearchToggle";
import AddMenu from "./AddMenu";
import UserPanel from "./UserPanel";

interface UserState {
  username: string;
  isActiveMember: boolean;
}

/**
 * Header Component
 *
 * This component displays the main navigation header. It uses the AuthContext to:
 * - Determine whether the user is authenticated.
 * - Fetch and display user details from the API if authenticated.
 * - Trigger UI changes (such as showing the AddMenu and user dropdown) based on auth status.
 *
 * The component also manages the display state for the off-canvas search menu.
 */
export default function Header() {
  const { token, logout, isAuthenticated } = useAuth();
  const [user, setUser] = useState<UserState | null>(null);
  const [loading, setLoading] = useState(true);
  const [showSearch, setShowSearch] = useState(false);

  // Toggle for off-canvas search
  const handleSearchToggle = () => {
    setShowSearch(true);
  };

  const handleSearchClose = () => {
    setShowSearch(false);
  };

  /**
   * useEffect to check the user's auth details whenever the token changes.
   * If a token exists, it calls the check-auth endpoint to retrieve user details.
   * If the token is invalid or absent, the user state is cleared and auth state updated.
   */
  useEffect(() => {
    async function checkAuth() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL;
        const res = await fetch(`${baseUrl}/accounts/check-auth/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          const userName = data.username || "Unknown";
          setUser({
            username: userName,
            isActiveMember: !!data.is_active_member,
          });
        } else {
          // Invalidate token if response is not OK
          logout();
        }
      } catch (e) {
        console.error("Auth check failed:", e);
        logout();
      }
      setLoading(false);
    }
    checkAuth();
  }, [token, logout]);

  // While checking auth, display a loading indicator in the header.
  if (loading) {
    return (
      <nav className="navbar navbar-dark bg-dark px-3">
        <span className="navbar-text">Checking auth...</span>
      </nav>
    );
  }

  return (
    <>
      <nav className="navbar navbar-dark bg-dark px-3">
        {/* (1) Site Logo */}
        <SiteLogo brandName="MySite" />

        <div className="ms-auto d-flex align-items-center">
          {/* (2) Search Toggle: triggers OffCanvasSearch */}
          <SearchToggle onClick={handleSearchToggle} />

          {/* (3) Add Menu: shown only if the user is authenticated */}
          {isAuthenticated && <AddMenu />}

          {/* (4) User Panel: displays login button or user dropdown,
              the sign-out action now calls the logout function from AuthContext */}
          <UserPanel user={user} onSignOut={logout} />
        </div>
      </nav>

      {/* Off-canvas search component */}
      <OffCanvasSearch show={showSearch} onHide={handleSearchClose} />

      {/* Horizontal scroll menu */}
      <ScrollMenu />
    </>
  );
}
