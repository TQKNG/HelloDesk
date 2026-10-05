"use client";

import { useState, type FormEvent } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { ActionOutcome, Language, PendingAction } from "@hellodesk/shared/api-types";

import { ActionConfirmation } from "@/features/guest-stay/action-confirmation";
import { getGuestStayMessages } from "@/features/guest-stay/messages";

import { RideStatus } from "./ride-status";

const DEMO_DESTINATIONS = [
  { id: "demo-union-square", en: "Union Square, San Francisco", vi: "Quảng trường Union, San Francisco" },
  { id: "demo-ferry-building", en: "Ferry Building, San Francisco", vi: "Ferry Building, San Francisco" },
] as const;

interface RideRequestFlowProps {
  apiClient: ApiClient;
  language: Language;
  sessionToken: string;
}

function createIdempotencyKey(): string {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function RideRequestFlow({ apiClient, language, sessionToken }: RideRequestFlowProps) {
  const [destinationId, setDestinationId] = useState("");
  const [action, setAction] = useState<PendingAction>();
  const [outcome, setOutcome] = useState<ActionOutcome>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const isVietnamese = language === "vi";
  const messages = getGuestStayMessages(language);

  const runRequest = async (request: () => Promise<void>) => {
    setIsSubmitting(true);
    setErrorMessage(undefined);
    try {
      await request();
    } catch {
      setErrorMessage(isVietnamese ? "Không thể hoàn tất yêu cầu xe mô phỏng." : "We could not complete the simulated ride request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const prepareRide = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const destination = DEMO_DESTINATIONS.find((item) => item.id === destinationId);
    if (!destination) {
      return;
    }
    void runRequest(async () => {
      setAction(await apiClient.prepareGuestAction(sessionToken, {
        kind: "uber_ride",
        details: {
          destinationId,
          summary: isVietnamese
            ? `Yêu cầu chuyến xe mô phỏng đến ${destination.vi}.`
            : `Request a simulated ride to ${destination.en}.`,
        },
      }));
    });
  };

  const cancelRide = () => {
    if (!action) {
      return;
    }
    void runRequest(async () => {
      await apiClient.cancelGuestAction(sessionToken, action.actionId);
      setAction(undefined);
    });
  };

  const confirmRide = () => {
    if (!action) {
      return;
    }
    void runRequest(async () => {
      setOutcome(await apiClient.confirmGuestAction(sessionToken, action.actionId, createIdempotencyKey()));
      setAction(undefined);
    });
  };

  return (
    <section className="details-card" aria-labelledby="ride-request-heading">
      <h2 id="ride-request-heading">{isVietnamese ? "Yêu cầu xe" : "Request a ride"}</h2>
      <p>{isVietnamese ? "Chọn một điểm đến để xem lại yêu cầu xe mô phỏng." : "Select a destination to review a simulated ride request."}</p>
      <form onSubmit={prepareRide}>
        <label htmlFor="ride-destination">{isVietnamese ? "Điểm đến" : "Destination"}</label>
        <select id="ride-destination" value={destinationId} required onChange={(event) => setDestinationId(event.target.value)}>
          <option value="">{isVietnamese ? "Chọn điểm đến" : "Choose a destination"}</option>
          {DEMO_DESTINATIONS.map((destination) => (
            <option key={destination.id} value={destination.id}>{destination[language]}</option>
          ))}
        </select>
        <button type="submit" disabled={isSubmitting}>{isVietnamese ? "Xem lại yêu cầu xe" : "Review ride request"}</button>
      </form>
      {action ? (
        <ActionConfirmation
          action={action}
          language={language}
          messages={messages}
          confirmLabel={isVietnamese ? "Xác nhận chuyến xe mô phỏng" : "Confirm simulated ride"}
          cancelLabel={isVietnamese ? "Hủy yêu cầu xe" : "Cancel ride request"}
          isSubmitting={isSubmitting}
          onConfirm={confirmRide}
          onCancel={cancelRide}
        />
      ) : null}
      {outcome ? <RideStatus language={language} outcome={outcome} /> : null}
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
    </section>
  );
}
