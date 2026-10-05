"use client";

import { useMemo, useState, type FormEvent } from "react";

import { ApiClient } from "@hellodesk/shared/api-client";
import type { StaffSession } from "@hellodesk/shared/api-types";

import { HelpRequestList } from "./help-request-list";

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = configuredApiBaseUrl.endsWith("/api/v1")
  ? configuredApiBaseUrl
  : `${configuredApiBaseUrl.replace(/\/$/, "")}/api/v1`;

interface StaffDashboardProps {
  apiClient?: ApiClient;
}

export function StaffDashboard({ apiClient: providedApiClient }: StaffDashboardProps) {
  const defaultApiClient = useMemo(() => new ApiClient({ baseUrl: API_BASE_URL }), []);
  const apiClient = providedApiClient ?? defaultApiClient;
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [staffSession, setStaffSession] = useState<StaffSession>();
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  const signIn = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void (async () => {
      setIsSigningIn(true);
      setErrorMessage(undefined);
      try {
        setStaffSession(await apiClient.createStaffSession({ username, password }));
        setPassword("");
      } catch {
        setErrorMessage("Sign-in failed. Check the local demo credentials and try again.");
      } finally {
        setIsSigningIn(false);
      }
    })();
  };

  if (staffSession) {
    return (
      <main>
        <HelpRequestList apiClient={apiClient} sessionToken={staffSession.sessionToken} />
      </main>
    );
  }

  return (
    <main>
      <section className="kiosk-card" aria-labelledby="staff-sign-in-heading">
        <p className="eyebrow">HelloDesk</p>
        <h1 id="staff-sign-in-heading">Staff sign in</h1>
        <p>Use local demo credentials only.</p>
        <form className="staff-sign-in-form" onSubmit={signIn}>
          <label htmlFor="staff-username">Username</label>
          <input id="staff-username" value={username} required onChange={(event) => setUsername(event.target.value)} />
          <label htmlFor="staff-password">Password</label>
          <input id="staff-password" type="password" value={password} required onChange={(event) => setPassword(event.target.value)} />
          <button type="submit" disabled={isSigningIn}>{isSigningIn ? "Signing in…" : "Sign in"}</button>
        </form>
        {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
      </section>
    </main>
  );
}
