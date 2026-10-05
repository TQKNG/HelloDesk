"use client";

import { useCallback, useEffect, useRef, useState, type Dispatch, type MutableRefObject, type SetStateAction } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { Language } from "@hellodesk/shared/api-types";

export type VoiceSessionStatus =
  | "idle"
  | "requesting_microphone"
  | "connecting"
  | "connected"
  | "microphone_denied"
  | "unavailable"
  | "error";

export interface UseVoiceSessionOptions {
  apiClient: ApiClient;
  sessionToken?: string;
  language: Language;
}

export interface VoiceSession {
  status: VoiceSessionStatus;
  errorMessage?: string;
  transcript: VoiceTranscriptEntry[];
  start: () => Promise<void>;
  stop: () => void;
}

export interface VoiceTranscriptEntry {
  id: string;
  role: "guest" | "receptionist";
  text: string;
}

export function useVoiceSession({ apiClient, sessionToken, language }: UseVoiceSessionOptions): VoiceSession {
  const [status, setStatus] = useState<VoiceSessionStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string>();
  const [transcript, setTranscript] = useState<VoiceTranscriptEntry[]>([]);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const microphoneStreamRef = useRef<MediaStream | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const transcriptSequenceRef = useRef(0);

  const stop = useCallback(() => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.onconnectionstatechange = null;
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    dataChannelRef.current?.close();
    dataChannelRef.current = null;
    microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());
    microphoneStreamRef.current = null;
    remoteAudioRef.current?.remove();
    remoteAudioRef.current = null;
    setStatus("idle");
    setErrorMessage(undefined);
    setTranscript([]);
  }, []);

  const start = useCallback(async () => {
    if (!sessionToken) {
      setStatus("error");
      setErrorMessage(language === "vi" ? "Hãy bắt đầu phiên khách trước khi kết nối giọng nói." : "Start a guest session before connecting voice.");
      return;
    }
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setStatus("unavailable");
      setErrorMessage(language === "vi" ? "Cần kết nối an toàn và micrô để sử dụng giọng nói." : "Voice requires a secure browser connection with microphone support.");
      return;
    }

    stop();
    setStatus("requesting_microphone");

    try {
      const microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      microphoneStreamRef.current = microphoneStream;
      const peerConnection = new RTCPeerConnection();
      peerConnectionRef.current = peerConnection;
      const dataChannel = peerConnection.createDataChannel("oai-events");
      dataChannelRef.current = dataChannel;
      dataChannel.addEventListener("message", ({ data }: MessageEvent<string>) => {
        try {
          const event = JSON.parse(data) as { type?: unknown; delta?: unknown };
          if (typeof event.delta !== "string") {
            return;
          }
          if (event.type === "session.input_transcript.delta") {
            appendTranscript("guest", event.delta, setTranscript, transcriptSequenceRef);
          } else if (event.type === "session.output_transcript.delta") {
            appendTranscript("receptionist", event.delta, setTranscript, transcriptSequenceRef);
          }
        } catch {
          // Ignore malformed provider events without exposing payloads in logs or the UI.
        }
      });

      microphoneStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, microphoneStream);
      });
      peerConnection.ontrack = ({ streams }) => {
        if (!streams[0]) {
          return;
        }
        const remoteAudio = new Audio();
        remoteAudio.autoplay = true;
        remoteAudio.srcObject = streams[0];
        remoteAudioRef.current?.remove();
        remoteAudioRef.current = remoteAudio;
        void remoteAudio.play().catch(() => undefined);
      };
      peerConnection.onconnectionstatechange = () => {
        if (peerConnection.connectionState === "connected") {
          setStatus("connected");
        }
        if (["failed", "disconnected", "closed"].includes(peerConnection.connectionState)) {
          setStatus("error");
        setErrorMessage(language === "vi" ? "Kết nối giọng nói đã kết thúc. Hãy thử lại hoặc dùng các điều khiển trên kiosk." : "The voice connection ended. Please try again or use the kiosk controls.");
        }
      };

      setStatus("connecting");
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      await waitForIceGatheringComplete(peerConnection);
      const answerSdp = await apiClient.negotiateVoiceSession(sessionToken, offer.sdp ?? "");
      await peerConnection.setRemoteDescription({ type: "answer", sdp: answerSdp });
    } catch (error) {
      microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());
      microphoneStreamRef.current = null;
      if (peerConnectionRef.current) {
        peerConnectionRef.current.onconnectionstatechange = null;
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
      dataChannelRef.current?.close();
      dataChannelRef.current = null;

      if (error instanceof DOMException && error.name === "NotAllowedError") {
        setStatus("microphone_denied");
        setErrorMessage(language === "vi" ? "Bạn chưa cấp quyền micrô. Hãy dùng các điều khiển trên kiosk hoặc nhờ nhân viên trợ giúp." : "Microphone permission was denied. Use the kiosk controls or ask staff for help.");
        return;
      }
      setStatus("error");
      setErrorMessage(language === "vi" ? "Không thể khởi động dịch vụ giọng nói. Hãy thử lại hoặc dùng các điều khiển trên kiosk." : "We could not start voice service. Please try again or use the kiosk controls.");
    }
  }, [apiClient, language, sessionToken, stop]);

  useEffect(() => stop, [stop]);

  return { status, errorMessage, transcript, start, stop };
}

function appendTranscript(
  role: VoiceTranscriptEntry["role"],
  delta: string,
  setTranscript: Dispatch<SetStateAction<VoiceTranscriptEntry[]>>,
  sequenceRef: MutableRefObject<number>,
): void {
  setTranscript((entries) => {
    const lastEntry = entries.at(-1);
    if (lastEntry?.role === role) {
      return [...entries.slice(0, -1), { ...lastEntry, text: lastEntry.text + delta }];
    }
    sequenceRef.current += 1;
    return [...entries, { id: `voice-${sequenceRef.current}`, role, text: delta }];
  });
}

function waitForIceGatheringComplete(peerConnection: RTCPeerConnection): Promise<void> {
  if (peerConnection.iceGatheringState === "complete") {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const handleIceGatheringStateChange = () => {
      if (peerConnection.iceGatheringState !== "complete") {
        return;
      }
      peerConnection.removeEventListener("icegatheringstatechange", handleIceGatheringStateChange);
      resolve();
    };
    peerConnection.addEventListener("icegatheringstatechange", handleIceGatheringStateChange);
  });
}
