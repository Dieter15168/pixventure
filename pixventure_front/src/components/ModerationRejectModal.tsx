// src/components/ModerationRejectModal.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { useTermsAPI, Term } from "../utils/api/terms";

interface ModerationRejectModalProps {
  show: boolean;
  onClose: () => void;
  onSubmit: (reasonId: number, comment: string) => void;
}

export default function ModerationRejectModal({ show, onClose, onSubmit }: ModerationRejectModalProps) {
  const [reasons, setReasons] = useState<Term[]>([]);
  const [selectedReason, setSelectedReason] = useState<number | null>(null);
  const [comment, setComment] = useState("");

  useEffect(() => {
    async function loadReasons() {
      // Suppose active rejection reasons are available from a dedicated endpoint.
      // Here, we'll simulate with hardcoded data.
      setReasons([
        { id: 1, term_type: 2, name: "Inappropriate content", slug: "inappropriate" },
        { id: 2, term_type: 2, name: "Spam", slug: "spam" },
      ]);
    }
    loadReasons();
  }, []);

  function handleSubmit() {
    if (!selectedReason) {
      alert("Please select a rejection reason.");
      return;
    }
    onSubmit(selectedReason, comment);
  }

  return (
    <Modal show={show} onHide={onClose} backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>Reject Content</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group>
            <Form.Label>Select a reason:</Form.Label>
            {reasons.map((reason) => (
              <Form.Check
                key={reason.id}
                type="radio"
                label={reason.name}
                name="rejectionReason"
                id={`reason-${reason.id}`}
                value={reason.id}
                onChange={() => setSelectedReason(reason.id)}
              />
            ))}
          </Form.Group>
          <Form.Group className="mt-3">
            <Form.Label>Comment (optional):</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={handleSubmit}>
          Reject
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
