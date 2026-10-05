"use client";

import { useCallback, useEffect, useState } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { HelpRequest } from "@hellodesk/shared/api-types";

interface HelpRequestListProps {
  apiClient: ApiClient;
  sessionToken: string;
}

export function HelpRequestList({ apiClient, sessionToken }: HelpRequestListProps) {
  const [requests, setRequests] = useState<HelpRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAcknowledging, setIsAcknowledging] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(undefined);
    try {
      setRequests(await apiClient.listStaffHelpRequests(sessionToken));
    } catch {
      setErrorMessage("We could not load staff help requests.");
    } finally {
      setIsLoading(false);
    }
  }, [apiClient, sessionToken]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const acknowledge = async (requestId: string) => {
    setIsAcknowledging(requestId);
    setErrorMessage(undefined);
    try {
      const acknowledgedRequest = await apiClient.acknowledgeHelpRequest(sessionToken, requestId);
      setRequests((currentRequests) => currentRequests.map((request) => (
        request.id === requestId ? acknowledgedRequest : request
      )));
    } catch {
      setErrorMessage("We could not acknowledge this request.");
    } finally {
      setIsAcknowledging(undefined);
    }
  };

  return (
    <section className="kiosk-card staff-card" aria-labelledby="staff-help-requests-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Local demo staff view</p>
          <h1 id="staff-help-requests-heading">Guest help requests</h1>
        </div>
        <button type="button" className="secondary-button" disabled={isLoading} onClick={() => void refresh()}>
          {isLoading ? "Refreshing…" : "Refresh"}
        </button>
      </div>
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
      {!isLoading && requests.length === 0 ? <p>No help requests are waiting.</p> : null}
      <ul className="help-request-list" aria-live="polite">
        {requests.map((request) => (
          <li key={request.id}>
            <article>
              <div>
                <h2>{request.status === "pending" ? "Pending" : "Acknowledged"}</h2>
                <p>{request.summary}</p>
                <p className="muted-text">Requested {new Date(request.createdAt).toLocaleString()}</p>
              </div>
              {request.status === "pending" ? (
                <button
                  type="button"
                  disabled={isAcknowledging === request.id}
                  onClick={() => void acknowledge(request.id)}
                >
                  {isAcknowledging === request.id ? "Acknowledging…" : "Acknowledge"}
                </button>
              ) : null}
            </article>
          </li>
        ))}
      </ul>
    </section>
  );
}
