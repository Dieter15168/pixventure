// src/components/ModerationRejectModal.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { useModerationAPI, RejectionReason } from "../utils/api/moderation";

interface ModerationRejectModalProps {
  show: boolean;
  onClose: () => void;
  onSubmit: (reasonIds: number[], comment: string) => void;
}

export default function ModerationRejectModal({
  show,
  onClose,
  onSubmit,
}: ModerationRejectModalProps) {
  const { fetchActiveRejectionReasons } = useModerationAPI();
  const [reasons, setReasons] = useState<RejectionReason[]>([]);
  const [selectedReasonIds, setSelectedReasonIds] = useState<number[]>([]);
  const [comment, setComment] = useState("");

  useEffect(() => {
    async function loadReasons() {
      try {
        const data = await fetchActiveRejectionReasons();
        setReasons(data);
      } catch (err) {
        console.error("Failed to load rejection reasons", err);
      }
    }
    loadReasons();
  }, [fetchActiveRejectionReasons]);

  function toggleReason(reasonId: number) {
    setSelectedReasonIds((prev) =>
      prev.includes(reasonId)
        ? prev.filter((id) => id !== reasonId)
        : [...prev, reasonId]
    );
  }

  function handleSubmit() {
    if (selectedReasonIds.length === 0) {
      alert("Please select at least one rejection reason.");
      return;
    }
    onSubmit(selectedReasonIds, comment);
  }

  return (
    <Modal
      show={show}
      onHide={onClose}
      backdrop="static"
    >
      <Modal.Header closeButton>
        <Modal.Title>Reject Content</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group>
            <Form.Label>
              Select rejection reasons (choose one or more):
            </Form.Label>
            {reasons.map((reason) => (
              <Form.Check
                key={reason.id}
                type="checkbox"
                label={reason.name}
                id={`reason-${reason.id}`}
                value={reason.id}
                checked={selectedReasonIds.includes(reason.id)}
                onChange={() => toggleReason(reason.id)}
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
        <Button
          variant="secondary"
          onClick={onClose}
        >
          Cancel
        </Button>
        <Button
          variant="danger"
          onClick={handleSubmit}
        >
          Reject
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
