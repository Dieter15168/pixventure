// src/app/new-post/page.tsx
"use client";

import React, { useState } from "react";
import ErrorModal from "../../../components/ErrorModal";
import Step1MediaSelection from "./Step1MediaSelection";
import Step2PostFinalization from "./Step2PostFinalization";
import { MinimalMediaItemDTO } from "./AvailableMedia";

/**
 * The top-level multi-step page for creating a new post.
 * Step 1: user picks items
 * Step 2: user finalizes the post (name, featured item, terms)
 */
export default function NewPostPage() {
  const [step, setStep] = useState(1);

  // The "selected" items from step 1 (the actual objects, not just IDs)
  const [selectedItems, setSelectedItems] = useState<MinimalMediaItemDTO[]>([]);

  // Potentially we can store errors or do a top-level ErrorModal if desired
  const [errors, setErrors] = useState<string[]>([]);
  const [showErrorModal, setShowErrorModal] = useState(false);

  function handleCloseModal() {
    setShowErrorModal(false);
  }

  // Move to step 2
  function goToStep2(items: MinimalMediaItemDTO[]) {
    if (items.length === 0) {
      alert("Please select at least one media item!");
      return;
    }
    setSelectedItems(items);
    setStep(2);
  }

  return (
    <div>
      {step === 1 && (
        <Step1MediaSelection
          onNextStep={goToStep2}
          errors={errors}
          setErrors={setErrors}
          showErrorModal={showErrorModal}
          setShowErrorModal={setShowErrorModal}
        />
      )}

      {step === 2 && (
        <Step2PostFinalization
          selectedItems={selectedItems}
          onBack={() => setStep(1)}
        />
      )}

      <ErrorModal
        show={showErrorModal && errors.length > 0}
        errors={errors}
        onClose={handleCloseModal}
      />
    </div>
  );
}
