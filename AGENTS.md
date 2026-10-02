# Repository Guidelines
This project is a real-time hotel voice receptionist that supports three core guest functions:

1. Check-in
2. Check-out
3. Uber booking

## Project Organization

### Architecture

The product is a monorepo with a Next.js web application and a FastAPI backend.
Keep application responsibilities in their respective apps and put reusable code in shared packages.
Do not use a plugin architecture.

### Tech stack

- Package manager: pnpm
- Repository type: monorepo
- Language: TypeScript (frontend), Python (backend)
- Node version: 22
- Frontend framework: Next.js 15
- Backend services: Supabase, Azure Foundry, FastAPI, Microsoft Agent Framework, and Azure OpenAI models
- Testing: Vitest

### Folder Structure

The repository currently contains the specification scaffold and the first feature specification.
As the application is implemented, use the following layout:

```text
apps/
  web/                        Next.js guest and staff web experience
  api/                        FastAPI backend and API endpoints
packages/
  design-system/              Shared web UI components and styles
  shared/                     Reusable frontend types and utilities
docs/                         Product and engineering documentation
specs/                        Feature specifications and checklists
.specify/                     Spec Kit templates, scripts, and project memory
```

Keep service integrations behind clear interfaces so providers can change without coupling application features to provider details.

## Build, Test, and Development Commands

- Use pnpm for all workspace commands.

| Command | Purpose |
| --- | --- |
| `pnpm install` | Install workspace dependencies. |
| `pnpm dev` | Run the web application locally. |
| `pnpm build` | Build the application for production. |
| `pnpm start` | Serve the production build. |
| `pnpm lint` | Check code quality rules. |
| `pnpm typecheck` | Validate TypeScript types. |
| `pnpm test` | Run the Vitest suite. |

## Coding Style & Naming Conventions

- Use strict TypeScript and ES modules.
- Use `.tsx` for React routes and components, and `.ts` for services, contracts, and utilities.
- Use PascalCase for classes, types, and public members; use camelCase for local variables, parameters, and private methods.
- Use ALL_CAPS with underscores for JavaScript and TypeScript global constants.
- Use snake_case for Python functions, methods, and variables.
- Prefer package boundaries over cross-directory shortcuts.
- Keep shared packages focused and independent of app-specific behavior.
- Keep mocks behind service interfaces so providers can change without altering application behavior.

## Testing Guidelines

- Use Vitest for automated tests.
- Name shared package and service contract tests `*.contract.test.ts`.
- Add focused tests beside the code they validate.
- Run `pnpm test` before submitting changes; also run `pnpm lint` and `pnpm typecheck` when TypeScript changes.

## Agent Workflow

- Use a small team of two or three agents for substantial feature work.
  A lead coordinates Spec Kit artifacts and integration, a specification reviewer checks requirements and design consistency, and an implementer handles the code.
  Combine roles for small changes and add agents only when they have independent work.
- The lead owns the feature scope and final decisions.
  Assign one writer per artifact or code area, and give each agent the file paths, acceptance criteria, dependencies, and expected handoff.
- Follow the Spec Kit lifecycle for new features: `$speckit-specify`, `$speckit-clarify` when important questions remain, `$speckit-plan`, `$speckit-tasks`, then `$speckit-analyze`.
  Use the active feature path in `.specify/feature.json` to find its artifacts.
- Before implementation, have the reviewer check that the spec, plan, and tasks agree and that tasks have clear acceptance criteria.
  Resolve gaps in the relevant Spec Kit artifact before coding.
- Delegate implementation from the approved task list with `$speckit-implement`.
  Keep implementation work aligned to task boundaries and shared package/API contracts, and coordinate dependencies before parallel changes.
- After implementation, use `$speckit-converge` to compare the code with the spec and tasks.
  Add remaining work to the task list and implement it before reporting completion.
- Use an isolated worktree for implementation work when available.
  Inspect relevant apps, packages, and documentation first, and reproduce bugs in the closest practical end-to-end flow before fixing them.
- Keep changes within the requested behavior and preserve clear app, package, and API boundaries.
  Run focused checks first, then `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` when applicable.
- Report changed areas, completed Spec Kit stages, agent handoffs, verification results, and remaining risks.
  Use `.codex/agents/*.toml` for project agents and `.agents/skills/*/SKILL.md` for reusable workflows.

## Version Control, Commits, and Pull Requests

- Use an isolated worktree named `wt-<project>-<description>-<date>`.
- Link each worktree to a branch named `feature/<description>`, `fix/<description>`, or `update/<description>`.
- Use concise, imperative commit messages such as `Add reservation contract tests` or `Fix demo auth redirect`.
- Pull requests must describe the change, list affected apps or packages, link issues, include UI screenshots, and list verification commands.

## Security & Configuration Tips

- Development demo sign-in uses `admin` / `admin` only for local use.
- Do not treat these credentials as production-ready.
- Keep provider-specific credentials out of source control and route new integrations through service interfaces.
