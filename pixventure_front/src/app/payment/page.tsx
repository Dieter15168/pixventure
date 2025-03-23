// src/app/payment/page.tsx

"use client";

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { 
  usePaymentAPI, 
  MembershipPlan, 
  PaymentMethod, 
  PaymentSetupResponse, 
  PaymentContext 
} from '@/utils/api/payment';

// SWR fetcher for the setup endpoint.
const fetcher = (key: string, fetchFunction: () => Promise<any>) => fetchFunction();

/**
 * PaymentPage Component
 * Displays membership plan and payment method selection along with updated payment context.
 */
const PaymentPage: React.FC = () => {
  const { fetchPaymentSetup, updatePaymentContext } = usePaymentAPI();
  const { data, error } = useSWR<PaymentSetupResponse>('paymentSetup', () => fetchPaymentSetup());

  // Local state for selected options and payment context.
  const [selectedPlan, setSelectedPlan] = useState<MembershipPlan | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod | null>(null);
  const [paymentContext, setPaymentContext] = useState<PaymentContext | null>(null);

  // Initialize default selections from the aggregated API response.
  useEffect(() => {
    if (data) {
      setSelectedPlan(data.default_selected.membership_plan);
      setSelectedMethod(data.default_selected.payment_method);
      setPaymentContext(data.default_selected.payment_context);
    }
  }, [data]);

  // Handler for when the membership plan changes.
  const handlePlanChange = async (plan: MembershipPlan) => {
    setSelectedPlan(plan);
    if (selectedMethod) {
      try {
        const response = await updatePaymentContext(plan.id, selectedMethod.id);
        setPaymentContext(response.payment_context);
      } catch (err) {
        console.error("Error updating payment context", err);
      }
    }
  };

  // Handler for when the payment method changes.
  const handleMethodChange = async (method: PaymentMethod) => {
    setSelectedMethod(method);
    if (selectedPlan) {
      try {
        const response = await updatePaymentContext(selectedPlan.id, method.id);
        setPaymentContext(response.payment_context);
      } catch (err) {
        console.error("Error updating payment context", err);
      }
    }
  };

  if (error) return <div>Error loading payment setup data.</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="payment-container" style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Choose Your Plan and Payment Method</h1>
      <div className="selection-area" style={{ display: 'flex', gap: '2rem' }}>
        {/* Membership Plan Selection */}
        <div className="plan-selection">
          <h2>Select Membership Plan</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {data.membership_plans.map((plan) => (
              <li key={plan.id} style={{ marginBottom: '1rem' }}>
                <label>
                  <input
                    type="radio"
                    name="membershipPlan"
                    value={plan.id}
                    checked={selectedPlan?.id === plan.id}
                    onChange={() => handlePlanChange(plan)}
                  />
                  {` ${plan.name} - $${plan.price} ${plan.currency} (Duration: ${plan.duration_days} days)`}
                </label>
              </li>
            ))}
          </ul>
        </div>

        {/* Payment Method Selection */}
        <div className="payment-method-selection">
          <h2>Select Payment Method</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {data.payment_methods.filter((method) => method.is_active).map((method) => (
              <li key={method.id} style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'flex', alignItems: 'center' }}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value={method.id}
                    checked={selectedMethod?.id === method.id}
                    onChange={() => handleMethodChange(method)}
                  />
                  <img
                    src={method.icon}
                    alt={method.name}
                    style={{ width: '32px', height: '32px', marginLeft: '0.5rem', marginRight: '0.5rem' }}
                  />
                  {method.name}
                </label>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Payment Details Display */}
      <div className="payment-details" style={{ marginTop: '2rem' }}>
        <h2>Payment Details</h2>
        {selectedPlan && selectedMethod && paymentContext && (
          <div>
            <p>
              <strong>Plan:</strong> {selectedPlan.name}
            </p>
            <p>
              <strong>Payment Method:</strong> {selectedMethod.name}
            </p>
            <p>
              <strong>Amount:</strong> ${selectedPlan.price} {selectedPlan.currency}
            </p>
            <p>
              <strong>Payment Address:</strong> {paymentContext.payment_address}
            </p>
            <p>
              <strong>Native Crypto Amount:</strong> {paymentContext.crypto_amount}
            </p>
            <p>
              <strong>Transaction Status:</strong> {paymentContext.transaction_status}
            </p>
            <p>
              <strong>Expires At:</strong> {paymentContext.expires_at}
            </p>
            <p>
              <strong>QR Code:</strong>
            </p>
            {/* Placeholder for QR Code; integrate a QR code library as needed */}
            <div
              style={{
                width: '128px',
                height: '128px',
                backgroundColor: '#eee',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <span>QR Code</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentPage;
