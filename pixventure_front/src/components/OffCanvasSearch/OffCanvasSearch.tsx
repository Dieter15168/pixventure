// components/OffCanvasSearch.tsx
"use client";

import React, { useState, useEffect, ChangeEvent, KeyboardEvent } from "react";
import { Offcanvas, Button, Form, InputGroup } from "react-bootstrap";
import { useTermsAPI } from "../../utils/api/terms";
import TermDisplay from "../TermDisplay/TermDisplay";
import { useRouter } from "next/navigation";

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
 * OffCanvasSearch renders a search panel that allows the user to input a query.
 * On submission (button click or Enter key), it navigates to the search results page.
 */
export default function OffCanvasSearch({ show, onHide }: OffCanvasSearchProps) {
  const { fetchAllTerms } = useTermsAPI();
  const router = useRouter();

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
    // Navigate to the search results page with the query parameter.
    router.push(`/search?q=${encodeURIComponent(searchTerm)}`);
    onHide();
  };

  // Submit search on Enter key press.
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
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
                onKeyDown={handleKeyDown}  // Added handler for Enter key
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
