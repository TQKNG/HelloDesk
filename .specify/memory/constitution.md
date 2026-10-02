<!--
Sync Impact Report
Version change: unratified template -> 1.0.0 (initial adoption)
Modified principles: template placeholders -> I. Code Quality; II. Maintainable Design;
  III. Meaningful Testing; IV. Integration Confidence; V. Simplicity and Safe Change
Added sections: Quality Standards; Development Workflow
Removed sections: none
Follow-up TODOs: Confirm the original ratification date and replace TODO(RATIFICATION_DATE).
-->
# HelloDesk Constitution

## Core Principles

### I. Code Quality
Changes MUST be correct, readable, and consistent with established project conventions.
Contributors MUST address relevant lint, type, and static analysis findings introduced by
their changes. Names and abstractions MUST make behavior clear to the next maintainer.
These rules keep defects visible and reduce the cost of future changes.

### II. Maintainable Design
Code MUST keep responsibilities cohesive and dependencies explicit. Shared behavior MUST
have one clear owner instead of accumulating divergent copies. Contributors MUST prefer
the simplest design that meets current requirements, while preserving clear seams for
known extension points. This limits coupling and avoids speculative complexity.

### III. Meaningful Testing
Every behavior change MUST include automated tests at the level where that behavior is
defined. Tests MUST cover expected results and relevant failure or boundary cases. A bug
fix MUST include a regression test that fails before the fix when practical. Tests make
behavior reproducible and protect against regressions.

### IV. Integration Confidence
Changes that cross module, API, persistence, or user interface boundaries MUST be checked
with integration or end-to-end tests for the affected contract. Unit tests alone are
insufficient when correctness depends on collaboration between components. This catches
failures that isolated tests cannot reveal.

### V. Simplicity and Safe Change
Contributors MUST keep changes focused, preserve existing behavior unless requirements say
otherwise, and avoid unrelated cleanup in the same change. Public contracts and data
formats MUST be changed deliberately, with compatibility and migration needs documented.
Small, explicit changes are easier to review, validate, and safely evolve.

## Quality Standards

Before a change is considered complete, contributors MUST run the relevant checks available
in the repository and report any checks they could not run. Tests MUST be deterministic and
independent of external services unless the test explicitly exercises an integration
boundary. Security-sensitive values MUST NOT be committed; configuration examples MUST use
placeholders.

## Development Workflow

Pull requests MUST explain the user-visible or maintenance impact, summarize the design,
and list validation performed. Reviewers MUST check correctness, test coverage, readability,
and alignment with these principles. Changes to shared interfaces MUST identify affected
consumers and include suitable compatibility checks.

## Governance

This constitution guides implementation, review, and planning decisions. Amendments MUST
update this document and its version together. Versioning follows semantic intent: MAJOR
for incompatible governance changes, MINOR for new or materially expanded principles, and
PATCH for wording clarifications that do not change requirements. Every pull request MUST
be reviewed for compliance; any exception MUST state its reason and scope in the pull
request. Amendments MUST record the amendment date, and the original ratification date MUST
be retained.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-10-02
