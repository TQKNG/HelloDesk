import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { GuestSession } from "@hellodesk/shared/api-types";

import { GuestStayFlow } from "@/features/guest-stay/guest-stay-flow";
import { VoiceStatus } from "@/features/guest-session/voice-status";

const SESSION_WITHOUT_RESERVATION: GuestSession = {
  sessionToken: "guest-token",
  language: "en",
  expiresAt: "2026-10-04T19:00:00.000Z",
  status: "active",
};

describe("kiosk fallback controls", () => {
  it("makes microphone denial visible and keeps reservation code entry keyboard accessible", async () => {
    const lookUpReservation = vi.fn().mockResolvedValue({
      lookupId: "00000000-0000-4000-8000-000000000001",
      requiresConfirmation: true,
      reservation: {
        displayName: "Demo Guest",
        arrivalDate: "2026-10-04",
        departureDate: "2026-10-06",
        status: "reserved",
      },
    });
    render(
      <>
        <VoiceStatus status="microphone_denied" onStart={vi.fn()} />
        <GuestStayFlow
          apiClient={{ lookUpReservation } as unknown as ApiClient}
          initialSession={SESSION_WITHOUT_RESERVATION}
          onEndSession={vi.fn()}
        />
      </>,
    );

    expect(screen.getByText("Microphone permission is needed for voice service.")).toBeVisible();
    const reservationCode = screen.getByLabelText("Reservation code");
    reservationCode.focus();
    expect(reservationCode).toHaveFocus();
    fireEvent.change(reservationCode, { target: { value: "DEMO-402" } });
    fireEvent.submit(reservationCode.closest("form")!);
    await waitFor(() => {
      expect(lookUpReservation).toHaveBeenCalledWith("guest-token", { reservationCode: "DEMO-402" });
    });
  });

  it("keeps a visible cancellation control available before confirmation", async () => {
    const prepareGuestAction = vi.fn().mockResolvedValue({
      actionId: "00000000-0000-4000-8000-000000000001",
      kind: "check_in",
      summary: "Check in to room 402.",
      status: "pending",
      expiresAt: "2026-10-04T18:30:00.000Z",
    });
    render(
      <GuestStayFlow
        apiClient={{ prepareGuestAction } as unknown as ApiClient}
        initialSession={{
          ...SESSION_WITHOUT_RESERVATION,
          reservation: {
            displayName: "Demo Guest",
            arrivalDate: "2026-10-04",
            departureDate: "2026-10-06",
            status: "reserved",
          },
        }}
        onEndSession={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Check in" }));
    await screen.findByText("Check in to room 402.");
    expect(screen.getByRole("button", { name: "Cancel request" })).toBeVisible();
  });
});
