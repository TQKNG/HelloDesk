import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "@hellodesk/shared/api-client";

import { HelpRequestFlow } from "@/features/hotel-help/help-request-flow";
import { HotelQuestionPanel } from "@/features/hotel-help/hotel-question-panel";
import { StaffDashboard } from "@/features/staff/staff-dashboard";

const HELP_ACTION = {
  actionId: "00000000-0000-4000-8000-000000000010",
  kind: "staff_help" as const,
  summary: "Please bring extra towels.",
  status: "pending" as const,
  expiresAt: "2026-10-04T18:30:00.000Z",
};

describe("hotel help flow", () => {
  it("shows a localized answer for a supported hotel question", async () => {
    const apiClient = {
      answerHotelQuestion: vi.fn().mockResolvedValue({
        answer: "Bữa sáng được phục vụ từ 6:30 đến 10:00.",
        needsStaffHelp: false,
      }),
    } as unknown as ApiClient;
    render(
      <HotelQuestionPanel
        apiClient={apiClient}
        language="vi"
        sessionToken="guest-token"
        onRequestStaffHelp={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Câu hỏi của bạn"), { target: { value: "Bữa sáng lúc mấy giờ?" } });
    fireEvent.click(screen.getByRole("button", { name: "Hỏi lễ tân" }));

    await screen.findByText("Bữa sáng được phục vụ từ 6:30 đến 10:00.");
    expect(apiClient.answerHotelQuestion).toHaveBeenCalledWith("guest-token", { question: "Bữa sáng lúc mấy giờ?" });
  });

  it("offers staff help when a hotel question is unsupported", async () => {
    const onRequestStaffHelp = vi.fn();
    const apiClient = {
      answerHotelQuestion: vi.fn().mockResolvedValue({ answer: undefined, needsStaffHelp: true }),
    } as unknown as ApiClient;
    render(
      <HotelQuestionPanel
        apiClient={apiClient}
        language="en"
        sessionToken="guest-token"
        onRequestStaffHelp={onRequestStaffHelp}
      />,
    );

    fireEvent.change(screen.getByLabelText("Your question"), { target: { value: "Where is the pool?" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask receptionist" }));
    await screen.findByText("I do not have that information. Would you like staff help?");
    fireEvent.click(screen.getByRole("button", { name: "Request staff help" }));

    expect(onRequestStaffHelp).toHaveBeenCalledWith("Where is the pool?");
  });

  it("requires guest review and confirmation before a help request is submitted", async () => {
    const apiClient = {
      prepareGuestAction: vi.fn().mockResolvedValue(HELP_ACTION),
      cancelGuestAction: vi.fn().mockResolvedValue({ ...HELP_ACTION, status: "cancelled" }),
      confirmGuestAction: vi.fn(),
    } as unknown as ApiClient;
    render(<HelpRequestFlow apiClient={apiClient} language="en" sessionToken="guest-token" />);

    fireEvent.change(screen.getByLabelText("Your request"), { target: { value: "Please bring extra towels." } });
    fireEvent.click(screen.getByRole("button", { name: "Review request" }));
    await screen.findByText("Please bring extra towels.");

    expect(apiClient.confirmGuestAction).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Cancel request" }));
    await waitFor(() => expect(apiClient.cancelGuestAction).toHaveBeenCalledWith("guest-token", HELP_ACTION.actionId));
  });

  it("shows the guest when staff acknowledge a confirmed request", async () => {
    const apiClient = {
      prepareGuestAction: vi.fn().mockResolvedValue(HELP_ACTION),
      confirmGuestAction: vi.fn().mockResolvedValue({
        actionId: HELP_ACTION.actionId,
        status: "completed",
        message: "Help request sent.",
        result: { helpRequestId: "00000000-0000-4000-8000-000000000011" },
      }),
      getGuestHelpRequest: vi.fn().mockResolvedValue({
        id: "00000000-0000-4000-8000-000000000011",
        summary: "Please bring extra towels.",
        status: "acknowledged",
        createdAt: "2026-10-04T18:00:00.000Z",
      }),
    } as unknown as ApiClient;
    render(<HelpRequestFlow apiClient={apiClient} language="vi" sessionToken="guest-token" />);

    fireEvent.change(screen.getByLabelText("Yêu cầu của bạn"), { target: { value: "Khăn tắm" } });
    fireEvent.click(screen.getByRole("button", { name: "Xem lại yêu cầu" }));
    await screen.findByText("Please bring extra towels.");
    fireEvent.click(screen.getByRole("button", { name: "Gửi yêu cầu" }));

    await screen.findByText("Nhân viên đã xác nhận yêu cầu của bạn.");
  });

  it("lets local demo staff sign in and acknowledge a pending request", async () => {
    const pendingRequest = {
      id: "00000000-0000-4000-8000-000000000011",
      summary: "Please bring extra towels.",
      status: "pending" as const,
      createdAt: "2026-10-04T18:00:00.000Z",
    };
    const apiClient = {
      createStaffSession: vi.fn().mockResolvedValue({
        sessionToken: "staff-token",
        expiresAt: "2026-10-04T20:00:00.000Z",
      }),
      listStaffHelpRequests: vi.fn().mockResolvedValue([pendingRequest]),
      acknowledgeHelpRequest: vi.fn().mockResolvedValue({ ...pendingRequest, status: "acknowledged" }),
    } as unknown as ApiClient;
    render(<StaffDashboard apiClient={apiClient} />);

    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "admin" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "admin" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await screen.findByText("Please bring extra towels.");
    fireEvent.click(screen.getByRole("button", { name: "Acknowledge" }));

    await waitFor(() => expect(apiClient.acknowledgeHelpRequest).toHaveBeenCalledWith("staff-token", pendingRequest.id));
    expect(screen.getByText("Acknowledged")).toBeInTheDocument();
  });
});
