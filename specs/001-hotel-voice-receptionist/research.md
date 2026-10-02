# Research: Hotel Voice Receptionist Kiosk

**Date**: 2026-10-02

## Decisions

### Browser voice transport

**Decision**: Use Azure GPT-Live over WebRTC for the browser kiosk's low-latency audio session.
FastAPI creates the session and relays the SDP answer; media then flows between the browser and Azure.
Keep credentials on the server and create one expiring voice session per kiosk guest.

**Rationale**: Microsoft documents WebRTC for low-latency browser audio, with the API holding credentials because GPT-Live does not issue ephemeral client keys.
The current realtime language guidance lists Vietnamese and English for GPT-Realtime models.
The selected Foundry deployment and both languages still need an acceptance run in the target Azure region before implementation is considered complete.

**Alternatives considered**: Server-to-server WebSocket streaming would keep media server-side but adds a media relay and is not the recommended browser transport for low-latency audio.
Voice Live is an alternative unified speech service, but using it alongside GPT-Live in the first release would duplicate the voice path without a specified need.

Sources: [GPT-Live WebRTC](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/gpt-live-webrtc), [realtime language support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live-language-support), [Voice Live WebRTC](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live-webrtc).

### Agent and action boundary

**Decision**: Keep the user-facing voice session in GPT-Live and use Microsoft Agent Framework for server-side hotel information answering and typed read-only domain tools.
FastAPI owns all application actions and is the only component allowed to access storage or provider credentials.

**Rationale**: This assigns speech and hotel domain work to explicit layers while keeping data access, authorization, and write validation in the trusted API.
Treat model tool calls as proposals; they cannot commit a state change.
For every check-in, checkout, help request, or ride, the API returns an action summary and short-lived action identifier, then commits only after an explicit guest confirmation tied to that action.

**Alternatives considered**: Calling Supabase or Uber from the browser would expose sensitive access and weaken session scoping.
Letting model output directly trigger writes would violate the spec's confirmation requirement.

Sources: [Microsoft Agent Framework Azure OpenAI integration](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/azure-openai), [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/).

### Reservation and operational data

**Decision**: Store synthetic demo reservations, stays, bills, help requests, and ride records in Supabase Postgres.
FastAPI accesses them using server-only credentials, with versioned migrations, least-privilege grants, and row-level security.
Use fake/in-memory adapters in automated tests and when external demo credentials are unavailable.

**Rationale**: The spec excludes live hotel system integration and requires repeatable sample data.
Keeping database access in FastAPI prevents the public kiosk from querying hotel records directly.
Supabase documents that server secret keys bypass row-level security, so those keys must stay server-side; grants and RLS policies still need explicit setup and tests.

**Alternatives considered**: Direct browser queries would require exposing application data through Supabase and carefully scoping all anonymous access.
A real hotel property-management integration is outside this feature's scope.

Sources: [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys), [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security), [database migrations](https://supabase.com/docs/guides/local-development/database-migrations), [database testing](https://supabase.com/docs/guides/database/testing).

### Uber ride simulation

**Decision**: Use the Uber Guest Rides sandbox behind a FastAPI ride service adapter.
Keep a fake adapter for local and automated scenarios, label every sandbox result as simulated, and never call the production Uber endpoint.

**Rationale**: Guest Rides matches a hotel arranging a ride on behalf of a guest.
The sandbox does not create production trips, but its runs and mock drivers are ephemeral and can take up to a minute to initialize.
Sandbox access may require Uber support whitelisting, so the demo must remain testable without that access.

**Alternatives considered**: The rider-owned Request API assumes a rider-owned account and is a poorer fit for a hotel-arranged guest ride.
Live Uber booking conflicts with the spec.

Sources: [Guest Rides introduction](https://developer.uber.com/docs/guest-rides/introduction), [Guest Rides sandbox](https://developer.uber.com/docs/guest-rides/guides/sandbox).

### Browser, testing, and runtime baseline

**Decision**: Use the repository's stated pnpm, Node.js 22, TypeScript, Next.js 15, FastAPI, and Vitest stack.
Use Python 3.12 as the initial backend baseline and pytest for FastAPI tests.
Require HTTPS for kiosk microphone access, display a live transcript and action confirmations, and provide a visible text/staff-help fallback.

**Rationale**: The stack and monorepo boundaries come from `AGENTS.md`.
Python 3.12 and pytest are planning defaults because the repository currently has no Python package manifest or tests.
Browser media access requires a secure context and user permission, so unavailable audio must not strand the guest.

**Alternatives considered**: The repository contains no dependency manifests to establish a different Python version or API test runner.
The implementation may adjust the Python baseline if the chosen hosted runtime or dependency set requires it, while preserving the service boundaries and tests.

Sources: [Next.js 15 Route Handlers](https://nextjs.org/docs/15/app/getting-started/route-handlers-and-middleware), [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/), [MDN microphone access](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).
