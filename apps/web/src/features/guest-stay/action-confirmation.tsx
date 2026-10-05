"use client";

import type { Language, PendingAction } from "@hellodesk/shared/api-types";
import type { GuestStayMessages } from "./messages";

interface ActionConfirmationProps {
  action: PendingAction;
  language: Language;
  messages: GuestStayMessages;
  confirmLabel?: string;
  cancelLabel?: string;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ActionConfirmation({
  action,
  language,
  messages,
  confirmLabel = messages.confirm,
  cancelLabel = messages.cancelAction,
  isSubmitting,
  onConfirm,
  onCancel,
}: ActionConfirmationProps) {
  const locale = language === "vi" ? "vi-VN" : "en-US";

  return (
    <section className="confirmation-card" aria-labelledby="action-confirmation-heading">
      <p className="eyebrow">{messages.reviewRequired}</p>
      <h2 id="action-confirmation-heading">{messages.confirmHeading}</h2>
      <p>{action.summary}</p>
      <p className="muted-text">
        {messages.expiration} {new Date(action.expiresAt).toLocaleTimeString(locale)}.
      </p>
      <div className="button-row">
        <button type="button" className="secondary-button" disabled={isSubmitting} onClick={onCancel}>
          {cancelLabel}
        </button>
        <button type="button" disabled={isSubmitting} onClick={onConfirm}>
          {isSubmitting ? messages.confirming : confirmLabel}
        </button>
      </div>
    </section>
  );
}
