import type { ActionOutcome, Language } from "@hellodesk/shared/api-types";

interface RideStatusProps {
  language: Language;
  outcome: ActionOutcome;
}

export function RideStatus({ language, outcome }: RideStatusProps) {
  const isVietnamese = language === "vi";
  const rideStatus = outcome.result?.rideStatus;
  const message = rideStatus === "unavailable"
    ? (isVietnamese ? "Dịch vụ Uber sandbox hiện không khả dụng." : "The Uber sandbox is currently unavailable.")
    : rideStatus === "failed"
      ? (isVietnamese ? "Yêu cầu xe mô phỏng không thành công." : "The simulated ride request did not complete.")
      : (isVietnamese ? "Yêu cầu xe này chỉ là mô phỏng. Không có tài xế thật nào được điều phối." : "This ride request is simulated. No live driver has been dispatched.");

  return (
    <section className="success-card" aria-labelledby="ride-status-heading" aria-live="polite">
      <p className="eyebrow">{isVietnamese ? "Chuyến xe mô phỏng" : "Simulated ride"}</p>
      <h2 id="ride-status-heading">{isVietnamese ? "Cập nhật yêu cầu xe" : "Ride request update"}</h2>
      <p>{message}</p>
    </section>
  );
}
