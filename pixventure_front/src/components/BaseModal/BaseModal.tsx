// src/components/BaseModal/BaseModal.tsx
"use client";

import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

interface BaseModalProps {
  show: boolean;
  onHide: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

/**
 * BaseModal renders a generic modal container that can be composed with custom content.
 */
const BaseModal: React.FC<BaseModalProps> = ({ show, onHide, title, children, footer }) => {
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{children}</Modal.Body>
      <Modal.Footer>
        {footer ? (
          footer
        ) : (
          <Button variant="secondary" onClick={onHide}>
            Close
          </Button>
        )}
      </Modal.Footer>
    </Modal>
  );
};

export default BaseModal;
