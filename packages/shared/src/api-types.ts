export const SUPPORTED_LANGUAGES = ["en", "vi"] as const;
export const GUEST_SESSION_STATUSES = ["active", "ended", "expired"] as const;
export const RESERVATION_STATUSES = [
  "reserved",
  "checked_in",
  "checked_out",
  "cancelled",
] as const;
export const BILL_STATUSES = ["open", "reviewed", "closed"] as const;
export const ACTION_KINDS = [
  "check_in",
  "check_out",
  "staff_help",
  "uber_ride",
] as const;
export const PENDING_ACTION_STATUSES = [
  "pending",
  "confirmed",
  "cancelled",
  "expired",
  "failed",
] as const;
export const ACTION_OUTCOME_STATUSES = ["completed", "simulated", "failed"] as const;
export const HELP_REQUEST_STATUSES = ["pending", "acknowledged"] as const;
export const RIDE_STATUSES = ["simulated", "unavailable", "failed"] as const;

export type Language = (typeof SUPPORTED_LANGUAGES)[number];
export type GuestSessionStatus = (typeof GUEST_SESSION_STATUSES)[number];
export type ReservationStatus = (typeof RESERVATION_STATUSES)[number];
export type BillStatus = (typeof BILL_STATUSES)[number];
export type ActionKind = (typeof ACTION_KINDS)[number];
export type PendingActionStatus = (typeof PENDING_ACTION_STATUSES)[number];
export type ActionOutcomeStatus = (typeof ACTION_OUTCOME_STATUSES)[number];
export type HelpRequestStatus = (typeof HELP_REQUEST_STATUSES)[number];
export type RideStatus = (typeof RIDE_STATUSES)[number];

export interface ErrorResponse {
  code: string;
  message: string;
}

export interface ReservationSummary {
  displayName: string;
  arrivalDate: string;
  departureDate: string;
  status: ReservationStatus;
  roomNumber?: string;
}

export interface GuestSession {
  sessionToken: string;
  language: Language;
  expiresAt: string;
  status: GuestSessionStatus;
  reservation?: ReservationSummary | null;
}

/** Session state returned after reservation confirmation; the bearer token is not repeated. */
export interface GuestSessionState {
  language: Language;
  expiresAt: string;
  status: GuestSessionStatus;
}

export interface CreateGuestSessionRequest {
  language: Language;
}

export interface ReservationLookupRequest {
  reservationCode: string;
}

export interface ReservationLookup {
  lookupId: string;
  reservation: ReservationSummary;
  requiresConfirmation: true;
}

export interface BillItem {
  description: string;
  quantity: number;
  unitAmountMinor: number;
  lineTotalMinor: number;
}

export interface Bill {
  items: BillItem[];
  currency: string;
  totalAmountMinor: number;
  status: BillStatus;
}

export interface PrepareActionDetails {
  summary?: string;
  destinationId?: string;
}

export interface PrepareActionRequest {
  kind: ActionKind;
  details?: PrepareActionDetails;
}

export interface PendingAction {
  actionId: string;
  kind: ActionKind;
  summary: string;
  status: PendingActionStatus;
  expiresAt: string;
}

export interface ConfirmActionRequest {
  confirmed: true;
}

export interface ActionOutcomeResult {
  roomNumber?: string;
  roomBarcodePayload?: string;
  helpRequestId?: string;
  rideStatus?: RideStatus;
  rideRequestId?: string;
}

export interface ActionOutcome {
  actionId: string;
  status: ActionOutcomeStatus;
  message: string;
  result?: ActionOutcomeResult;
}

export interface HelpRequest {
  id: string;
  summary: string;
  status: HelpRequestStatus;
  createdAt: string;
  acknowledgedAt?: string;
}

export interface HotelQuestionRequest {
  question: string;
}

export interface HotelQuestionResponse {
  answer?: string;
  needsStaffHelp: boolean;
}

export interface CreateStaffSessionRequest {
  username: string;
  password: string;
}

export interface StaffSession {
  sessionToken: string;
  expiresAt: string;
}
