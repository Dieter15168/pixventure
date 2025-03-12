// src/components/ErrorModal.tsx
"use client";

import React from "react";
import { Modal, Button } from "react-bootstrap";

interface ErrorModalProps {
  show: boolean;      // Whether to show the modal
  errors: string[];   // Array of error messages
  onClose: () => void;
}

export default function ErrorModal({ show, errors, onClose }: ErrorModalProps) {
  return (
    <Modal show={show} onHide={onClose} backdrop="static" keyboard={false} scrollable>
      <Modal.Header closeButton>
        <Modal.Title>Upload Errors</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {errors.length > 0 ? (
          <ul>
            {errors.map((err, idx) => (
              <li key={idx} className="text-danger">
                {err}
              </li>
            ))}
          </ul>
        ) : (
          <p>No errors to display.</p>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
