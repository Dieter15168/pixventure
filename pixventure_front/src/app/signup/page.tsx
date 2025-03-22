// app/signup/page.tsx
"use client";

import React from "react";
import SignUpForm from "../../components/SignUpForm/SignUpForm";

/**
 * SignUpPage renders the global sign up form, reusing the component created for the modal.
 * This approach adheres to the DRY principle, as the same SignUpForm is used across the app.
 */
export default function SignUpPage() {
  return (
    <div>
      <h1>Sign Up</h1>
      <SignUpForm />
    </div>
  );
}
