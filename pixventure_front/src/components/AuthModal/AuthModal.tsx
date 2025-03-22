// src/components/AuthModal/AuthModal.tsx

"use client";

import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import SignUpForm from "../SignUpForm/SignUpForm";
import Link from "next/link";

interface AuthModalProps {
  /**
   * Controls the visibility of the modal.
   */
  show: boolean;
  /**
   * Callback to hide the modal.
   */
  onHide: () => void;
  /**
   * Optional title text for the modal header.
   */
  modalText?: string;
}

/**
 * AuthModal displays a modal dialog containing the sign up form and a link to the sign in page.
 */
const AuthModal: React.FC<AuthModalProps> = ({ show, onHide, modalText }) => {
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>{modalText || "Sign Up"}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <SignUpForm />
        <div style={{ marginTop: "15px", textAlign: "center" }}>
          <p>
            Already have an account?{" "}
            <Link href="/signin">
              Sign in
            </Link>
          </p>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AuthModal;
