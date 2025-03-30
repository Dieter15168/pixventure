// components/OffCanvasSearch.tsx
"use client";

import React, { useState, useEffect, ChangeEvent } from "react";
import { Offcanvas, Button, Form, InputGroup } from "react-bootstrap";
import { useTermsAPI } from "../../utils/api/terms";
import TermDisplay from "../TermDisplay";

interface Term {
  id: number;
  name: string;
  slug: string;
  term_type: number; // 1 => tag, 2 => category
}

interface OffCanvasSearchProps {
  show: boolean;
  onHide: () => void;
}

/**
 * OffCanvasSearch component renders a search panel that loads terms from the API,
 * filters them in real time, and provides a responsive layout.
 * When a search is submitted or a term is clicked, the offcanvas closes.
 */
export default function OffCanvasSearch({ show, onHide }: OffCanvasSearchProps) {
  const { fetchAllTerms } = useTermsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Term[]>([]);
  const [tags, setTags] = useState<Term[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

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
      // data is expected to be { categories: Term[], tags: Term[] }
      setCategories(data.categories || []);
      setTags(data.tags || []);
    } catch (err: any) {
      setError(err.message || "Failed to load terms");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    console.log("Search form submitted with query:", searchTerm);
    // Close the offcanvas after search submission.
    onHide();
  };

  // Filter terms based on user input.
  const filteredCategories = categories.filter(term =>
    term.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const filteredTags = tags.filter(term =>
    term.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  return (
    <Offcanvas show={show} onHide={onHide} placement="top" className="bg-dark text-light h-auto">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Search</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Form className="mb-3">
          <Form.Group controlId="searchQuery">
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Start typing..."
                value={searchTerm}
                onChange={handleInputChange}
              />
              <Button variant="primary" onClick={handleSubmit}>
                Search
              </Button>
            </InputGroup>
          </Form.Group>
        </Form>

        {loading && <p>Loading terms...</p>}
        {error && <p className="text-danger">{error}</p>}

        {!loading && !error && (
          <TermDisplay
            categories={filteredCategories}
            tags={filteredTags}
            onTermClick={onHide}
          />
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
