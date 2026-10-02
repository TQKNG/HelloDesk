# Tasks: Hotel Voice Receptionist Kiosk

**Input**: Design documents from `specs/001-hotel-voice-receptionist/`.

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, and `quickstart.md`.

**Testing**: Automated test tasks are included because the project constitution requires tests for behavior changes and integration checks across boundaries.
For each story, write the listed tests before implementation and confirm the new tests fail for the intended missing behavior.

**Organization**: Tasks are grouped by user story so the MVP and later stories can be delivered in increments.

## Phase 1: Setup

**Purpose**: Create the pnpm monorepo and app scaffolds described in `plan.md`.

- [ ] T001 Create `pnpm-workspace.yaml` with `apps/*` and `packages/*` workspace globs.
- [ ] T002 Create the root `package.json` with workspace scripts for `dev`, `build`, `start`, `lint`, `typecheck`, and `test`.
- [ ] T003 [P] Scaffold the Next.js 15 TypeScript web app and its `apps/web/package.json`, `apps/web/app/layout.tsx`, and `apps/web/app/page.tsx` entry points.
- [ ] T004 [P] Scaffold the FastAPI app and its `apps/api/pyproject.toml` and `apps/api/app/main.py` entry points.
- [ ] T005 [P] Configure local Supabase development and pgTAP database tests in `supabase/config.toml`, and create `supabase/migrations/`, `supabase/tests/`, and `supabase/seed.sql`.
- [ ] T006 [P] Add safe local configuration examples for web, API, Azure, Supabase, and Uber settings in `.env.example`.

## Phase 2: Foundational

**Purpose**: Implement shared session, action-confirmation, voice, and contract infrastructure required before any user story.

**Checkpoint**: Guest sessions, typed API contracts, provider configuration, and a pending-action confirmation boundary are ready.

- [ ] T007 [P] Initialize `packages/design-system/package.json` and `packages/shared/package.json`, add Vitest and React Testing Library dependencies, then configure web and shared-package tests in `apps/web/vitest.config.ts` and `packages/shared/vitest.config.ts`.
- [ ] T008 [P] Configure pytest and async API test support in `apps/api/pyproject.toml` and `apps/api/tests/conftest.py`.
- [ ] T009 Add typed runtime settings, secret loading, and safe redacted logging in `apps/api/app/core/settings.py` and `apps/api/app/core/logging.py`.
- [ ] T010 Add shared API error response handling for invalid input, unauthorized sessions, expired actions, and provider outages in `apps/api/app/core/errors.py` and `apps/api/app/main.py`.
- [ ] T011 Add tests for guest-session isolation, expiration, and unsupported language rejection in `apps/api/tests/unit/test_guest_session_service.py`.
- [ ] T012 Create the guest-session table and row policies in `supabase/migrations/001_guest_sessions.sql`, preserving these model constraints verbatim: `id` is an internal primary key; `token_hash` is "Unique hash of a random bearer token; return the raw token once and never persist it"; `language` is `en` or `vi`; `reservation_id` is "Set only after a valid reservation lookup and guest confirmation"; `status` is `active`, `ended`, or `expired`; `created_at` and `expires_at` are "Server managed; expire on idle timeout or guest completion".
- [ ] T013 Implement guest-session creation, bearer-token hashing and validation, reservation scoping, and expiration in `apps/api/app/models/guest_session.py`, `apps/api/app/repositories/guest_session_repository.py`, `apps/api/app/services/guest_session_service.py`, and `apps/api/app/routes/guest_sessions.py`.
- [ ] T014 Add tests proving pending actions cannot commit without an explicit guest confirmation, cannot be replayed, and expire in `apps/api/tests/unit/test_confirmation_service.py`.
- [ ] T015 [P] Create the pending-action table in `supabase/migrations/002_pending_actions.sql`, preserving these model constraints verbatim: `id` is a unique action identifier shown to the client as opaque; `session_id` references the creating guest session; `kind` is `check_in`, `check_out`, `staff_help`, or `uber_ride`; `summary` is "Human-readable, localized details shown and spoken before confirmation"; `details` are "Validated server-side, action-specific data; never trusted from the model alone"; `status` is `pending`, `confirmed`, `cancelled`, `expired`, or `failed`; `expires_at` is "Short-lived; confirmation after expiry is rejected"; `request_id` is "Idempotency key for a commit attempt" and nullable.
- [ ] T016 Implement pending-action preparation, localized summary storage, confirmation, cancellation, expiration, and idempotency in `apps/api/app/models/pending_action.py` and `apps/api/app/services/confirmation_service.py`.
- [ ] T017 Add a mocked-provider test for authenticated SDP negotiation in `apps/api/tests/integration/test_voice_session_route.py`.
- [ ] T018 Implement the server-side Azure GPT-Live WebRTC SDP broker in `apps/api/app/services/voice_session_service.py` and `apps/api/app/routes/voice.py`; keep Azure credentials server-side and do not persist raw audio or full transcripts.
- [ ] T019 Implement the initial guest-session voice client and microphone permission state in `apps/web/src/features/guest-session/use-voice-session.ts` and `apps/web/src/features/guest-session/voice-status.tsx`.
- [ ] T020 Define shared request and response types from `specs/001-hotel-voice-receptionist/contracts/openapi.yaml` in `packages/shared/src/api-types.ts` and `packages/shared/src/api-client.ts`.
- [ ] T021 Implement shared guest action prepare/confirm/cancel endpoints around `ConfirmationService` in `apps/api/app/routes/guest/actions.py`, create isolated guest and staff router modules in `apps/api/app/routes/guest/__init__.py`, `apps/api/app/routes/guest/stays.py`, `apps/api/app/routes/guest/help.py`, `apps/api/app/routes/guest/rides.py`, `apps/api/app/routes/staff/__init__.py`, `apps/api/app/routes/staff/help_requests.py`, and `apps/api/app/routes/staff/sessions.py`, and register the routers and guest/staff CORS allowlist in `apps/api/app/main.py`.

## Phase 3: User Story 1 - Complete a hotel stay task by voice (Priority: P1) 🎯 MVP

**Goal**: Guests select English or Vietnamese, check in, review a bill, and check out by voice with explicit confirmations and visual details.

**Independent Test**: Use seeded reservations to complete one check-in and one checkout, verify reservation and bill states change only after confirmation, and inspect the room information and barcode.

### Tests for User Story 1

- [ ] T022 [P] [US1] Add API tests for reservation lookup, lookup confirmation, bill retrieval, and check-in/checkout state transitions in `apps/api/tests/integration/test_reservation_journey.py`.
- [ ] T023 [P] [US1] Add web interaction tests for language selection, guest confirmation, cancellation, and room barcode display in `apps/web/tests/features/guest-stay-journey.test.tsx`.
- [ ] T024 [P] [US1] Add database policy tests for reservation and bill access scoped to the active guest session in `supabase/tests/reservation_bill_access.sql`.

### Implementation for User Story 1

- [ ] T025 [US1] Create reservation and bill schema, seed records, session foreign-key migration, and row policies in `supabase/migrations/003_reservations_and_bills.sql` and `supabase/seed.sql`, preserving these model constraints verbatim: reservation `id` is a primary key; `reservation_code` is "Unique demo lookup code; never use a real guest code"; `guest_display_name` is "Synthetic display name; reveal only after a successful lookup"; `arrival_date` is "Required"; `departure_date` "Must be after arrival"; `room_number` is "Required after check-in"; reservation `status` is `reserved`, `checked_in`, `checked_out`, or `cancelled`; reservation timestamps are "Server managed"; bill `id` is a primary key; `reservation_id` references one reservation; `items` are "Synthetic item description, quantity, unit amount, and line total in minor currency units"; bill `currency` is "Required" and ISO 4217; `total_amount_minor` "Must equal the sum of line totals; avoids floating-point currency arithmetic"; bill `status` is `open`, `reviewed`, or `closed` and "does not imply payment".
- [ ] T026 [US1] Implement reservation and bill repositories with session-scoped lookups in `apps/api/app/repositories/reservation_repository.py` and `apps/api/app/repositories/bill_repository.py`.
- [ ] T027 [US1] Implement reservation lookup, reservation confirmation, and itemized bill retrieval in `apps/api/app/services/reservation_service.py` and `apps/api/app/services/billing_service.py`.
- [ ] T028 [US1] Implement check-in and checkout action handlers in `apps/api/app/services/stay_action_handler.py`, allowing only `reserved -> checked_in -> checked_out`, rejecting check-in for `cancelled` reservations, requiring a matching unexpired guest session and confirmed pending action, and honoring an idempotency key; return room number and an opaque display-only barcode payload after check-in.
- [ ] T029 [US1] Add the reservation lookup, lookup confirmation, and bill routes from `specs/001-hotel-voice-receptionist/contracts/openapi.yaml` in `apps/api/app/routes/guest/stays.py`.
- [ ] T030 [US1] Implement English and Vietnamese welcome-screen language selection before guest session creation in `apps/web/app/page.tsx` and `apps/web/src/features/guest-session/language-picker.tsx`.
- [ ] T031 [US1] Implement the guest stay conversation and pending-action confirmation UI in `apps/web/src/features/guest-stay/guest-stay-flow.tsx` and `apps/web/src/features/guest-stay/action-confirmation.tsx`.
- [ ] T032 [US1] Render confirmed room information and the non-credential room barcode payload from the check-in result in `apps/web/src/features/guest-stay/room-confirmation.tsx`.
- [ ] T033 [US1] Render and localize the itemized bill, checkout confirmation, and non-payment completion state in `apps/web/src/features/guest-stay/bill-review.tsx` and `apps/web/src/features/guest-stay/messages.ts`.

**Checkpoint**: The P1 kiosk journey works independently with seeded data and does not change stay or bill state before confirmation.

## Phase 4: User Story 2 - Get hotel information and request staff help (Priority: P2)

**Goal**: Guests receive supported hotel answers in their selected language and can send a confirmed help request for staff acknowledgement.

**Independent Test**: Ask a configured and an unavailable hotel question, confirm a help request for the unavailable answer, then acknowledge it in the staff view and verify the guest sees the updated state.

### Tests for User Story 2

- [ ] T034 [P] [US2] Add API tests for supported hotel answers, unsupported questions, guest help-request ownership, and staff acknowledgement in `apps/api/tests/integration/test_hotel_help_flow.py`.
- [ ] T035 [P] [US2] Add web tests for localized hotel answers, request review, pending status, staff sign-in, and acknowledgement in `apps/web/tests/features/hotel-help-flow.test.tsx`.
- [ ] T036 [P] [US2] Add database policy tests that restrict help-request listing and acknowledgement to staff in `supabase/tests/help_request_access.sql`.

### Implementation for User Story 2

- [ ] T037 [US2] Create the help-request schema and row policies in `supabase/migrations/004_help_requests.sql`, preserving these model constraints verbatim: `id` is a primary key; `session_id` "References the guest interaction"; `reservation_id` is "Linked only when available in the guest session"; `summary` is "Guest-confirmed summary; do not store the full voice transcript"; `status` is `pending` or `acknowledged`; `created_at` is "Server managed"; `acknowledged_at` is "Set when a staff member acknowledges" and nullable.
- [ ] T038 [US2] Add synthetic hotel facts in `apps/api/app/data/hotel_information.json` and implement server-side answer handling through Microsoft Agent Framework in `apps/api/app/services/hotel_information_service.py` and `apps/api/app/services/hotel_agent.py`.
- [ ] T039 [US2] Implement and register the staff-help action handler, guest-owned status retrieval, and staff acknowledgement in `apps/api/app/models/help_request.py`, `apps/api/app/repositories/help_request_repository.py`, and `apps/api/app/services/help_action_handler.py`.
- [ ] T040 [US2] Add guest and authenticated staff help-request routes from `specs/001-hotel-voice-receptionist/contracts/openapi.yaml` in `apps/api/app/routes/guest/help.py` and `apps/api/app/routes/staff/help_requests.py`.
- [ ] T041 [US2] Implement local-only demo staff session creation and authorization in `apps/api/app/auth/staff.py` and `apps/api/app/routes/staff/sessions.py`; keep the `admin` / `admin` credentials local and configurable, never as production credentials.
- [ ] T042 [US2] Implement the staff help-request list, acknowledgement controls, and status refresh in `apps/web/app/staff/page.tsx` and `apps/web/src/features/staff/help-request-list.tsx`.
- [ ] T043 [US2] Show guest help-request submission and pending/acknowledged status in `apps/web/src/features/hotel-help/help-request-status.tsx`.

**Checkpoint**: Guests can get configured answers or create an owned help request, and only authenticated staff can view or acknowledge requests.

## Phase 5: User Story 3 - Request a ride (Priority: P3)

**Goal**: A guest confirms a ride request and receives a clearly simulated Uber sandbox result without live dispatch.

**Independent Test**: Request a ride to a configured demo destination, verify no sandbox call occurs before guest confirmation, then verify a simulated result and no live trip.

### Tests for User Story 3

- [ ] T044 [P] [US3] Add ride-service contract tests for fake and Uber sandbox adapters, including unavailable credentials and simulated outcomes, in `apps/api/tests/contracts/test_ride_booking_adapter.py`.
- [ ] T045 [P] [US3] Add API tests proving rides require confirmation and never use a production endpoint in `apps/api/tests/integration/test_ride_request_flow.py`.
- [ ] T046 [P] [US3] Add web tests for destination selection, exact detail confirmation, cancellation, and simulated status wording in `apps/web/tests/features/ride-request-flow.test.tsx`.

### Implementation for User Story 3

- [ ] T047 [US3] Create the ride-request schema and row policies in `supabase/migrations/005_ride_requests.sql`, preserving these model constraints verbatim: `id` is a primary key; `session_id` references the guest session; `destination_id` "Identifies a configured demo destination selected and confirmed by the guest"; `destination_label` is "Guest-visible destination label copied from configuration"; `status` is `pending`, `simulated`, `unavailable`, `failed`, or `cancelled`; `provider_reference` is "Uber sandbox identifier; server-side only" and nullable; `created_at` and `updated_at` are server managed.
- [ ] T048 [US3] Add configured synthetic ride destinations in `apps/api/app/data/demo_destinations.json` and define the ride-booking service interface and deterministic fake adapter in `apps/api/app/services/ride_booking_service.py` and `apps/api/app/adapters/fake_ride_booking.py`.
- [ ] T049 [US3] Implement the Uber Guest Rides sandbox adapter using only sandbox credentials and URLs in `apps/api/app/adapters/uber_guest_rides_sandbox.py`.
- [ ] T050 [US3] Register the confirmed `uber_ride` action handler, persist sandbox references server-side, and return only simulated guest-visible status in `apps/api/app/services/ride_action_handler.py` and `apps/api/app/routes/guest/rides.py`.
- [ ] T051 [US3] Implement configured destination selection, spoken detail review, and simulated ride confirmation in `apps/web/src/features/ride-request/ride-request-flow.tsx` and `apps/web/src/features/ride-request/ride-status.tsx`.

**Checkpoint**: The guest journey is independently testable with the fake adapter and reports only simulated results when the Uber sandbox is configured.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify privacy, accessibility, bilingual behavior, and the full set of measurable outcomes.

- [ ] T052 Add cross-session authorization and failed reservation-lookup rate-limit tests in `apps/api/tests/security/test_guest_session_isolation.py` and `apps/api/tests/security/test_reservation_lookup_limits.py`.
- [ ] T053 Add tests and redaction rules proving raw audio, full transcripts, and provider credentials are not persisted or logged in `apps/api/tests/security/test_voice_data_retention.py` and `apps/api/app/core/logging.py`.
- [ ] T054 Add microphone-denied, keyboard-entry, visible cancellation, and keyboard-accessibility fallback coverage in `apps/web/tests/accessibility/kiosk-fallback.test.tsx` and `apps/web/src/features/guest-session/voice-status.tsx`.
- [ ] T055 Document local environment setup and repeatable guest acceptance scenarios in `specs/001-hotel-voice-receptionist/quickstart.md` and `.env.example`.
- [ ] T056 Run the 20 scripted check-in/checkout scenarios and record whether at least 18 succeed in `specs/001-hotel-voice-receptionist/quickstart.md`.
- [ ] T057 Record first-time completion for both languages and confirm at least 90% of observed guests complete a primary stay task without facilitator assistance in `specs/001-hotel-voice-receptionist/quickstart.md`.
- [ ] T058 Run `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, and `python -m pytest apps/api/tests`, then record outcomes and unresolved environment limitations in `specs/001-hotel-voice-receptionist/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No prerequisites; complete before the foundational phase.
- **Foundational (Phase 2)**: Depends on the workspace and app scaffolds; blocks all user stories.
- **User Stories (Phases 3-5)**: Depend on the foundational phase.
- **Polish (Phase 6)**: Depends on the stories being delivered and integrated.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; it is the MVP and does not depend on US2 or US3.
- **User Story 2 (P2)**: Starts after Phase 2; shares guest sessions and confirmation infrastructure, but not US1 feature code.
- **User Story 3 (P3)**: Starts after Phase 2; shares guest sessions and confirmation infrastructure, but not US1 or US2 feature code.
- For the MVP-first delivery, complete US1 before scheduling US2 and US3.
  After Phase 2, US2 and US3 may be developed concurrently by separate agents because their feature modules and adapters are separate.

### Parallel Execution Examples

After T002, independent app and database setup can be assigned separately:

```text
Agent A: T003 scaffold apps/web
Agent B: T004 scaffold apps/api
Agent C: T005 configure Supabase local development
```

After Phase 2, story reviewers and implementers can work in separate story areas:

```text
Agent A: US1 reservation, bill, and guest stay flow (T022-T033)
Agent B: US2 hotel answers and staff help flow (T034-T043)
Agent C: US3 sandbox ride flow (T044-T051)
```

Each agent must own distinct files and coordinate edits to shared routes, OpenAPI types, and migrations with the lead before integration.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3, User Story 1.
3. Validate check-in and checkout independently with seeded records.
4. Demonstrate English and Vietnamese selection, confirmation gates, and barcode presentation.

### Incremental Delivery

1. Deliver the P1 stay flow as the first working kiosk increment.
2. Add P2 hotel answers and staff help acknowledgement.
3. Add P3 sandbox ride simulation.
4. Complete Phase 6 acceptance, privacy, and regression checks.

## Notes

- Every task uses the required `- [ ] T### [P?] [US#?] Description with file path` checklist format.
- `[P]` marks tasks that can be assigned concurrently without editing the same files or waiting on unfinished work.
- User-story tasks carry the matching `[US1]`, `[US2]`, or `[US3]` label; setup, foundational, and polish tasks do not.
- Test tasks precede their corresponding implementations and should demonstrate the missing behavior before implementation.
