// src/utils/api/terms.tsx
"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

export interface Term {
  id: number;
  term_type: number; // 1 => tag, 2 => category
  name: string;
  slug: string;
}

/**
 * React hook for terms (tags & categories).
 */
export function useTermsAPI() {
  const axios = useAxios();

  /**
   * Fetch all terms. The endpoint returns an array of objects:
   *  {
   *    "id": 1,
   *    "term_type": 2, // category
   *    "name": "Test category",
   *    "slug": "test-category"
   *  },
   *  ...
   */
  const fetchAllTerms = useCallback(async (): Promise<Term[]> => {
    const res = await axios.get("/terms/");
    return res.data as Term[];
  }, [axios]);

  return { fetchAllTerms };
}
