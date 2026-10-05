import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { GuestSession, PendingAction } from "@hellodesk/shared/api-types";

import { LanguagePicker } from "@/features/guest-session/language-picker";
import { GuestStayFlow } from "@/features/guest-stay/guest-stay-flow";

const CHECK_IN_ACTION: PendingAction = {
  actionId: "00000000-0000-4000-8000-000000000001",
  kind: "check_in",
  summary: "Check in to room 402.",
  status: "pending",
  expiresAt: "2026-10-04T18:30:00.000Z",
};

const RESERVED_SESSION: GuestSession = {
  sessionToken: "guest-token",
  language: "en",
  expiresAt: "2026-10-04T19:00:00.000Z",
  status: "active",
  reservation: {
    displayName: "Demo Guest",
    arrivalDate: "2026-10-04",
    departureDate: "2026-10-06",
    status: "reserved",
  },
};

function createApiClient(overrides: Partial<ApiClient> = {}): ApiClient {
  return {
    prepareGuestAction: vi.fn().mockResolvedValue(CHECK_IN_ACTION),
    cancelGuestAction: vi.fn().mockResolvedValue({ ...CHECK_IN_ACTION, status: "cancelled" }),
    confirmGuestAction: vi.fn().mockResolvedValue({
      actionId: CHECK_IN_ACTION.actionId,
      status: "completed",
      message: "You are checked in.",
      result: {
        roomNumber: "402",
        roomBarcodePayload: "demo-room-402",
      },
    }),
    ...overrides,
  } as unknown as ApiClient;
}

describe("guest stay journey", () => {
  it("starts only after the guest selects a language", () => {
    const onSelect = vi.fn();
    render(<LanguagePicker onSelect={onSelect} />);

    fireEvent.click(screen.getByRole("button", { name: /english/i }));

    expect(onSelect).toHaveBeenCalledWith("en");
  });

  it("preserves the bearer token after reservation confirmation", async () => {
    const reservation = {
      displayName: "Demo Guest",
      arrivalDate: "2026-10-04",
      departureDate: "2026-10-06",
      status: "reserved" as const,
    };
    const apiClient = createApiClient({
      lookUpReservation: vi.fn().mockResolvedValue({
        lookupId: "lookup-1",
        reservation,
        requiresConfirmation: true,
      }),
      confirmReservationLookup: vi.fn().mockResolvedValue({
        language: "en",
        expiresAt: "2026-10-04T19:00:00.000Z",
        status: "active",
      }),
    });
    render(
      <GuestStayFlow
        apiClient={apiClient}
        initialSession={{ ...RESERVED_SESSION, reservation: undefined }}
        onEndSession={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Reservation code"), { target: { value: "DEMO-402" } });
    fireEvent.click(screen.getByRole("button", { name: "Find reservation" }));
    await screen.findByText("Demo Guest");
    fireEvent.click(screen.getByRole("button", { name: "Confirm reservation details" }));

    await waitFor(() => expect(apiClient.confirmReservationLookup).toHaveBeenCalledWith("guest-token", "lookup-1"));
    fireEvent.click(screen.getByRole("button", { name: "Check in" }));
    await waitFor(() => expect(apiClient.prepareGuestAction).toHaveBeenCalledWith("guest-token", { kind: "check_in" }));
  });

  it("keeps check-in uncommitted until the guest confirms the exact action", async () => {
    const apiClient = createApiClient();
    render(<GuestStayFlow apiClient={apiClient} initialSession={RESERVED_SESSION} onEndSession={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Check in" }));
    await screen.findByText("Check in to room 402.");

    expect(apiClient.confirmGuestAction).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));

    await waitFor(() => expect(apiClient.confirmGuestAction).toHaveBeenCalledOnce());
    expect(screen.getByText("demo-room-402")).toBeInTheDocument();
    expect(screen.getByLabelText("Room barcode: demo-room-402")).toBeInTheDocument();
  });

  it("cancels the pending action without committing it", async () => {
    const apiClient = createApiClient();
    render(<GuestStayFlow apiClient={apiClient} initialSession={RESERVED_SESSION} onEndSession={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Check in" }));
    await screen.findByText("Check in to room 402.");
    fireEvent.click(screen.getByRole("button", { name: "Cancel request" }));

    await waitFor(() => expect(apiClient.cancelGuestAction).toHaveBeenCalledWith("guest-token", CHECK_IN_ACTION.actionId));
    expect(apiClient.confirmGuestAction).not.toHaveBeenCalled();
  });
});
