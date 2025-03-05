// components/OffCanvasSearch.tsx
"use client";

import React from "react";
import { Offcanvas, Button, Form } from "react-bootstrap";

interface OffCanvasSearchProps {
  show: boolean;
  onHide: () => void;
}

export default function OffCanvasSearch({ show, onHide }: OffCanvasSearchProps) {
  const handleSubmit = () => {
    console.log("Search form submitted");
  };

  return (
    <Offcanvas show={show} onHide={onHide} placement="top" className="bg-dark text-light">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Search</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Form>
          <Form.Group controlId="searchQuery">
            <Form.Control type="text" placeholder="Start typing..." />
          </Form.Group>
          <Button variant="primary" onClick={handleSubmit}>
            Search
          </Button>
        </Form>
      </Offcanvas.Body>
    </Offcanvas>
  );
}
