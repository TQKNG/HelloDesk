"use client";

import { useState, type FormEvent } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type {
  ActionOutcome,
  ActionKind,
  Bill,
  GuestSession,
  PendingAction,
  ReservationLookup,
} from "@hellodesk/shared/api-types";

import { VoiceStatus } from "@/features/guest-session/voice-status";
import { useVoiceSession } from "@/features/guest-session/use-voice-session";
import { HelpRequestFlow } from "@/features/hotel-help/help-request-flow";
import { HotelQuestionPanel } from "@/features/hotel-help/hotel-question-panel";
import { RideRequestFlow } from "@/features/ride-request/ride-request-flow";

import { ActionConfirmation } from "./action-confirmation";
import { BillReview } from "./bill-review";
import { getGuestStayMessages } from "./messages";
import { RoomConfirmation } from "./room-confirmation";

interface GuestStayFlowProps {
  apiClient: ApiClient;
  initialSession: GuestSession;
  onEndSession: () => void;
}

function createIdempotencyKey(): string {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function GuestStayFlow({ apiClient, initialSession, onEndSession }: GuestStayFlowProps) {
  const [session, setSession] = useState(initialSession);
  const [reservationCode, setReservationCode] = useState("");
  const [lookup, setLookup] = useState<ReservationLookup>();
  const [pendingAction, setPendingAction] = useState<PendingAction>();
  const [bill, setBill] = useState<Bill>();
  const [outcome, setOutcome] = useState<ActionOutcome>();
  const [completedActionKind, setCompletedActionKind] = useState<ActionKind>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [helpSuggestion, setHelpSuggestion] = useState<string>();
  const voiceSession = useVoiceSession({ apiClient, sessionToken: session.sessionToken, language: session.language });
  const messages = getGuestStayMessages(session.language);

  const runRequest = async (request: () => Promise<void>) => {
    setIsSubmitting(true);
      setErrorMessage(undefined);
    try {
      await request();
    } catch {
      setErrorMessage(session.language === "vi"
        ? "Không thể hoàn tất yêu cầu. Vui lòng kiểm tra thông tin và thử lại."
        : "We could not complete that request. Please check the details and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLookup = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runRequest(async () => {
      const nextLookup = await apiClient.lookUpReservation(session.sessionToken, { reservationCode });
      setLookup(nextLookup);
      setBill(undefined);
      setOutcome(undefined);
    });
  };

  const confirmReservation = () => {
    if (!lookup) {
      return;
    }
    void runRequest(async () => {
      const nextSession = await apiClient.confirmReservationLookup(session.sessionToken, lookup.lookupId);
      setSession((currentSession) => ({
        ...currentSession,
        ...nextSession,
        reservation: lookup.reservation,
      }));
      setLookup(undefined);
    });
  };

  const prepareAction = (kind: "check_in" | "check_out") => {
    void runRequest(async () => {
      const action = await apiClient.prepareGuestAction(session.sessionToken, { kind });
      setPendingAction(action);
    });
  };

  const loadBill = () => {
    void runRequest(async () => {
      const nextBill = await apiClient.getGuestBill(session.sessionToken);
      setBill(nextBill);
      setOutcome(undefined);
    });
  };

  const cancelAction = () => {
    if (!pendingAction) {
      return;
    }
    void runRequest(async () => {
      await apiClient.cancelGuestAction(session.sessionToken, pendingAction.actionId);
      setPendingAction(undefined);
    });
  };

  const confirmAction = () => {
    if (!pendingAction) {
      return;
    }
    void runRequest(async () => {
      const nextOutcome = await apiClient.confirmGuestAction(
        session.sessionToken,
        pendingAction.actionId,
        createIdempotencyKey(),
      );
      setOutcome(nextOutcome);
      setCompletedActionKind(pendingAction.kind);
      setPendingAction(undefined);
      if (nextOutcome.status === "completed") {
        if (pendingAction.kind === "check_in") {
          setSession((currentSession) => ({
            ...currentSession,
            reservation: currentSession.reservation
              ? { ...currentSession.reservation, status: "checked_in" }
              : currentSession.reservation,
          }));
        }
        if (pendingAction.kind === "check_out") {
          setSession((currentSession) => ({
            ...currentSession,
            reservation: currentSession.reservation
              ? { ...currentSession.reservation, status: "checked_out" }
              : currentSession.reservation,
          }));
          if (bill) {
            setBill({ ...bill, status: "closed" });
          }
        }
      }
    });
  };

  const reservation = lookup?.reservation ?? session.reservation;
  const canCheckIn = reservation?.status === "reserved";
  const canCheckOut = reservation?.status === "checked_in";
  const outcomeMessage = outcome?.status === "completed" && completedActionKind === "check_out"
    ? messages.checkoutComplete
    : outcome?.status === "completed" && completedActionKind === "check_in"
      ? messages.checkInComplete
      : outcome?.message;

  return (
    <main>
      <section className="kiosk-card" aria-labelledby="guest-stay-heading" lang={session.language}>
        <div className="section-heading">
          <div>
            <p className="eyebrow">{session.language === "vi" ? "Tiếng Việt" : "English"}</p>
            <h1 id="guest-stay-heading">{messages.welcome}</h1>
          </div>
          <button className="text-button" type="button" onClick={onEndSession}>{messages.endSession}</button>
        </div>

        <VoiceStatus
          status={voiceSession.status}
          language={session.language}
          transcript={voiceSession.transcript}
          errorMessage={voiceSession.errorMessage}
          onStart={() => void voiceSession.start()}
          onStop={voiceSession.stop}
        />

        {!reservation && !lookup ? (
          <form className="reservation-form" onSubmit={handleLookup}>
            <label htmlFor="reservation-code">{messages.reservationCode}</label>
            <div className="form-row">
              <input
                id="reservation-code"
                value={reservationCode}
                minLength={4}
                maxLength={32}
                required
                onChange={(event) => setReservationCode(event.target.value)}
              />
              <button type="submit" disabled={isSubmitting}>{messages.lookup}</button>
            </div>
          </form>
        ) : null}

        {lookup ? (
          <section className="details-card" aria-labelledby="reservation-details-heading">
            <h2 id="reservation-details-heading">{messages.reservationDetails}</h2>
            <dl>
              <div><dt>{messages.guest}</dt><dd>{lookup.reservation.displayName}</dd></div>
              <div><dt>{messages.arrival}</dt><dd>{lookup.reservation.arrivalDate}</dd></div>
              <div><dt>{messages.departure}</dt><dd>{lookup.reservation.departureDate}</dd></div>
            </dl>
            <div className="button-row">
              <button type="button" className="secondary-button" onClick={() => setLookup(undefined)}>
                {messages.cancel}
              </button>
              <button type="button" disabled={isSubmitting} onClick={confirmReservation}>
                {messages.confirmReservation}
              </button>
            </div>
          </section>
        ) : null}

        {session.reservation ? (
          <section className="stay-actions" aria-label="Stay actions">
            <p>{messages.stayReady}</p>
            {canCheckIn ? (
              <button type="button" disabled={isSubmitting || Boolean(pendingAction)} onClick={() => prepareAction("check_in")}>
                {messages.checkIn}
              </button>
            ) : null}
            {canCheckOut ? (
              <button type="button" disabled={isSubmitting || Boolean(pendingAction)} onClick={loadBill}>
                {messages.bill}
              </button>
            ) : null}
          </section>
        ) : null}

        {bill ? (
          <BillReview
            bill={bill}
            language={session.language}
            isPreparing={isSubmitting || Boolean(pendingAction)}
            onPrepareCheckout={() => prepareAction("check_out")}
          />
        ) : null}

        {pendingAction ? (
          <ActionConfirmation
            action={pendingAction}
            language={session.language}
            messages={messages}
            isSubmitting={isSubmitting}
            onConfirm={confirmAction}
            onCancel={cancelAction}
          />
        ) : null}

        {outcome ? (
          <section className="success-card" aria-live="polite">
            <h2>{outcome.status === "completed" ? messages.requestComplete : messages.requestUpdate}</h2>
            <p>{outcomeMessage}</p>
          </section>
        ) : null}
        {outcome ? <RoomConfirmation language={session.language} outcome={outcome} /> : null}
        <HotelQuestionPanel
          apiClient={apiClient}
          language={session.language}
          sessionToken={session.sessionToken}
          onRequestStaffHelp={setHelpSuggestion}
        />
        <HelpRequestFlow
          apiClient={apiClient}
          language={session.language}
          sessionToken={session.sessionToken}
          suggestedSummary={helpSuggestion}
        />
        <RideRequestFlow
          apiClient={apiClient}
          language={session.language}
          sessionToken={session.sessionToken}
        />
        {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
      </section>
    </main>
  );
}
