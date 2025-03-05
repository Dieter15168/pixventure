// components/SearchToggle.tsx
"use client";

import React, { useState } from "react";
import { Button } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";

interface SearchToggleProps {
  onClick: () => void;
}

export default function SearchToggle({ onClick }: SearchToggleProps) {
  return (
    <Button variant="dark" className="me-2" onClick={onClick}>
      <FontAwesomeIcon icon={faSearch} />
    </Button>
  );
}
