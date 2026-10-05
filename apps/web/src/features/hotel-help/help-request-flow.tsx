"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { Language, PendingAction } from "@hellodesk/shared/api-types";

import { ActionConfirmation } from "@/features/guest-stay/action-confirmation";
import { getGuestStayMessages } from "@/features/guest-stay/messages";

import { HelpRequestStatus } from "./help-request-status";

interface HelpRequestFlowProps {
  apiClient: ApiClient;
  language: Language;
  sessionToken: string;
  suggestedSummary?: string;
}

function createIdempotencyKey(): string {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function HelpRequestFlow({ apiClient, language, sessionToken, suggestedSummary }: HelpRequestFlowProps) {
  const [summary, setSummary] = useState("");
  const [action, setAction] = useState<PendingAction>();
  const [helpRequestId, setHelpRequestId] = useState<string>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const isVietnamese = language === "vi";
  const messages = getGuestStayMessages(language);
  const summaryInputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!suggestedSummary) {
      return;
    }
    setSummary(suggestedSummary);
    summaryInputRef.current?.focus();
  }, [suggestedSummary]);

  const runRequest = async (request: () => Promise<void>) => {
    setIsSubmitting(true);
    setErrorMessage(undefined);
    try {
      await request();
    } catch {
      setErrorMessage(isVietnamese ? "Không thể hoàn tất yêu cầu hỗ trợ." : "We could not complete your help request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const prepareRequest = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runRequest(async () => {
      setAction(await apiClient.prepareGuestAction(sessionToken, {
        kind: "staff_help",
        details: { summary },
      }));
    });
  };

  const cancelRequest = () => {
    if (!action) {
      return;
    }
    void runRequest(async () => {
      await apiClient.cancelGuestAction(sessionToken, action.actionId);
      setAction(undefined);
    });
  };

  const confirmRequest = () => {
    if (!action) {
      return;
    }
    void runRequest(async () => {
      const outcome = await apiClient.confirmGuestAction(sessionToken, action.actionId, createIdempotencyKey());
      const requestId = outcome.result?.helpRequestId;
      if (!requestId) {
        throw new Error("The help request outcome did not include its identifier.");
      }
      setHelpRequestId(requestId);
      setAction(undefined);
    });
  };

  if (helpRequestId) {
    return (
      <HelpRequestStatus
        apiClient={apiClient}
        language={language}
        requestId={helpRequestId}
        sessionToken={sessionToken}
      />
    );
  }

  return (
    <section className="details-card" aria-labelledby="staff-help-heading">
      <h2 id="staff-help-heading">{isVietnamese ? "Yêu cầu nhân viên hỗ trợ" : "Request staff help"}</h2>
      <p>{isVietnamese ? "Mô tả ngắn gọn nhu cầu của bạn để nhân viên có thể hỗ trợ." : "Describe what you need so hotel staff can help."}</p>
      <form onSubmit={prepareRequest}>
        <label htmlFor="help-summary">{isVietnamese ? "Yêu cầu của bạn" : "Your request"}</label>
        <textarea
          id="help-summary"
          ref={summaryInputRef}
          value={summary}
          maxLength={500}
          required
          onChange={(event) => setSummary(event.target.value)}
        />
        <button type="submit" disabled={isSubmitting}>{isVietnamese ? "Xem lại yêu cầu" : "Review request"}</button>
      </form>
      {action ? (
        <ActionConfirmation
          action={action}
          language={language}
          messages={messages}
          confirmLabel={isVietnamese ? "Gửi yêu cầu" : "Send request"}
          cancelLabel={isVietnamese ? "Hủy yêu cầu" : "Cancel request"}
          isSubmitting={isSubmitting}
          onConfirm={confirmRequest}
          onCancel={cancelRequest}
        />
      ) : null}
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
    </section>
  );
}
