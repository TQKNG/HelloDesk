import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "@hellodesk/shared/api-client";

import { RideRequestFlow } from "@/features/ride-request/ride-request-flow";

const RIDE_ACTION = {
  actionId: "00000000-0000-4000-8000-000000000020",
  kind: "uber_ride" as const,
  summary: "Request a simulated ride to Union Square, San Francisco.",
  status: "pending" as const,
  expiresAt: "2026-10-04T18:30:00.000Z",
};

describe("ride request flow", () => {
  it("reviews exact destination details and can be cancelled without confirmation", async () => {
    const apiClient = {
      prepareGuestAction: vi.fn().mockResolvedValue(RIDE_ACTION),
      cancelGuestAction: vi.fn().mockResolvedValue({ ...RIDE_ACTION, status: "cancelled" }),
      confirmGuestAction: vi.fn(),
    } as unknown as ApiClient;
    render(<RideRequestFlow apiClient={apiClient} language="en" sessionToken="guest-token" />);

    fireEvent.change(screen.getByLabelText("Destination"), { target: { value: "demo-union-square" } });
    fireEvent.click(screen.getByRole("button", { name: "Review ride request" }));
    await screen.findByText("Request a simulated ride to Union Square, San Francisco.");

    expect(apiClient.confirmGuestAction).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Cancel ride request" }));
    await waitFor(() => expect(apiClient.cancelGuestAction).toHaveBeenCalledWith("guest-token", RIDE_ACTION.actionId));
  });

  it("labels every confirmed outcome as simulated", async () => {
    const apiClient = {
      prepareGuestAction: vi.fn().mockResolvedValue(RIDE_ACTION),
      confirmGuestAction: vi.fn().mockResolvedValue({
        actionId: RIDE_ACTION.actionId,
        status: "simulated",
        message: "Ride requested.",
        result: { rideStatus: "simulated" },
      }),
    } as unknown as ApiClient;
    render(<RideRequestFlow apiClient={apiClient} language="en" sessionToken="guest-token" />);

    fireEvent.change(screen.getByLabelText("Destination"), { target: { value: "demo-union-square" } });
    fireEvent.click(screen.getByRole("button", { name: "Review ride request" }));
    await screen.findByText("Request a simulated ride to Union Square, San Francisco.");
    fireEvent.click(screen.getByRole("button", { name: "Confirm simulated ride" }));

    await screen.findByText("This ride request is simulated. No live driver has been dispatched.");
    expect(apiClient.confirmGuestAction).toHaveBeenCalledOnce();
  });
});
