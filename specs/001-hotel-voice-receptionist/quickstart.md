# Quickstart: Hotel Voice Receptionist Kiosk

This guide documents local setup and the repeatable acceptance run for the feature.

## Prerequisites

- Node.js 22 and pnpm are installed.
- Python 3.12 or newer is installed.
- The repository includes the `apps/web`, `apps/api`, and Supabase migration projects.
- Supabase local development is available, or a dedicated non-production Supabase project is configured.
- Synthetic seed data contains one reserved stay, one active stay with an itemized bill, and at least one hotel information answer.
- Browser voice checks use HTTPS and microphone permission.
- Azure Foundry GPT-Live credentials are optional for fake-adapter testing and required for live voice validation.
- Uber sandbox credentials and access are optional; without them, use the fake ride adapter.

## Start the services

1. Install JavaScript dependencies from the repository root with `pnpm install`.
2. Create and activate a Python virtual environment in `apps/api` with `python3 -m venv .venv` and `source .venv/bin/activate`.
3. Install API dependencies from `apps/api` with `python -m pip install -e '.[dev]'`.
4. Copy `.env.example` to `.env` and configure local values; never put real credentials in source control.
5. Start Supabase locally with `supabase start` and apply migrations and seed data with `supabase db reset`, or point the API at a dedicated non-production Supabase project.
6. Start the API from `apps/api` with `python -m uvicorn app.main:app --reload`.
7. Start the web app from the repository root with `pnpm dev`.
8. Open `http://localhost:3000` and grant microphone permission for the live voice path.

The API uses deterministic hotel answers and fake ride outcomes when Azure and Uber credentials are absent.
Set `AZURE_AGENT_ENABLED=true` and provide the Azure OpenAI endpoint, key, deployment, and API version to use the optional Agent Framework hotel-answer provider.
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
3. Request a ride to Union Square or the Ferry Building in San Francisco.
4. Verify destination and ride details are presented for confirmation.
5. Confirm the request and verify the guest sees a clearly simulated outcome; no live trip is created.

## Checks and expected results

- Run frontend checks with `pnpm --filter @hellodesk/web test` and `pnpm --filter @hellodesk/web lint`.
- Run API tests with `python -m pytest apps/api/tests`.
- Run repository-wide `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` when those root scripts are configured.
- Verify guest session isolation, expired action rejection, idempotent confirmation, and staff-only help-request access in integration tests.
- Execute the scenarios above for both languages and record outcomes in this guide.
- For the 20 scripted check-in and checkout scenarios and first-time completion target, record participant counts, language, successes, and facilitator assistance here after running them with guests.

Expected outcome: supported guest tasks complete with visible confirmations, every write waits for explicit guest confirmation, staff can acknowledge help requests, and all ride outcomes remain sandbox-simulated.
The current voice integration provides a bilingual realtime conversation and on-screen transcript, while reservation, help, and ride operations still run through kiosk form controls.
The realtime voice model does not yet invoke those domain operations, so the acceptance criteria that require completing tasks by voice remain open.

## Implementation validation record

Record the date, environment, command, and result for each scripted run before treating the target as achieved.
Do not infer first-time guest completion from developer testing; the target requires observation of first-time guests in both languages.

| Measure | Target | Result |
|---|---:|---|
| Scripted check-in and checkout scenarios | At least 18 of 20 successful | Not run in this workspace session. |
| First-time task completion | At least 90% in each supported language | Not measured with first-time guests. |

### Workspace checks on 2026-10-04

| Command | Result |
|---|---|
| `pnpm lint` | Blocked because the JavaScript workspace dependencies are not installed and the npm registry could not resolve (`ENOTFOUND`). |
| `pnpm typecheck` | Blocked because the JavaScript workspace dependencies are not installed and the npm registry could not resolve (`ENOTFOUND`). |
| `pnpm test` | Blocked because the JavaScript workspace dependencies are not installed and the npm registry could not resolve (`ENOTFOUND`). |
| `pnpm build` | Blocked because the JavaScript workspace dependencies are not installed and the npm registry could not resolve (`ENOTFOUND`). |
| `python3 -m pytest apps/api/tests` | Blocked because `pytest` is not installed in the available Python 3.14 environment. |
| `python3 -m compileall -q apps/api/app apps/api/tests` | Passed. |
| `git diff --check` | Passed for tracked-file diffs. |
