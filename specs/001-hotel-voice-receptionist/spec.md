# Feature Specification: Hotel Voice Receptionist Kiosk

**Feature Branch**: `001-hotel-voice-receptionist`

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: Context from the referenced chat, “Plan a voice receptionist app.”

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete a hotel stay task by voice (Priority: P1)

A hotel guest at the lobby kiosk chooses English or Vietnamese, then speaks naturally with the receptionist to check in or check out. The kiosk confirms important details visually and aloud before completing the requested action.

**Why this priority**: Check-in and checkout are the core front-desk tasks and demonstrate the main value of the voice receptionist.

**Independent Test**: Use a sample reservation to check in, inspect the confirmation and room barcode, then use a second sample reservation to review a bill and check out.

**Acceptance Scenarios**:

1. **Given** a guest is at the welcome screen, **When** they select English or Vietnamese, **Then** the kiosk starts the conversation in that language and keeps that language for the session.
2. **Given** a valid reservation, **When** the guest asks to check in and confirms the presented reservation details, **Then** the reservation is checked in and the kiosk presents the room information and room barcode.
3. **Given** an active stay with a bill, **When** the guest asks to check out, **Then** the kiosk presents the bill for review and completes checkout only after the guest confirms.
4. **Given** the receptionist is unsure what the guest said, **When** it asks a clarifying question, **Then** the guest can correct or repeat the request before any consequential action occurs.

---

### User Story 2 - Get hotel information and request staff help (Priority: P2)

A guest asks a hotel or stay-related question and receives an answer based on the information available for the demo hotel. If the guest needs a person, they can describe the issue and send it to staff.

**Why this priority**: Answering routine questions and handing off other needs lets guests use the kiosk beyond arrival and departure.

**Independent Test**: Ask a question with a known answer, then request staff help and verify the request and conversation summary appear for staff with an acknowledgement state.

**Acceptance Scenarios**:

1. **Given** an answer exists in the demo hotel information, **When** the guest asks the question in the selected language, **Then** the receptionist answers in that language.
2. **Given** the guest asks for staff help and describes a need, **When** the guest confirms sending the request, **Then** staff can see the request and conversation summary, and the kiosk shows that help was requested.
3. **Given** staff have acknowledged the request, **When** the guest checks its status, **Then** the kiosk reports that staff have acknowledged it.

---

### User Story 3 - Request a ride (Priority: P3)

A guest asks the receptionist to arrange an Uber ride. The demo completes the ride request using a sandbox simulation and shows a test confirmation without dispatching a real driver.

**Why this priority**: A simulated ride showcases an additional front-desk service while keeping the demo isolated from live transportation.

**Independent Test**: Request a ride using a configured demo destination and verify the guest receives a test ride confirmation and no live trip is created.

**Acceptance Scenarios**:

1. **Given** the guest has requested a ride and provided the required destination, **When** the guest reviews and confirms the request, **Then** the kiosk shows the simulated ride confirmation.
2. **Given** the guest has not confirmed the ride details, **When** the request is being prepared, **Then** no simulated ride is created.

### Edge Cases

- A reservation code does not match a reservation, or the reservation is already checked in, checked out, or cancelled.
- A guest's spoken request is not understood after clarification, or the guest changes their mind before confirming.
- A bill contains a charge the guest disputes; the kiosk must not represent checkout as complete until the guest confirms the reviewed bill.
- Staff have not acknowledged a help request, or the staff view is temporarily unavailable.
- The ride sandbox is unavailable, or required ride details are missing.
- The guest changes language, ends the session, or leaves before confirming an action.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The kiosk MUST let a guest choose English or Vietnamese before starting a voice session.
- **FR-002**: The receptionist MUST understand and respond in the guest's selected language throughout the session, including when asking for clarification.
- **FR-003**: The receptionist MUST answer questions when the answer exists in the configured demo hotel information and MUST offer staff help when it does not.
- **FR-004**: The receptionist MUST find a demo reservation from a guest-provided reservation code and present its identifying details for confirmation before changing its status.
- **FR-005**: The receptionist MUST complete check-in only after the guest confirms the reservation details and MUST then present room information and a room barcode on screen.
- **FR-006**: The receptionist MUST retrieve and present the bill for an active stay and complete checkout only after the guest confirms the reviewed bill.
- **FR-007**: The guest MUST be able to request staff help by voice, review the request before sending it, and see whether staff have acknowledged it.
- **FR-008**: A staff member MUST be able to view and acknowledge a help request together with its conversation summary.
- **FR-009**: The receptionist MUST collect and confirm the destination and other required ride details before submitting a ride request to the Uber sandbox.
- **FR-010**: Ride requests MUST create only simulated sandbox rides and MUST NOT dispatch a live driver.
- **FR-011**: The kiosk MUST show visual confirmations and the current action status while voice remains the primary way to complete guest tasks after language selection.
- **FR-012**: The guest MUST be able to cancel or correct a request before confirmation, and the receptionist MUST not perform a consequential action when intent or required details are uncertain.
- **FR-013**: The demo MUST use sample reservation and bill data without requiring connection to a hotel's live property-management system.

### Key Entities

- **Reservation**: A demo guest stay identified by a reservation code, guest details, stay dates, and status.
- **Bill**: The itemized charges associated with a reservation and presented for guest review at checkout.
- **Help Request**: A guest's request for staff assistance, including its summary, status, and acknowledgement.
- **Ride Request**: A guest-confirmed destination and ride request with a simulated sandbox outcome.
- **Voice Session**: A guest interaction with a selected language, conversation state, and pending action confirmations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a representative set of 20 scripted check-in and checkout scenarios, at least 18 complete successfully without staff intervention.
- **SC-002**: At least 90% of first-time test guests complete one of the primary stay tasks (check-in or checkout) without facilitator assistance.
- **SC-003**: In all tested cases, check-in, checkout, and ride requests remain uncommitted until the guest confirms the presented details.
- **SC-004**: In all tested ride scenarios, the guest receives a sandbox confirmation and no live driver is dispatched.
- **SC-005**: At least 90% of test guests can select either supported language, understand the on-screen confirmation, and complete or cancel their task without switching to another language.
- **SC-006**: Every submitted staff help request is visible to staff with its summary and a status that distinguishes pending from acknowledged.

## Assumptions

- The first release is a demonstration for one small, privately run hotel using a lobby kiosk.
- Language selection is made on the welcome screen; the rest of the guest flow is voice operated, with visual confirmations and task status.
- Reservation, bill, and hotel information are seeded for the demo; no live hotel system integration is required.
- Guests identify a reservation with its code, then confirm the displayed reservation details. Additional identity verification is outside this demo's scope.
- The room barcode is displayed after check-in as requested; its use for door access or guest identity is not defined by this feature.
- Checkout means review and confirmation of the bill and stay status. Processing a payment is outside this demo's scope.
- The Uber sandbox is used only for simulated ride requests. Live rides are outside the feature's scope.
- Voice recognition and speech responses are expected to support both English and Vietnamese; equivalent task completion in both languages is required before the demo is considered successful.
