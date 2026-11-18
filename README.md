# HelloDesk

HelloDesk is a real-time hotel voice receptionist for guest check-in, check-out, and Uber ride requests.

## Status

The repository contains a Next.js web application, a FastAPI API, shared TypeScript packages, Supabase migrations, and a hotel voice receptionist specification.

Voice conversations support English and Vietnamese; reservation, help, and ride operations currently use kiosk controls.

## Prerequisites

- Node.js 22 and pnpm 11
- Python 3.12 or newer
- Supabase local development or a non-production Supabase project

## Setup

1. Run `pnpm install` at the repository root.
2. In `apps/api`, create a virtual environment and install with `python -m pip install -e '.[dev]'`.
3. Copy `.env.example` to `.env` and set local values.
4. Start Supabase with `supabase start` and apply local schema and seed data with `supabase db reset`.
5. Start the API from `apps/api` with `python -m uvicorn app.main:app --reload`.
6. Start the web app from the root with `pnpm dev`.

Use synthetic guest records and non-production credentials.

## Checks

- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm build`
- `python -m pytest apps/api/tests`

## Layout

- `apps/web`: guest and staff web application
- `apps/api`: FastAPI service
- `packages/shared`: shared API types and client
- `packages/design-system`: shared UI components
- `supabase`: local configuration, migrations, seeds, and database tests
- `specs`: feature specifications and acceptance guidance

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution steps and [AGENTS.md](AGENTS.md) for repository guidance.