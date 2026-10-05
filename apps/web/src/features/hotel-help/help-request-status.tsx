"use client";

import { useCallback, useEffect, useState } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { HelpRequest, Language } from "@hellodesk/shared/api-types";

interface HelpRequestStatusProps {
  apiClient: ApiClient;
  language: Language;
  requestId: string;
  sessionToken: string;
}

const STATUS_COPY: Record<Language, Record<HelpRequest["status"], string>> = {
  en: {
    pending: "Your request has been sent. A staff member has not acknowledged it yet.",
    acknowledged: "A staff member has acknowledged your request.",
  },
  vi: {
    pending: "Yêu cầu của bạn đã được gửi. Nhân viên chưa xác nhận yêu cầu này.",
    acknowledged: "Nhân viên đã xác nhận yêu cầu của bạn.",
  },
};

export function HelpRequestStatus({ apiClient, language, requestId, sessionToken }: HelpRequestStatusProps) {
  const [request, setRequest] = useState<HelpRequest>();
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string>();

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(undefined);
    try {
      setRequest(await apiClient.getGuestHelpRequest(sessionToken, requestId));
    } catch {
      setErrorMessage(language === "vi" ? "Không thể cập nhật trạng thái yêu cầu." : "We could not refresh your request status.");
    } finally {
      setIsLoading(false);
    }
  }, [apiClient, language, requestId, sessionToken]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  if (isLoading && !request) {
    return <p role="status">{language === "vi" ? "Đang kiểm tra yêu cầu…" : "Checking your request…"}</p>;
  }

  return (
    <section className="details-card" aria-labelledby="help-request-status-heading">
      <h2 id="help-request-status-heading">{language === "vi" ? "Trạng thái yêu cầu hỗ trợ" : "Help request status"}</h2>
      {request ? <p aria-live="polite">{STATUS_COPY[language][request.status]}</p> : null}
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
      <button type="button" className="secondary-button" disabled={isLoading} onClick={() => void refresh()}>
        {isLoading ? (language === "vi" ? "Đang cập nhật…" : "Refreshing…") : language === "vi" ? "Cập nhật trạng thái" : "Refresh status"}
      </button>
    </section>
  );
}
