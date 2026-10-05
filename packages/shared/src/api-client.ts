import type {
  ActionOutcome,
  Bill,
  ConfirmActionRequest,
  CreateGuestSessionRequest,
  CreateStaffSessionRequest,
  ErrorResponse,
  GuestSession,
  GuestSessionState,
  HelpRequest,
  HelpRequestStatus,
  HotelQuestionRequest,
  HotelQuestionResponse,
  PendingAction,
  PrepareActionRequest,
  ReservationLookup,
  ReservationLookupRequest,
  StaffSession,
} from "./api-types";

export class ApiClientError extends Error {
  public readonly status: number;
  public readonly code?: string;

  public constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
  }
}

export interface ApiClientOptions {
  baseUrl: string;
  fetch?: typeof fetch;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  public constructor({ baseUrl, fetch: fetchImpl = globalThis.fetch }: ApiClientOptions) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.fetchImpl = fetchImpl;
  }

  public createGuestSession(request: CreateGuestSessionRequest): Promise<GuestSession> {
    return this.request("/guest/sessions", { method: "POST", body: request });
  }

  public lookUpReservation(
    sessionToken: string,
    request: ReservationLookupRequest,
  ): Promise<ReservationLookup> {
    return this.request("/guest/reservation-lookups", {
      method: "POST",
      sessionToken,
      body: request,
    });
  }

  public confirmReservationLookup(sessionToken: string, lookupId: string): Promise<GuestSessionState> {
    return this.request(`/guest/reservation-lookups/${encodeURIComponent(lookupId)}/confirm`, {
      method: "POST",
      sessionToken,
    });
  }

  public getGuestBill(sessionToken: string): Promise<Bill> {
    return this.request("/guest/bill", { sessionToken });
  }

  public prepareGuestAction(
    sessionToken: string,
    request: PrepareActionRequest,
  ): Promise<PendingAction> {
    return this.request("/guest/actions", { method: "POST", sessionToken, body: request });
  }

  public confirmGuestAction(
    sessionToken: string,
    actionId: string,
    idempotencyKey: string,
    request: ConfirmActionRequest = { confirmed: true },
  ): Promise<ActionOutcome> {
    return this.request(`/guest/actions/${encodeURIComponent(actionId)}/confirm`, {
      method: "POST",
      sessionToken,
      headers: { "Idempotency-Key": idempotencyKey },
      body: request,
    });
  }

  public cancelGuestAction(sessionToken: string, actionId: string): Promise<PendingAction> {
    return this.request(`/guest/actions/${encodeURIComponent(actionId)}/cancel`, {
      method: "POST",
      sessionToken,
    });
  }

  public getGuestHelpRequest(sessionToken: string, requestId: string): Promise<HelpRequest> {
    return this.request(`/guest/help-requests/${encodeURIComponent(requestId)}`, { sessionToken });
  }

  public answerHotelQuestion(
    sessionToken: string,
    request: HotelQuestionRequest,
  ): Promise<HotelQuestionResponse> {
    return this.request("/guest/hotel-questions", { method: "POST", sessionToken, body: request });
  }

  public createStaffSession(request: CreateStaffSessionRequest): Promise<StaffSession> {
    return this.request("/staff/sessions", { method: "POST", body: request });
  }

  public listStaffHelpRequests(
    sessionToken: string,
    status?: HelpRequestStatus,
  ): Promise<HelpRequest[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.request(`/staff/help-requests${query}`, { sessionToken });
  }

  public acknowledgeHelpRequest(sessionToken: string, requestId: string): Promise<HelpRequest> {
    return this.request(
      `/staff/help-requests/${encodeURIComponent(requestId)}/acknowledgement`,
      { method: "PUT", sessionToken },
    );
  }

  public negotiateVoiceSession(sessionToken: string, offerSdp: string): Promise<string> {
    return this.requestText("/guest/voice/sdp", {
      method: "POST",
      sessionToken,
      headers: { Accept: "application/sdp", "Content-Type": "application/sdp" },
      body: offerSdp,
    });
  }

  private async request<T>(
    path: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const response = await this.fetchResponse(path, options);
    if (!response.ok) {
      throw await this.createError(response);
    }
    return (await response.json()) as T;
  }

  private async requestText(path: string, options: RequestOptions): Promise<string> {
    const response = await this.fetchResponse(path, options);
    if (!response.ok) {
      throw await this.createError(response);
    }
    return response.text();
  }

  private fetchResponse(path: string, options: RequestOptions): Promise<Response> {
    const headers = new Headers(options.headers);
    if (options.sessionToken) {
      headers.set("Authorization", `Bearer ${options.sessionToken}`);
    }

    let body: BodyInit | undefined;
    if (options.body !== undefined) {
      if (typeof options.body === "string") {
        body = options.body;
      } else {
        headers.set("Content-Type", "application/json");
        body = JSON.stringify(options.body);
      }
    }

    return this.fetchImpl(`${this.baseUrl}${path}`, {
      method: options.method ?? "GET",
      headers,
      body,
    });
  }

  private async createError(response: Response): Promise<ApiClientError> {
    let error: ErrorResponse | undefined;
    try {
      error = (await response.json()) as ErrorResponse;
    } catch {
      // A provider failure may not have an API JSON body.
    }
    return new ApiClientError(response.status, error?.message ?? response.statusText, error?.code);
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT";
  sessionToken?: string;
  headers?: HeadersInit;
  body?: object | string;
}
