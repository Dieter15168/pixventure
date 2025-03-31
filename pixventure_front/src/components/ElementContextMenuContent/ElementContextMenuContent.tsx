// src/components/ElementContextMenuContent/ElementContextMenuContent.tsx
"use client";

import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faEdit, faTrash } from "@fortawesome/free-solid-svg-icons";
import styles from "./ElementContextMenuContent.module.scss";

interface Term {
  id: number;
  term_type: number;
  name: string;
  slug: string;
}

interface ElementContextMenuContentProps {
  postMeta?: {
    id: number;
    name: string;
    slug: string;
    owner_username: string | null;
    categories: Term[];
    tags: Term[];
    can_edit: boolean;
    moderation_status?: number;
    moderation_status_display?: string;
    thumbnail_url?: string;
  };
  onSaveToAlbum: () => void;
  onDelete: () => Promise<void>;
  onEdit: () => void;
}

/**
 * ElementContextMenuContent renders the offcanvas content with
 * responsive columns for actions, categories, and tags.
 */
const ElementContextMenuContent: React.FC<ElementContextMenuContentProps> = ({
  postMeta,
  onSaveToAlbum,
  onDelete,
  onEdit,
}) => {
  return (
    <Container fluid className={styles.menuContainer}>
      <Row>
        {/* Actions Column */}
        <Col xs={12} md={3} className="mb-3">
          <div className={styles.actionsColumn}>
            <Button variant="outline-light" className="mb-2" onClick={onSaveToAlbum}>
              <FontAwesomeIcon icon={faPlus} className="me-2" />
              Save to Album
            </Button>
            {postMeta?.can_edit && (
              <>
                <Button variant="outline-light" className="mb-2" onClick={onEdit}>
                  <FontAwesomeIcon icon={faEdit} className="me-2" />
                  Edit
                </Button>
                <Button variant="outline-danger" onClick={onDelete}>
                  <FontAwesomeIcon icon={faTrash} className="me-2" />
                  Delete
                </Button>
              </>
            )}
          </div>
        </Col>
        {/* Categories Column */}
        <Col xs={12} md={3} className="mb-3">
          {postMeta?.categories && postMeta.categories.length > 0 && (
            <div className={styles.termsColumn}>
              <h5>Categories</h5>
              <div className="d-flex flex-wrap">
                {postMeta.categories.map((cat) => (
                  <a
                    key={cat.id}
                    href={`/category/${cat.slug}`}
                    className={`${styles.tag} m-1 p-1 text-decoration-none`}
                  >
                    {cat.name}
                  </a>
                ))}
              </div>
            </div>
          )}
        </Col>
        {/* Tags Column */}
        <Col xs={12} md={6} className="mb-3">
          {postMeta?.tags && postMeta.tags.length > 0 && (
            <div className={styles.termsColumn}>
              <h5>Tags</h5>
              <div className="d-flex flex-wrap">
                {postMeta.tags.map((tag) => (
                  <a
                    key={tag.id}
                    href={`/tag/${tag.slug}`}
                    className={`${styles.tag} m-1 p-1 text-decoration-none`}
                  >
                    {tag.name}
                  </a>
                ))}
              </div>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default ElementContextMenuContent;
