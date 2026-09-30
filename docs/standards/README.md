# Portfolio Engineering Standards

This directory contains the shared development standards used across Sam Briggs' software engineering portfolio.

These documents provide consistent project planning, implementation, AI-assisted development, review, and completion practices across repositories.

They are intended to provide enough context for work to remain consistent when projects are developed across different ChatGPT conversations, Codex sessions, repositories, and development periods.

---

## Development Model

Portfolio development follows three levels of specification:

```text
Portfolio Standards
        ↓
     PROJECT.md
        ↓
   GitHub Issue
        ↓
 Implementation
        ↓
      Review
        ↓
       Done
```

### Portfolio Standards

The documents in this directory define practices shared across projects.

### Project Specification

Each substantial portfolio project should contain a `PROJECT.md` created from `PROJECT_BRIEF_TEMPLATE.md`.

It defines the project's objectives, scope, architecture, technologies, requirements, testing strategy, and completion criteria.

### Implementation Issues

Individual units of work are specified through GitHub Issues using the shared issue structure.

Issues should contain enough information for the work to be implemented and reviewed without relying on undocumented conversation context.

---

## Documents

### `DEFINITION_OF_DONE.md`

Defines the requirements for an issue or project to be considered complete.

This includes implementation, testing, review, documentation, repository quality, and portfolio readiness.

### `PROJECT_BRIEF_TEMPLATE.md`

Template used when beginning a new portfolio project.

The completed version becomes the project's `PROJECT.md` and acts as the authoritative project-level specification.

### `ISSUE_TEMPLATE.md`

Defines the standard structure for implementation tasks.

Issues describe:

- objectives;
- context;
- requirements;
- acceptance criteria;
- technical constraints;
- AI/delegation instructions.

### `AI_DEVELOPMENT_GUIDE.md`

Defines how ChatGPT, Codex, and other AI-assisted development tools should be used.

AI may assist substantially with implementation, but architecture, scope, review, and final acceptance remain human decisions.

### `REPOSITORY_STANDARD.md`

Defines expected repository structure and engineering practices including:

- documentation;
- source organisation;
- testing;
- dependencies;
- CI;
- Git practices;
- secrets;
- AI-generated work;
- portfolio presentation.

---

## GitHub Project Workflow

Portfolio work is tracked through the **Portfolio Development** GitHub Project.

The standard workflow is:

```text
Backlog
   ↓
Ready
   ↓
In Progress
   ↓
Review
   ↓
Done
```

Work may move to **Blocked** when progress cannot continue.

If review identifies required changes:

```text
Review → In Progress
```

AI-assisted implementation should normally end at **Review**.

Only reviewed work should move to **Done**.

---

## Project Metadata

### Status

- Backlog
- Ready
- In Progress
- Review
- Blocked
- Done

### Priority

- P0 — Critical
- P1 — High
- P2 — Normal
- P3 — Low

### Size

- XS — Less than approximately one hour
- S — Approximately 1–3 hours
- M — Approximately one development evening
- L — Multiple development evenings

Work significantly larger than `L` should normally be decomposed.

### Type Labels

Each GitHub issue should normally have one primary type label describing the nature of the work:

- `type:feature` — new functionality or behaviour;
- `type:bug` — correction of incorrect behaviour;
- `type:test` — testing-focused work;
- `type:docs` — documentation-focused work;
- `type:refactor` — internal restructuring without an intentional behaviour change;
- `type:devops` — CI/CD, build, deployment, or development infrastructure;
- `type:research` — investigation required before an implementation decision.

### Discipline

Current portfolio disciplines are:

- Frontend
- Backend
- Full Stack
- Data Engineering
- Database Engineering
- Systems
- Automation / Tooling
- DevOps / Infrastructure

Technology is tracked separately from engineering discipline.

---

## Ownership

Issues may identify their expected implementation approach:

- `owner:sam` — primarily manual development;
- `owner:ai` — suitable for substantial AI implementation;
- `owner:pair` — intended for collaborative human/AI development.

Ownership describes the expected development process, not responsibility for the final result.

All merged portfolio work remains subject to human review.

---

## Technology

Technology labels describe implementation technologies rather than engineering disciplines.

Initial technology labels include:

- `tech:python`
- `tech:java`
- `tech:javascript`
- `tech:sql`
- `tech:cpp`
- `tech:html-css`

Additional technology labels should only be introduced when they provide useful filtering or portfolio information.

---

## Guiding Principle

These standards exist to preserve consistency and engineering quality without creating unnecessary process.

Documentation should carry important decisions between development sessions so that projects do not depend on the memory or context of a particular conversation.

When starting or continuing a project in a new AI session, provide the relevant portfolio standards, the project's `PROJECT.md`, and the current GitHub issue.

Those documents should provide the context required to continue development consistently.
