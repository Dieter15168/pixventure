// src/app/payment/page.tsx

"use client";

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { Container, Row, Col, Card, Button, Accordion } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSync, faCopy, faExternalLinkAlt, faCheck } from '@fortawesome/free-solid-svg-icons';
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
 * Implements a modern UI for selecting membership plans, payment methods,
 * and displaying the updated payment context using React Bootstrap and Font Awesome.
 */
const PaymentPage: React.FC = () => {
  const { fetchPaymentSetup, updatePaymentContext } = usePaymentAPI();
  const { data, error, mutate } = useSWR<PaymentSetupResponse>('paymentSetup', () => fetchPaymentSetup());

  // Local state for selected membership plan, payment method, and payment context.
  const [selectedPlan, setSelectedPlan] = useState<MembershipPlan | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod | null>(null);
  const [paymentContext, setPaymentContext] = useState<PaymentContext | null>(null);

  useEffect(() => {
    if (data) {
      setSelectedPlan(data.default_selected.membership_plan);
      setSelectedMethod(data.default_selected.payment_method);
      setPaymentContext(data.default_selected.payment_context);
    }
  }, [data]);

  // When the user selects a different membership plan.
  const handlePlanChange = async (plan: MembershipPlan) => {
    setSelectedPlan(plan);
    if (selectedMethod) {
      try {
        const res = await updatePaymentContext(plan.id, selectedMethod.id);
        setPaymentContext(res.payment_context);
      } catch (err) {
        console.error("Error updating payment context", err);
      }
    }
  };

  // When the user selects a different payment method.
  const handleMethodChange = async (method: PaymentMethod) => {
    setSelectedMethod(method);
    if (selectedPlan) {
      try {
        const res = await updatePaymentContext(selectedPlan.id, method.id);
        setPaymentContext(res.payment_context);
      } catch (err) {
        console.error("Error updating payment context", err);
      }
    }
  };

  // Manual refresh triggers SWR revalidation.
  const handleManualRefresh = async () => {
    await mutate();
  };

  if (error) return <Container><p>Error loading payment setup data.</p></Container>;
  if (!data) return <Container><p>Loading...</p></Container>;

  return (
    <Container className="my-4">
      <h1 className="mb-4 text-center">Become a Member</h1>

      {/* FAQ Accordion */}
      <Accordion defaultActiveKey="0" className="mb-4">
        <Accordion.Item eventKey="0">
          <Accordion.Header>
            <strong>FAQ:</strong> Will I be charged automatically for the next period?
          </Accordion.Header>
          <Accordion.Body>
            No, you will not be charged automatically. Our service does not use recurring payments.
            Your membership will expire at the end of the period. To continue your membership,
            simply make a separate payment for the next month or year.
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>

      {/* Membership Plan Selection */}
      <h4 className="text-center mb-3">1. Select Membership Plan</h4>
      <Row className="mb-4">
        {data.membership_plans.map((plan) => (
          <Col md={6} key={plan.id} className="mb-3">
            <Card 
              className={selectedPlan?.id === plan.id ? "border-danger" : ""}
              onClick={() => handlePlanChange(plan)}
              style={{ cursor: 'pointer' }}
            >
              <Card.Body className="text-center">
                <Card.Title className="text-uppercase text-muted">{plan.name}</Card.Title>
                <Card.Text>
                  <span style={{ fontSize: '1.5rem' }}>
                    ${plan.price} <small className="text-muted">/{plan.duration_days} days</small>
                  </span>
                </Card.Text>
                <Button 
                  variant={selectedPlan?.id === plan.id ? "danger" : "primary"} 
                  disabled={selectedPlan?.id === plan.id}
                >
                  {selectedPlan?.id === plan.id ? "Selected" : "Select"}
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Payment Method Selection */}
      <h4 className="text-center mb-3">2. Select Payment Method</h4>
      <Row className="mb-4 justify-content-center">
        {data.payment_methods.filter(method => method.is_active).map((method) => (
          <Col key={method.id} xs="auto" className="text-center">
            <div onClick={() => handleMethodChange(method)} style={{ cursor: 'pointer' }}>
              <img 
                src={method.icon}
                alt={method.name}
                style={{
                  width: '80px',
                  border: selectedMethod?.id === method.id ? "2px solid hotpink" : "none",
                  borderRadius: "8px",
                  padding: "2px",
                  margin: "2px",
                }}
              />
              <div>{method.name}</div>
            </div>
          </Col>
        ))}
      </Row>

      {/* Payment Details Card */}
      {selectedPlan && selectedMethod && paymentContext && (
        <Card bg="dark" text="light" className="mb-4">
          <Card.Header className="d-flex justify-content-between align-items-center">
            <span>Payment Details</span>
            <Button variant="secondary" size="sm" onClick={handleManualRefresh}>
              <FontAwesomeIcon icon={faSync} />
            </Button>
          </Card.Header>
          <Card.Body className="text-center">
            <div>
              <img 
                src={`https://quickchart.io/qr?text=${encodeURIComponent(paymentContext.wallet_url)}`} 
                alt="QR Code"
                style={{ width: '200px', height: '200px' }}
              />
            </div>
            <div className="mt-3" style={{ fontSize: '1.75rem' }}>
              {paymentContext.crypto_amount} <small className="text-muted">{selectedMethod.name}</small>
            </div>
            {/* Display plain text crypto address */}
            <div className="mt-3">
              <strong>Crypto Address:</strong>
              <div style={{ wordBreak: 'break-all' }}>
                {paymentContext.payment_address}
              </div>
            </div>
            <div className="d-flex justify-content-center mt-3">
              <Button variant="outline-light" className="me-2" onClick={() => navigator.clipboard.writeText(paymentContext.payment_address)}>
                <FontAwesomeIcon icon={faCopy} /> Copy Address
              </Button>
              <Button variant="outline-light" onClick={() => window.open(paymentContext.wallet_url, "_blank")}>
                <FontAwesomeIcon icon={faExternalLinkAlt} /> Open Wallet
              </Button>
            </div>
            <div className="mt-3">
              {paymentContext.transaction_status.toLowerCase().includes("completed") ? (
                <Button variant="success" disabled>
                  <FontAwesomeIcon icon={faCheck} /> Payment Confirmed
                </Button>
              ) : (
                <Button variant="primary" disabled>
                  Awaiting Payment
                </Button>
              )}
            </div>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
};

export default PaymentPage;
