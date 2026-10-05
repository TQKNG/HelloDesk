"use client";

import { useState, type FormEvent } from "react";

import type { ApiClient } from "@hellodesk/shared/api-client";
import type { HotelQuestionResponse, Language } from "@hellodesk/shared/api-types";

interface HotelQuestionPanelProps {
  apiClient: ApiClient;
  language: Language;
  sessionToken: string;
  onRequestStaffHelp: (suggestedSummary: string) => void;
}

export function HotelQuestionPanel({
  apiClient,
  language,
  sessionToken,
  onRequestStaffHelp,
}: HotelQuestionPanelProps) {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<HotelQuestionResponse>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const isVietnamese = language === "vi";

  const askQuestion = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void (async () => {
      setIsSubmitting(true);
      setErrorMessage(undefined);
      try {
        setResponse(await apiClient.answerHotelQuestion(sessionToken, { question }));
      } catch {
        setErrorMessage(isVietnamese ? "Không thể trả lời câu hỏi này ngay bây giờ." : "We could not answer that question right now.");
      } finally {
        setIsSubmitting(false);
      }
    })();
  };

  return (
    <section className="details-card" aria-labelledby="hotel-question-heading">
      <h2 id="hotel-question-heading">{isVietnamese ? "Hỏi về khách sạn" : "Ask about the hotel"}</h2>
      <p>{isVietnamese ? "Hỏi về các dịch vụ và thông tin khách sạn." : "Ask about hotel services and information."}</p>
      <form onSubmit={askQuestion}>
        <label htmlFor="hotel-question">{isVietnamese ? "Câu hỏi của bạn" : "Your question"}</label>
        <textarea
          id="hotel-question"
          value={question}
          maxLength={500}
          required
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (isVietnamese ? "Đang hỏi…" : "Asking…") : isVietnamese ? "Hỏi lễ tân" : "Ask receptionist"}
        </button>
      </form>
      {response?.answer ? (
        <div className="hotel-answer" aria-live="polite">
          <h3>{isVietnamese ? "Trả lời" : "Answer"}</h3>
          <p>{response.answer}</p>
        </div>
      ) : null}
      {response?.needsStaffHelp ? (
        <div className="hotel-answer" aria-live="polite">
          <p>{isVietnamese ? "Tôi không có thông tin đó. Bạn có muốn nhờ nhân viên hỗ trợ không?" : "I do not have that information. Would you like staff help?"}</p>
          <button type="button" className="secondary-button" onClick={() => onRequestStaffHelp(question)}>
            {isVietnamese ? "Yêu cầu nhân viên hỗ trợ" : "Request staff help"}
          </button>
        </div>
      ) : null}
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
    </section>
  );
}
