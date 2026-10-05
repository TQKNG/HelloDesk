import type { ActionOutcome, Language } from "@hellodesk/shared/api-types";

import { getGuestStayMessages } from "./messages";

interface RoomConfirmationProps {
  language: Language;
  outcome: ActionOutcome;
}

export function RoomConfirmation({ language, outcome }: RoomConfirmationProps) {
  const messages = getGuestStayMessages(language);
  const roomNumber = outcome.result?.roomNumber;
  const roomBarcodePayload = outcome.result?.roomBarcodePayload;

  if (!roomNumber || !roomBarcodePayload) {
    return null;
  }

  return (
    <section className="success-card" aria-labelledby="room-confirmation-heading">
      <p className="eyebrow">{messages.checkIn}</p>
      <h2 id="room-confirmation-heading">{messages.room} {roomNumber}</h2>
      <p>{messages.checkInComplete}</p>
      <div className="barcode" aria-label={`Room barcode: ${roomBarcodePayload}`}>
        <span aria-hidden="true">▌▌ █ ▌██ ▌█ ▌▌█</span>
        <code>{roomBarcodePayload}</code>
      </div>
        <p className="muted-text">{messages.barcodeNote}</p>
    </section>
  );
}
