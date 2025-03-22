// components/UserPanel.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Dropdown } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUserPlus,
  faSignInAlt,
  faQuestion,
  faSignOutAlt,
  faUserCircle,
} from "@fortawesome/free-solid-svg-icons";

interface UserState {
  username: string;
  isActiveMember: boolean;
}

interface UserPanelProps {
  user: UserState | null;
  onSignOut?: () => void;
}

export default function UserPanel({ user, onSignOut }: UserPanelProps) {
  if (!user) {
    // Not logged in
    return (
      <Dropdown>
        <Dropdown.Toggle variant="secondary">Login</Dropdown.Toggle>
        <Dropdown.Menu align="end">
          <Dropdown.Item as={Link} href="/signup">
            <FontAwesomeIcon icon={faUserPlus} className="me-2" />
            Sign Up
          </Dropdown.Item>
          <Dropdown.Item as={Link} href="/signin">
            <FontAwesomeIcon icon={faSignInAlt} className="me-2" />
            Sign In
          </Dropdown.Item>
          <Dropdown.Item as={Link} href="/contact">
            <FontAwesomeIcon icon={faQuestion} className="me-2" />
            Contact
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    );
  }

  // Logged in
  const handleSignOut = () => {
    if (onSignOut) onSignOut();
  };

  return (
    <Dropdown>
      <Dropdown.Toggle variant="dark">{user.username}</Dropdown.Toggle>
      <Dropdown.Menu align="end">
        <Dropdown.Item
          as={Link}
          href="/signout"
          onClick={handleSignOut}
        >
          <FontAwesomeIcon icon={faSignOutAlt} className="me-2" />
          Sign Out
        </Dropdown.Item>
        <Dropdown.Item as={Link} href="/profile">
          <FontAwesomeIcon icon={faUserCircle} className="me-2" />
          Profile
        </Dropdown.Item>
        <Dropdown.Item as={Link} href="/contact">
          <FontAwesomeIcon icon={faQuestion} className="me-2" />
          Contact
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
}
