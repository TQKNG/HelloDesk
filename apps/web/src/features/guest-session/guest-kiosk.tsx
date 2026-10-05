"use client";

import { useMemo, useState } from "react";

import { ApiClient } from "@hellodesk/shared/api-client";
import type { GuestSession, Language } from "@hellodesk/shared/api-types";

import { GuestStayFlow } from "@/features/guest-stay/guest-stay-flow";

import { LanguagePicker } from "./language-picker";

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = configuredApiBaseUrl.endsWith("/api/v1")
  ? configuredApiBaseUrl
  : `${configuredApiBaseUrl.replace(/\/$/, "")}/api/v1`;

export function GuestKiosk() {
  const apiClient = useMemo(() => new ApiClient({ baseUrl: API_BASE_URL }), []);
  const [session, setSession] = useState<GuestSession>();
  const [isStarting, setIsStarting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  const startSession = async (language: Language) => {
    setIsStarting(true);
    setErrorMessage(undefined);
    try {
      setSession(await apiClient.createGuestSession({ language }));
    } catch {
      setErrorMessage("We could not start a guest session. Please try again.");
    } finally {
      setIsStarting(false);
    }
  };

  if (session) {
    return <GuestStayFlow apiClient={apiClient} initialSession={session} onEndSession={() => setSession(undefined)} />;
  }

  return <main><LanguagePicker isStarting={isStarting} errorMessage={errorMessage} onSelect={startSession} /></main>;
}
