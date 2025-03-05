// components/OffCanvasSearch.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Offcanvas, Button, Form } from "react-bootstrap";
import { useTermsAPI, Term } from "../../utils/api/terms";

interface OffCanvasSearchProps {
  show: boolean;
  onHide: () => void;
}

export default function OffCanvasSearch({ show, onHide }: OffCanvasSearchProps) {
  const { fetchAllTerms } = useTermsAPI();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [categories, setCategories] = useState<Term[]>([]);
  const [tags, setTags] = useState<Term[]>([]);

  // Whenever `show` becomes true, fetch the terms if needed
  useEffect(() => {
    if (show) {
      loadTerms();
    }
    // We only want to fetch once each time it opens, not every re-render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [show]);

  const loadTerms = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAllTerms();
      // separate them
      const categoriesArr = data.filter((t) => t.term_type === 2);
      const tagsArr = data.filter((t) => t.term_type === 1);

      setCategories(categoriesArr);
      setTags(tagsArr);
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
    <Offcanvas
      show={show}
      onHide={onHide}
      placement="top"
      className="bg-dark text-light h-auto"
    >
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Search</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {/* SEARCH FORM */}
        <Form>
          <Form.Group controlId="searchQuery">
            <Form.Control type="text" placeholder="Start typing..." />
          </Form.Group>
          <Button variant="primary" onClick={handleSubmit} className="mt-2">
            Search
          </Button>
        </Form>

        {/* Display loading/error states */}
        {loading && <p>Loading terms...</p>}
        {error && <p className="text-danger">{error}</p>}

        {/* Display categories & tags */}
        {!loading && !error && (
          <div className="row mt-3">
            {/* Categories */}
            {categories.length > 0 && (
              <div className="col-sm-4 mb-2">
                <h5>Categories:</h5>
                <div className="d-flex flex-wrap">
                  {categories.map((cat) => (
                    <div key={cat.id} className="m-1 p-1 border border-secondary rounded">
                      {cat.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {tags.length > 0 && (
              <div className="col-sm-8 mb-2">
                <h5>Tags:</h5>
                <div className="d-flex flex-wrap">
                  {tags.map((tag) => (
                    <div key={tag.id} className="m-1 p-1 border border-secondary rounded">
                      {tag.name}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
