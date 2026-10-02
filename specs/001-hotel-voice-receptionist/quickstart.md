# Quickstart: Hotel Voice Receptionist Kiosk

This guide defines the end-to-end acceptance run for the feature.
The current checkout contains Spec Kit artifacts only, so these commands are the planned run path after the application scaffold and package scripts have been added.

## Prerequisites

- Node.js 22 and pnpm are installed.
- Python 3.12 is installed.
- The repository has been scaffolded with `apps/web`, `apps/api`, and Supabase migrations from [the implementation plan](./plan.md).
- Supabase local development is available, or a dedicated non-production Supabase project is configured.
- Synthetic seed data contains one reserved stay, one active stay with an itemized bill, and at least one hotel information answer.
- Browser voice checks use HTTPS and microphone permission.
- Azure Foundry GPT-Live credentials are optional for fake-adapter testing and required for live voice validation.
- Uber sandbox credentials and access are optional; without them, use the fake ride adapter.

## Start the services

1. Install JavaScript dependencies from the repository root with `pnpm install`.
2. Install the API package from `apps/api` using its Python package manifest.
3. Configure local environment values from the committed example file; never place credentials in source control.
4. Start the API from `apps/api` with `python -m uvicorn app.main:app --reload`.
5. Start the web app from the repository root with `pnpm --dir apps/web dev`.
6. Open the kiosk in a secure browser context and grant microphone permission for the live voice path.

The API must start with fake provider adapters when Azure and Uber credentials are absent.
Use only non-production credentials and synthetic guest records during the run.

## Validate guest scenarios

### English check-in

1. Select English and start a guest session.
2. Speak a seeded reservation code.
3. Verify that masked reservation details are shown and spoken before the reservation is attached to the session.
4. Ask to check in and review the pending action summary.
5. Verify that no reservation state changes before confirmation.
6. Confirm the action and verify the checked-in status, room information, and room barcode.

### Vietnamese checkout

1. Select Vietnamese and start a session for a seeded active stay.
2. Ask to check out and verify the bill is presented in Vietnamese for review.
3. Verify that the guest can cancel or correct the request and that the bill remains open until confirmation.
4. Confirm the action and verify checkout is complete without payment collection.

### Staff handoff and Uber simulation

1. Ask a hotel question without a configured answer, then request staff help.
2. Review and confirm the help summary; verify the kiosk shows pending status and the authenticated staff view can acknowledge it.
3. Request a ride to a configured demo destination.
4. Verify destination and ride details are presented for confirmation.
5. Confirm the request and verify the guest sees a clearly simulated outcome; no live trip is created.

## Checks and expected results

- Run frontend checks with `pnpm --dir apps/web test` and `pnpm --dir apps/web lint`.
- Run API tests with `python -m pytest apps/api/tests`.
- Run repository-wide `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` when those root scripts are configured.
- Verify guest session isolation, expired action rejection, idempotent confirmation, and staff-only help-request access in integration tests.
- Record success against the spec's 20 scripted check-in/checkout scenarios, 90% first-time completion target, and both supported languages.

Expected outcome: supported guest tasks complete through voice with visible confirmations, every write waits for explicit guest confirmation, staff can acknowledge help requests, and all ride outcomes remain sandbox-simulated.
