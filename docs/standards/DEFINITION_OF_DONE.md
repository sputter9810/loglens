# Portfolio Definition of Done

This document defines the minimum standard required for work to be considered
complete across portfolio projects.

The purpose is to ensure that "Done" means the work is functional, tested,
reviewed, documented, and suitable for inclusion in a professional portfolio.

---

## Issue Definition of Done

An issue may move to **Done** when all applicable criteria below are satisfied.

### Implementation

- [ ] The issue's stated requirements have been implemented.
- [ ] All acceptance criteria have been satisfied.
- [ ] The implementation works as intended.
- [ ] No unrelated functionality has been changed unnecessarily.
- [ ] Temporary/debug code has been removed.

### Testing

- [ ] Appropriate automated tests have been added or updated.
- [ ] Existing automated tests continue to pass.
- [ ] Relevant manual testing has been completed where automation is unsuitable.
- [ ] Important edge cases and failure conditions have been considered.

### Code Quality

- [ ] The implementation has been reviewed by Sam.
- [ ] Generated or AI-assisted code is understood before being accepted.
- [ ] Naming and structure are clear and consistent with the project.
- [ ] Obvious duplication or unnecessary complexity has been addressed.
- [ ] No credentials, secrets, personal data, or machine-specific configuration
      have been committed.

### Documentation

- [ ] Relevant documentation has been updated.
- [ ] Public APIs, configuration, or setup changes are documented where required.
- [ ] Significant engineering decisions are explained where useful.

### Repository

- [ ] Changes have been committed with a meaningful commit message.
- [ ] The intended branch contains the completed work.
- [ ] CI checks pass where CI is configured.

---

# Project Definition of Done

A portfolio project may be considered **Complete** when the applicable criteria
below are satisfied.

## Functionality

- [ ] The project's intended core functionality is complete.
- [ ] Major known defects have been resolved or explicitly documented.
- [ ] Error and failure conditions are handled appropriately.

## Testing and Quality

- [ ] An appropriate automated test suite exists.
- [ ] All tests pass.
- [ ] CI automatically verifies the project where appropriate.
- [ ] The final implementation has been manually reviewed.
- [ ] Dependencies and generated files have been cleaned up.

## Documentation

- [ ] `README.md` clearly explains what the project does.
- [ ] The project's purpose and motivation are explained.
- [ ] Technologies used are identified.
- [ ] Installation and setup instructions are provided.
- [ ] Usage instructions or examples are provided.
- [ ] Testing instructions are provided.
- [ ] Important architecture or engineering decisions are explained.
- [ ] Screenshots, demonstrations, or sample output are included where useful.

## Repository Quality

- [ ] `.gitignore` is appropriate for the technology.
- [ ] No secrets, credentials, build artefacts, IDE files, or unnecessary files
      are committed.
- [ ] Repository structure is understandable.
- [ ] Commit history is reasonably clean and descriptive.
- [ ] Repository metadata and description are complete.
- [ ] An appropriate licence is included where the project is intended to be
      publicly reusable.

## Portfolio Review

Before declaring the project complete, answer:

- [ ] Can another developer understand the project without Sam explaining it?
- [ ] Can another developer run the project using only the repository documentation?
- [ ] Can Sam explain the important implementation and architecture decisions?
- [ ] Can Sam explain AI-generated or AI-assisted sections of the project?
- [ ] Does the repository demonstrate the engineering skills it was intended to show?
- [ ] Would this repository be suitable to open during a technical interview?

If the answer to an applicable question is **No**, the project should return to
Review rather than be considered Complete.

---

## Workflow Rule

AI or automated implementation completing successfully does **not** automatically
mean that an issue is Done.

The normal workflow is:

`Ready → In Progress → Review → Done`

AI-assisted work must pass through **Review** before reaching **Done**.

If changes are required during review:

`Review → In Progress`

If work cannot continue because of a dependency or unresolved problem:

`In Progress → Blocked`

Once the blocker is resolved:

`Blocked → Ready` or `Blocked → In Progress`