// src/components/AccessModal/AccessModal.tsx
"use client";

import React from "react";
import BaseModal from "../BaseModal/BaseModal";
import SignUpForm from "../SignUpForm/SignUpForm";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext"; // Adjust path if needed

interface AccessModalProps {
  show: boolean;
  onHide: () => void;
}

/**
 * AccessModal displays custom paywall content for non-members.
 * For unauthenticated users, it shows the sign-up form; for authenticated users,
 * it displays a direct link to the payment page.
 */
const AccessModal: React.FC<AccessModalProps> = ({ show, onHide }) => {
  const { isAuthenticated } = useAuth();

  return (
    <BaseModal show={show} onHide={onHide} title="Members Area">
      <div>
        <p>Full version of ALL content is available for Members.</p>
        <p>Become a Member now and get:</p>
        <ul>
          <li>Complete Access</li>
          <li>All content in Full Resolution</li>
        </ul>
        {isAuthenticated ? (
          <div style={{ marginTop: "15px", textAlign: "center" }}>
            <Link href="/payment">Become member now</Link>
          </div>
        ) : (
          <>
            <p>Start by registering</p>
            <SignUpForm />
          </>
        )}
      </div>
    </BaseModal>
  );
};

export default AccessModal;
