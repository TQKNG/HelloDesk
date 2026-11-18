# Contributing to HelloDesk

## Propose a change

Open an issue to discuss substantial changes before implementation.

For bugs, include reproducible steps, expected behavior, and actual behavior.

For feature requests, describe the user outcome and acceptance criteria.

## Set up

Follow the prerequisites and setup steps in [README.md](README.md).

Keep secrets in local environment files and use synthetic guest data.

## Validate

Run relevant focused checks, then run `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` when applicable.

Run API tests with `python -m pytest apps/api/tests` when API behavior changes.

Include commands and results in your pull request.

## Submit a pull request

Use the pull request template, link related issues, summarize affected apps or packages, and attach screenshots for user interface changes.

Do not include credentials, private guest data, or other sensitive information.