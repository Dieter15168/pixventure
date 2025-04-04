// components/TermDisplay.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Row, Col } from "react-bootstrap";
import styles from "./TermDisplay.module.scss";

interface Term {
  id: number;
  name: string;
  slug: string;
  term_type: number;
}

interface TermDisplayProps {
  categories?: Term[];
  tags?: Term[];
  onTermClick?: () => void;
}

/**
 * TermDisplay component shows filtered categories and tags as clickable links.
 * Uses React Bootstrap's grid system for a responsive layout: categories in one column
 * (1/3 width on wide screens) and tags in another (2/3 width).
 * When a term is clicked, the onTermClick callback is triggered to close the offcanvas.
 */
export default function TermDisplay({ categories = [], tags = [], onTermClick }: TermDisplayProps) {
  return (
    <div className="mb-3">
      <Row>
        {categories.length > 0 && (
          <Col xs={12} md={4} className="mb-3 mb-md-0">
            <h5>Categories:</h5>
            <div className="d-flex flex-wrap">
              {categories.map((cat) => (
                <Link
                  key={cat.id}
                  href={`/category/${cat.slug}`}
                  onClick={onTermClick}
                  className={`${styles.tag}  m-1 p-1 border border-secondary rounded text-decoration-none text-light`}
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </Col>
        )}
        {tags.length > 0 && (
          <Col xs={12} md={8}>
            <h5>Tags:</h5>
            <div className="d-flex flex-wrap">
              {tags.map((tag) => (
                <Link
                  key={tag.id}
                  href={`/tag/${tag.slug}`}
                  onClick={onTermClick}
                  className={`${styles.tag} m-1 p-1 border border-secondary rounded text-decoration-none text-light`}
                >
                  {tag.name}
                </Link>
              ))}
            </div>
          </Col>
        )}
      </Row>
      {categories.length === 0 && tags.length === 0 && (
        null
      )}
    </div>
  );
}
