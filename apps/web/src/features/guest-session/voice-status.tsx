"use client";

import type { Language } from "@hellodesk/shared/api-types";

import type { VoiceSessionStatus, VoiceTranscriptEntry } from "./use-voice-session";

const STATUS_MESSAGES: Record<VoiceSessionStatus, string> = {
  idle: "Voice service is ready when you are.",
  requesting_microphone: "Requesting microphone permission…",
  connecting: "Connecting to voice service…",
  connected: "Voice service is connected.",
  microphone_denied: "Microphone permission is needed for voice service.",
  unavailable: "Voice service is unavailable in this browser connection.",
  error: "Voice service could not connect.",
};

interface VoiceStatusProps {
  status: VoiceSessionStatus;
  language?: Language;
  transcript?: VoiceTranscriptEntry[];
  errorMessage?: string;
  onStart?: () => void;
  onStop?: () => void;
}

export function VoiceStatus({
  status,
  language = "en",
  transcript = [],
  errorMessage,
  onStart,
  onStop,
}: VoiceStatusProps) {
  const isConnecting = status === "requesting_microphone" || status === "connecting";
  const isConnected = status === "connected";
  const needsFallback = status === "microphone_denied" || status === "unavailable" || status === "error";
  const isVietnamese = language === "vi";
  const heading = isVietnamese ? "Hội thoại bằng giọng nói" : "Voice conversation";
  const guestLabel = isVietnamese ? "Bạn" : "You";
  const receptionistLabel = isVietnamese ? "Lễ tân" : "Receptionist";
  const startButtonLabel = isConnecting
    ? (isVietnamese ? "Đang kết nối…" : "Connecting…")
    : (isVietnamese ? "Bắt đầu giọng nói" : "Start voice service");
  const statusMessages: Record<VoiceSessionStatus, string> = isVietnamese
    ? {
        idle: "Dịch vụ giọng nói đã sẵn sàng.",
        requesting_microphone: "Đang yêu cầu quyền truy cập micrô…",
        connecting: "Đang kết nối dịch vụ giọng nói…",
        connected: "Đã kết nối dịch vụ giọng nói.",
        microphone_denied: "Cần quyền truy cập micrô để sử dụng giọng nói.",
        unavailable: "Trình duyệt này không hỗ trợ dịch vụ giọng nói.",
        error: "Không thể kết nối dịch vụ giọng nói.",
      }
    : STATUS_MESSAGES;

  return (
    <section aria-labelledby="voice-status-heading">
      <h2 id="voice-status-heading">{heading}</h2>
      <p aria-live="polite" role="status">
        {errorMessage ?? statusMessages[status]}
      </p>
      {needsFallback ? (
        <p className="muted-text">
          {isVietnamese
            ? "Bạn có thể nhập mã đặt phòng bằng các điều khiển trên kiosk."
            : "You can continue by entering a reservation code with the kiosk controls."}
        </p>
      ) : null}
      {transcript.length > 0 ? (
        <ol
          className="voice-transcript"
          aria-label={isVietnamese ? "Bản ghi hội thoại tạm thời" : "Live conversation transcript"}
          aria-live="polite"
          role="log"
        >
          {transcript.map((entry) => (
            <li key={entry.id}>
              <strong>{entry.role === "guest" ? guestLabel : receptionistLabel}:</strong> {entry.text}
            </li>
          ))}
        </ol>
      ) : null}
      {isConnected ? (
        <button type="button" onClick={onStop}>
          {isVietnamese ? "Dừng giọng nói" : "Stop voice service"}
        </button>
      ) : (
        <button type="button" disabled={isConnecting} onClick={onStart}>
          {startButtonLabel}
        </button>
      )}
    </section>
  );
}
