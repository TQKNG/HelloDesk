# Data Model: Hotel Voice Receptionist Kiosk

## Reservation

Represents a synthetic hotel booking used by the demo.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Primary key. |
| `reservation_code` | String | Unique demo lookup code; never use a real guest code. |
| `guest_display_name` | String | Synthetic display name; reveal only after a successful lookup. |
| `arrival_date` | Date | Required. |
| `departure_date` | Date | Must be after arrival. |
| `room_number` | String | Required after check-in; not a door credential. |
| `status` | Enum | `reserved`, `checked_in`, `checked_out`, `cancelled`. |
| `created_at`, `updated_at` | Timestamp | Server managed. |

### Rules and transitions

- Allowed transitions are `reserved -> checked_in -> checked_out`.
- A cancelled reservation cannot be checked in.
- Check-in and checkout require a matching, unexpired guest session and a confirmed pending action.
- Keep the lookup result scoped to that guest session and return only the details needed for confirmation.

## Bill

Represents charges for a reservation, shown for review during checkout.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Primary key. |
| `reservation_id` | UUID | References one reservation. |
| `items` | JSON array | Synthetic item description, quantity, unit amount, and line total in minor currency units. |
| `currency` | ISO 4217 string | Required. |
| `total_amount_minor` | Integer | Must equal the sum of line totals; avoids floating-point currency arithmetic. |
| `status` | Enum | `open`, `reviewed`, `closed`; does not imply payment. |
| `updated_at` | Timestamp | Server managed. |

Checkout closes the bill and updates the stay only after the guest confirms the exact displayed bill summary.
Payment collection is out of scope.

## Guest Session

An expiring interaction context for one kiosk guest.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Internal primary key. |
| `token_hash` | String | Unique hash of a random bearer token; return the raw token once and never persist it. |
| `language` | Enum | `en` or `vi`, selected before the voice session. |
| `reservation_id` | UUID, nullable | Set only after a valid reservation lookup and guest confirmation. |
| `created_at`, `expires_at` | Timestamp | Server managed; expire on idle timeout or guest completion. |
| `status` | Enum | `active`, `ended`, `expired`. |

The session scopes all guest lookups and mutations to one stay.
Voice audio and transcript text remain ephemeral and are not stored as session history.

## Pending Action

A server-side proposal requiring an explicit guest decision before a write is committed.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Unique action identifier shown to the client as opaque. |
| `session_id` | UUID | References the creating guest session. |
| `kind` | Enum | `check_in`, `check_out`, `staff_help`, `uber_ride`. |
| `summary` | String | Human-readable, localized details shown and spoken before confirmation. |
| `details` | JSON object | Validated server-side, action-specific data; never trusted from the model alone. |
| `status` | Enum | `pending`, `confirmed`, `cancelled`, `expired`, `failed`. |
| `expires_at` | Timestamp | Short-lived; confirmation after expiry is rejected. |
| `request_id` | UUID, nullable | Idempotency key for a commit attempt. |

Confirmation applies only to the exact pending action and summary.
Repeated requests with the same idempotency key return the original outcome without repeating a mutation.

## Help Request

A staff work item created from a guest-confirmed request.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Primary key. |
| `session_id` | UUID | References the guest interaction. |
| `reservation_id` | UUID, nullable | Linked only when available in the guest session. |
| `summary` | String | Guest-confirmed summary; do not store the full voice transcript. |
| `status` | Enum | `pending`, `acknowledged`. |
| `created_at` | Timestamp | Server managed. |
| `acknowledged_at` | Timestamp, nullable | Set when a staff member acknowledges. |

Only authenticated staff can list and acknowledge requests.
Guests can see their own request status through the owning session.

## Ride Request

A guest-confirmed simulated ride request.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | UUID | Primary key. |
| `session_id` | UUID | References the guest session. |
| `destination_id` | String | Identifies a configured demo destination selected and confirmed by the guest. |
| `destination_label` | String | Guest-visible destination label copied from configuration. |
| `status` | Enum | `pending`, `simulated`, `unavailable`, `failed`, `cancelled`. |
| `provider_reference` | String, nullable | Uber sandbox identifier; server-side only. |
| `created_at`, `updated_at` | Timestamp | Server managed. |

Every guest-visible completed outcome is explicitly labeled simulated.
No production endpoint, live driver dispatch, or payment operation is allowed.

## Relationships

- The reservation status represents the stay lifecycle, and each reservation has one current bill in the demo.
- A guest session may be anonymous for hotel questions, then become scoped to one reservation after lookup confirmation.
- Pending actions belong to one active guest session and are single-use.
- Help requests and ride requests belong to their originating guest session and, when known, its reservation.
- Raw audio and full transcripts are not durable entities; only a guest-confirmed help summary is retained.
