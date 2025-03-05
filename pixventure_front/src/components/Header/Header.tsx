"use client";

import { useEffect, useState } from "react";
import { getAuthToken } from "../../utils/auth";
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

export default function Header() {
  const [user, setUser] = useState<UserState | null>(null);
  const [loading, setLoading] = useState(true);
  const [showSearch, setShowSearch] = useState(false);

  const handleSearchToggle = () => {
    setShowSearch(true);
  };

  const handleSearchClose = () => {
    setShowSearch(false);
  };

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return; // Not logged in
    }

    const checkAuth = async () => {
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
          localStorage.removeItem("authToken");
          localStorage.removeItem("username");
        }
      } catch (e) {
        console.error("Auth check failed:", e);
        localStorage.removeItem("authToken");
        localStorage.removeItem("username");
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

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
          {/* (2) Search Toggle => triggers OffCanvasSearch */}
          <SearchToggle onClick={handleSearchToggle} />

          {/* (3) Add Menu => plus icon */}
          {user && <AddMenu />}

          {/* (4) User Panel => login or user dropdown */}
          <UserPanel
            user={user}
            onSignOut={() => console.log("Signed out")}
          />
        </div>
      </nav>

      {/* The offcanvas itself */}
      <OffCanvasSearch
        show={showSearch}
        onHide={handleSearchClose}
      />

      {/* The horizontal scroll menu */}
      <ScrollMenu />
    </>
  );
}
