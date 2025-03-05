// components/OffCanvasSearch.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Offcanvas, Button, Form } from "react-bootstrap";
import { useTermsAPI } from "../../utils/api/terms";
import TermDisplay from "../TermDisplay"; // Import the new component

interface OffCanvasSearchProps {
  show: boolean;
  onHide: () => void;
}

export default function OffCanvasSearch({ show, onHide }: OffCanvasSearchProps) {
  const { fetchAllTerms } = useTermsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    if (show) {
      loadTerms();
    }
  }, [show]);

  const loadTerms = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAllTerms();
      // data => { categories: Term[], tags: Term[] }
      setCategories(data.categories || []);
      setTags(data.tags || []);
    } catch (err: any) {
      setError(err.message || "Failed to load terms");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    console.log("Search form submitted");
  };

  return (
    <Offcanvas show={show} onHide={onHide} placement="top" className="bg-dark text-light h-auto">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Search</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Form>
          <Form.Group controlId="searchQuery">
            <Form.Control type="text" placeholder="Start typing..." />
          </Form.Group>
          <Button variant="primary" onClick={handleSubmit} className="mt-2">
            Search
          </Button>
        </Form>

        {loading && <p>Loading terms...</p>}
        {error && <p className="text-danger">{error}</p>}

        {!loading && !error && (
          <TermDisplay
            categories={categories}
            tags={tags}
          />
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
