// src/components/SignUpForm/SignUpForm.tsx

"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

/**
 * SignUpForm component handles user registration.
 */
const SignUpForm: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Handles the sign up form submission.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL;
      const res = await fetch(`${baseUrl}/accounts/signup/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to register");
      }
      // Success message; optionally, you could redirect to sign in after successful signup.
      setSuccess("User registered successfully. You can sign in now.");
    } catch (err: any) {
      setError(err.message);
      setSuccess(null);
    }
  };

  return (
    <div>
      {success && <p style={{ color: "green" }}>{success}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", width: "300px" }}
      >
        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button
          type="submit"
          style={{ marginTop: "10px" }}
        >
          Sign Up
        </button>
      </form>
      <div style={{ marginTop: "15px"}}>
        <p>
          Already have an account? <Link href="/signin">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

export default SignUpForm;
