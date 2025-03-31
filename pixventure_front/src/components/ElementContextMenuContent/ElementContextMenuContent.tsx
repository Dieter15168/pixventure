"use client";

import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faEdit, faTrash } from "@fortawesome/free-solid-svg-icons";
import TermDisplay from "@/components/TermDisplay/TermDisplay";
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
  onTermClick: () => void;
}

/**
 * ElementContextMenuContent renders the offcanvas content with
 * responsive columns for actions and terms (categories & tags).
 * It reuses the existing TermDisplay component for consistency.
 */
const ElementContextMenuContent: React.FC<ElementContextMenuContentProps> = ({
  postMeta,
  onSaveToAlbum,
  onDelete,
  onEdit,
  onTermClick,
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
        {/* Terms Column */}
        <Col xs={12} md={9} className="mb-3">
          <TermDisplay
            categories={postMeta?.categories || []}
            tags={postMeta?.tags || []}
            onTermClick={onTermClick}
          />
        </Col>
      </Row>
    </Container>
  );
};

export default ElementContextMenuContent;
