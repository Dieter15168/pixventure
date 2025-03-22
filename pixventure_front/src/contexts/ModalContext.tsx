// src/contexts/ModalContext.tsx

"use client";

import React, { createContext, useContext, useState } from "react";
import AuthModal from "../components/AuthModal/AuthModal";

interface ModalContextProps {
  /**
   * Triggers the modal to display with an optional header text.
   */
  showModal: (modalText?: string) => void;
  /**
   * Hides the modal.
   */
  hideModal: () => void;
}

const ModalContext = createContext<ModalContextProps | undefined>(undefined);

/**
 * Custom hook to access the modal context.
 */
export const useModal = (): ModalContextProps => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error("useModal must be used within a ModalProvider");
  }
  return context;
};

/**
 * ModalProvider wraps your application and renders the global AuthModal.
 */
export const ModalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [modalText, setModalText] = useState<string | undefined>(undefined);
  const [show, setShow] = useState<boolean>(false);

  const showModal = (text?: string) => {
    setModalText(text);
    setShow(true);
  };

  const hideModal = () => {
    setShow(false);
  };

  return (
    <ModalContext.Provider value={{ showModal, hideModal }}>
      {children}
      {/* Global modal rendered once */}
      <AuthModal show={show} onHide={hideModal} modalText={modalText} />
    </ModalContext.Provider>
  );
};
