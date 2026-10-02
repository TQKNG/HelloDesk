# Implementation Plan: Hotel Voice Receptionist Kiosk

**Branch**: `001-hotel-voice-receptionist` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-hotel-voice-receptionist/spec.md`

## Summary

Build a bilingual lobby kiosk and staff view for a single small-hotel demo.
The Next.js web app handles guest interaction and staff workflows, while a FastAPI service owns guest sessions, hotel actions, data access, agent tools, and provider integrations.
Use Supabase Postgres with synthetic demo records, Azure GPT-Live over a backend-brokered WebRTC session for English and Vietnamese voice, Microsoft Agent Framework for server-side hotel question answering and typed read-only tools, and the Uber Guest Rides sandbox for simulated rides.
All state-changing actions follow a prepare, review, and explicit-confirmation flow.

## Technical Context

**Language/Version**: TypeScript on Node.js 22 for the web app; Python 3.12 for the API (planning baseline).

**Primary Dependencies**: Next.js 15, FastAPI, Microsoft Agent Framework, Azure Foundry GPT-Live, Supabase Postgres, and Uber Guest Rides sandbox.

**Storage**: Supabase Postgres for seeded reservations, bills, help requests, and ride records; reservation status represents the stay lifecycle; short-lived guest and voice sessions expire and are not used as durable transcript storage.

**Testing**: Vitest for web and shared TypeScript packages; pytest with FastAPI's test client for API tests; adapter contract and cross-service integration tests for Supabase, voice-session brokerage, and Uber sandbox behavior.

**Target Platform**: HTTPS-enabled modern browser on a lobby kiosk; hosted Python API and managed Supabase database.

**Project Type**: pnpm monorepo with a Next.js web app, FastAPI backend app, and focused shared TypeScript packages.

**Performance Goals**: Preserve a natural streaming voice interaction and meet the spec's 18-of-20 scripted check-in/check-out completion goal and 90% first-time guest completion goal; no numeric speech-latency SLO is set by the spec.

**Constraints**: English and Vietnamese must both work; browser microphone access requires HTTPS and user permission; each kiosk guest gets an isolated, expiring session; the browser never receives provider secrets or direct database access; write actions require explicit guest confirmation; use synthetic hotel data; no payment, live property-management connection, or live Uber dispatch.

**Scale/Scope**: One hotel demonstration, one lobby kiosk session at a time per kiosk, seeded reservations and bills, and a small staff help-request view.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Code Quality**: Pass. Typed request and response contracts, focused service responsibilities, and repository lint/type checks make behavior reviewable.
- **Maintainable Design**: Pass. Apps own their runtime concerns; provider adapters sit behind backend service interfaces; reusable web code lives in shared packages; no plugin architecture is introduced.
- **Meaningful Testing**: Pass. Each user behavior has a focused test, and mutations require regression coverage.
- **Integration Confidence**: Pass. The plan includes API, database, voice session, and sandbox integration checks for cross-boundary flows.
- **Simplicity and Safe Change**: Pass. The first release uses one hotel, seeded data, one voice provider path, and sandbox-only rides; it excludes payments and live hotel system integration.

No constitution exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/001-hotel-voice-receptionist/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md                 # Created later by $speckit-tasks
```

### Source Code (repository root)

```text
apps/
├── web/                     # Next.js guest kiosk and staff interface
│   ├── app/
│   └── tests/
└── api/                     # FastAPI endpoints and application services
    ├── app/
    ├── tests/
    └── pyproject.toml
packages/
├── design-system/           # Shared web components and styles
└── shared/                  # Shared TypeScript contracts and utilities
supabase/
├── migrations/              # Versioned schema, grants, and row policies
└── seed.sql                 # Synthetic demo data only
docs/
```

**Structure Decision**: Use the repository's documented monorepo layout with `apps/web`, `apps/api`, `packages/design-system`, and `packages/shared`.
Keep persistence and provider adapters in `apps/api`; no plugins or additional app/package boundaries are needed for this single-hotel demo.

## Design Decisions

- The web app never queries reservation, bill, help-request, or ride tables directly.
  FastAPI is the only boundary for application data and third-party actions; the voice media connection is negotiated through FastAPI before streaming directly to Azure.
- The browser negotiates a short-lived Azure GPT-Live WebRTC voice session through FastAPI.
  The trusted API broker creates the Azure session so provider credentials stay server-side.
- GPT-Live handles low-latency spoken conversation and function requests.
  FastAPI validates every function request and routes hotel questions through the Microsoft Agent Framework and typed domain services.
- Read-only lookups may occur during conversation, but a function request cannot commit check-in, checkout, staff help, or a ride.
  FastAPI creates a short-lived pending action summary; the guest reviews and explicitly confirms it before the API commits the action.
- Supabase credentials remain server-side.
  Use synthetic seed records, versioned migrations, least-privilege grants, and row-level security as defense in depth.
- Use the Uber Guest Rides API sandbox behind a ride service adapter.
  The interface reports simulated status and never presents a sandbox result as a live dispatched driver.
- Keep spoken transcript text and audio in the active voice session only.
  Persist only the summary explicitly sent with a staff request, and do not log raw audio, credentials, or full transcripts.
- Give the staff view a separate authenticated surface.
  Local demo credentials documented in `AGENTS.md` are for local use only and must not be treated as production authentication.

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Browser microphone is unavailable or permission is denied. | Serve the kiosk over HTTPS; show a clear permission state and provide a visible text-entry and staff-help fallback. |
| Spoken or model-generated intent is ambiguous. | Keep consequential actions pending until the guest confirms the exact action summary; allow correction, cancellation, and expiration. |
| Azure model, language, or region availability changes. | Validate English and Vietnamese voice quality and model availability in the target Foundry region before selecting deployment identifiers. |
| Guest Rides sandbox access is not enabled or sandbox data expires. | Keep an in-memory fake adapter for deterministic demos and tests; make sandbox access an optional integration configuration. |
| Guest or staff data leaks across sessions, or reservation codes are guessed. | Scope guest sessions to one stay, expire them, limit repeated failed lookups, keep secrets and provider calls on the API, and test unauthorized cross-session access. |
| A sandbox confirmation is mistaken for a real ride. | Use explicit simulated wording and status in the guest UI and staff record. |

## Complexity Tracking

No constitution violations or unjustified architecture complexity are proposed.
