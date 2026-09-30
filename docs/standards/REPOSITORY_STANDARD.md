# Portfolio Repository Standard

This document defines the baseline structure, quality expectations, and conventions for repositories created as part of Sam Briggs' software engineering portfolio.

The standard exists to keep projects consistent while allowing each repository to use structures appropriate to its technology and purpose.

This document should be read alongside:

- `DEFINITION_OF_DONE.md`
- `PROJECT_BRIEF_TEMPLATE.md`
- `AI_DEVELOPMENT_GUIDE.md`
- `ISSUE_TEMPLATE.md`

---

## 1. Core Principles

Portfolio repositories should be:

- understandable without verbal explanation;
- straightforward for another developer to run;
- appropriately tested;
- intentionally structured;
- documented sufficiently to explain important decisions;
- free from unnecessary generated or development artefacts;
- representative of professional software engineering practice.

Consistency is encouraged, but project-specific engineering decisions take priority over blindly following a template.

Do not create empty directories, unnecessary configuration, or documentation solely to satisfy this standard.

---

## 2. Recommended Repository Structure

A typical repository may resemble:

```text
project-name/
├── .github/
│   └── workflows/
├── docs/
├── src/
├── tests/
├── .gitignore
├── LICENSE
├── PROJECT.md
└── README.md
```

This is a guideline rather than a mandatory structure.

Technology conventions should be followed where they provide a more natural structure.

Examples include Maven/Gradle layouts for Java, standard Python package layouts, or framework-specific frontend structures.

---

## 3. Required Files

### README.md

Every public portfolio repository must contain a useful README.

At minimum it should explain:

- what the project is;
- what problem it solves;
- why it was built;
- the main technologies used;
- how to install or configure it;
- how to run it;
- how to run its tests.

Where appropriate, it should also include:

- screenshots;
- demonstrations;
- sample commands;
- API examples;
- architecture diagrams;
- performance results;
- limitations;
- future development opportunities.

The README is written primarily for someone discovering the repository for the first time.

### PROJECT.md

Every substantial portfolio project should contain a `PROJECT.md`.

It should be created from `PROJECT_BRIEF_TEMPLATE.md` before significant implementation begins.

`PROJECT.md` defines:

- the project's purpose;
- portfolio objective;
- discipline;
- technology choices;
- scope;
- requirements;
- architecture;
- testing strategy;
- milestones;
- completion criteria.

It acts as the authoritative project-level specification.

Material changes to project scope or architecture should be reflected in this document.

### .gitignore

Every repository must use an appropriate `.gitignore`.

It should exclude applicable:

- build output;
- dependency directories;
- IDE-specific files;
- temporary files;
- logs;
- local configuration;
- environment files;
- generated artefacts;
- secrets and credentials.

Files should not be ignored merely to hide repository clutter that should instead be removed.

### LICENSE

Public repositories intended for reuse should include an appropriate licence.

A licence is optional when licensing would not make sense for the project's purpose.

Do not add a licence automatically without considering the intended use of the repository.

---

## 4. Source Code

Source code should follow conventions appropriate to its language and framework.

Code should favour:

- meaningful naming;
- small and understandable components;
- clear responsibility boundaries;
- appropriate error handling;
- minimal unnecessary duplication;
- maintainability over cleverness.

Comments should explain reasoning, constraints, or non-obvious behaviour.

Comments should not simply restate obvious code.

---

## 5. Dependencies

Dependencies should be introduced intentionally.

Before adding a dependency, consider whether:

1. the functionality is genuinely required;
2. the standard library or existing dependencies already provide it;
3. the dependency is maintained and appropriate;
4. the additional complexity is justified.

AI-assisted development must not introduce frameworks or dependencies solely for convenience without considering these points.

Dependency versions should be managed through the standard tooling for the technology.

---

## 6. Configuration and Secrets

Secrets must never be committed.

This includes:

- passwords;
- API keys;
- private SSH keys;
- access tokens;
- database credentials;
- production secrets.

Where configuration is required, use an appropriate mechanism such as environment variables or external configuration.

Example configuration may be committed where useful, for example:

```text
.env.example
```

Example files must contain placeholders rather than real credentials.

---

## 7. Testing

Testing should be proportional to the project's purpose and risk.

Projects should use automated testing where meaningful.

Depending on the project, this may include:

- unit testing;
- integration testing;
- API testing;
- acceptance/end-to-end testing;
- performance testing;
- static analysis.

Tests should focus on meaningful behaviour rather than artificially increasing test counts or coverage percentages.

Bug fixes should normally include a regression test where practical.

AI-generated tests must be reviewed to ensure that they verify useful behaviour rather than simply reproduce the implementation.

---

## 8. Continuous Integration

Portfolio projects should use CI where it provides meaningful value.

A typical CI workflow should verify applicable:

- compilation/build;
- automated tests;
- linting;
- static analysis.

CI should run automatically on relevant pushes and/or pull requests.

A failing CI pipeline should not be bypassed simply to mark work complete.

---

## 9. Documentation

Documentation should explain information that cannot be easily inferred from the source code.

Additional documentation may be stored under:

```text
docs/
```

Useful subjects include:

- architecture;
- database design;
- API behaviour;
- significant technical decisions;
- benchmarking methodology;
- deployment;
- complex algorithms.

Avoid creating documentation that merely duplicates source code or the README.

---

## 10. Git and Commit Practices

Commits should represent meaningful units of work.

Commit messages should be concise and descriptive.

Prefer:

```text
Add validation for malformed log entries
Implement URL expiry handling
Add integration tests for user registration
Refactor file indexing service
```

Avoid:

```text
changes
stuff
fix
update
working now
```

Commits do not need to be artificially small, but unrelated changes should not be bundled together unnecessarily.

Do not rewrite history merely to make development appear more perfect than it was.

---

## 11. Branches and Pull Requests

Small projects may use a simple development workflow.

For isolated, low-risk work, direct development may be appropriate.

For larger features or AI-delegated work, prefer:

```text
main
  └── feature/<descriptive-name>
```

Examples:

```text
feature/log-parser
feature/query-benchmarking
fix/invalid-input-handling
```

Pull requests should be used when they provide useful review boundaries, particularly for significant or AI-generated changes.

Do not create branches or pull requests solely for ceremony.

---

## 12. GitHub Issues

Issues represent independently understandable units of work.

Issues should follow `ISSUE_TEMPLATE.md` and include:

- objective;
- context;
- requirements;
- acceptance criteria;
- relevant technical notes;
- AI/delegation instructions where applicable.

Issues should normally be small enough to complete and review independently.

Work too large to describe clearly in one issue should be decomposed.

---

## 13. AI-Assisted Development

AI-assisted work must follow `AI_DEVELOPMENT_GUIDE.md`.

AI may assist with implementation, testing, debugging, documentation, refactoring, research, and configuration within approved project boundaries.

AI-generated code is not considered reviewed simply because it compiles or passes tests.

Sam remains responsible for:

- understanding merged code;
- reviewing significant changes;
- approving architecture;
- approving scope changes;
- determining whether work satisfies the Definition of Done.

AI-completed work normally moves to **Review**, not directly to **Done**.

---

## 14. Repository Presentation

Before a repository is treated as portfolio-ready:

- its GitHub description should clearly describe the project;
- appropriate repository topics should be added;
- the README should render correctly;
- screenshots or demonstrations should work where applicable;
- setup instructions should be tested;
- CI should be passing;
- obvious temporary files and debug output should be removed.

The repository should be understandable to someone who encounters it without additional context.

---

## 15. Exceptions

This standard should support engineering judgement rather than replace it.

A project may deviate from this standard when:

- its technology has stronger established conventions;
- a requirement does not apply;
- following the standard would add unnecessary complexity;
- the project brief explicitly defines another approach.

Significant deviations should be intentional and, where useful, documented.

---

## Final Principle

The objective is not to make every repository identical.

The objective is to make every repository demonstrate deliberate, understandable, and professional software engineering.
