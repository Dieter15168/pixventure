"use client";

import { useCallback } from "react";
import useAxios from "../useAxios";

/**
 * Type definitions for membership plans, payment methods, and payment context.
 */
export interface MembershipPlan {
  id: number;
  name: string;
  duration_days: number;
  price: string;
  currency: string;
}

export interface PaymentProvider {
  id: number;
  name: string;
  description?: string;
}

export interface PaymentMethod {
  id: number;
  name: string;
  icon: string;
  is_active: boolean;
  provider: PaymentProvider;
}

export interface PaymentContext {
  payment_address: string;
  crypto_amount: number;
  transaction_status: string;
  expires_at: string;
}

export interface PaymentSetupResponse {
  membership_plans: MembershipPlan[];
  payment_methods: PaymentMethod[];
  default_selected: {
    membership_plan: MembershipPlan;
    payment_method: PaymentMethod;
    payment_context: PaymentContext;
  };
}

/**
 * Custom hook to encapsulate Payment API calls.
 */
export function usePaymentAPI() {
  const axios = useAxios();

  /**
   * Fetch active membership plans.
   */
  const fetchMembershipPlans = useCallback(async (): Promise<
    MembershipPlan[]
  > => {
    const res = await axios.get("/memberships/plans/");
    return res.data;
  }, [axios]);

  /**
   * Fetch active payment methods.
   */
  const fetchPaymentMethods = useCallback(async (): Promise<
    PaymentMethod[]
  > => {
    const res = await axios.get("/payments/methods/");
    return res.data;
  }, [axios]);

  /**
   * Fetch aggregated payment setup data.
   */
  const fetchPaymentSetup =
    useCallback(async (): Promise<PaymentSetupResponse> => {
      const res = await axios.get("/payments/setup/");
      return res.data;
    }, [axios]);

  /**
   * Update payment context based on user's new selection.
   */
  const updatePaymentContext = useCallback(
    async (
      membership_plan_id: number,
      payment_method_id: number
    ): Promise<{ payment_context: PaymentContext }> => {
      const res = await axios.post("/payments/update/", {
        membership_plan_id,
        payment_method_id,
      });
      return res.data;
    },
    [axios]
  );

  return {
    fetchMembershipPlans,
    fetchPaymentMethods,
    fetchPaymentSetup,
    updatePaymentContext,
  };
}
