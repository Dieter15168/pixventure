// components/AddMenu.tsx
"use client";

import React from "react";
import Link from "next/link";
import { Dropdown } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faCamera, faImages } from "@fortawesome/free-solid-svg-icons";

export default function AddMenu() {
  return (
    <Dropdown className="me-2">
      <Dropdown.Toggle variant="dark">
        <FontAwesomeIcon icon={faPlus} />
      </Dropdown.Toggle>
      <Dropdown.Menu align="end">
        <Dropdown.Item as={Link} href="/new-post">
          <FontAwesomeIcon icon={faCamera} className="me-2" />
          New Post
        </Dropdown.Item>
        <Dropdown.Item as={Link} href="/albums/new">
          <FontAwesomeIcon icon={faImages} className="me-2" />
          New Album
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
}
