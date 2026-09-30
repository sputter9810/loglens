# Project Brief

## Project

**Name:** LogLens

## Purpose

LogLens is a command-line application for analysing HTTP server access logs.

Web servers can produce large text-based access logs containing information such as client IP addresses, timestamps, HTTP methods, requested paths, response status codes and response sizes.

Manually inspecting large log files is inefficient. LogLens will convert these raw log entries into structured records and provide commands for filtering, summarising and analysing them.

The initial version is intentionally focused on local log-file analysis rather than live monitoring or server administration.

## Portfolio Objective

LogLens is intended to demonstrate the design, implementation, testing, packaging and documentation of a focused Python command-line application using professional software-engineering practices.

The project should demonstrate:

- Python application and package structure;
- command-line interface design;
- text parsing and structured data modelling;
- file processing;
- validation and error handling;
- separation of responsibilities;
- automated testing;
- continuous integration;
- packaging and installation;
- professional documentation;
- consideration of performance and memory usage.

LogLens is also the first project developed using the portfolio's standard AI-assisted development workflow.

It will therefore be used to evaluate the effectiveness of project briefs, GitHub issues, AI delegation, human review and the Portfolio Definition of Done.

## Discipline

**Primary:** Automation / Tooling

**Secondary:** Systems, where file-processing performance and memory usage are considered.

## Technology

**Primary language:** Python

**Frameworks/libraries:** Prefer the Python standard library for core functionality. Additional libraries may be introduced where they provide clear value and are justified during development.

**Database:** None

**Infrastructure:** GitHub, GitHub Actions and standard Python packaging/tooling.

## Scope

### Included

Version 1 will include:

- reading HTTP access logs from local files;
- support for one clearly documented access-log format;
- parsing supported log entries into structured records;
- identifying and handling malformed or unsupported entries;
- a command-line interface;
- summary statistics for a log file;
- filtering records by useful fields such as HTTP status code and request method;
- aggregation of useful information such as frequently requested paths or active client IP addresses;
- human-readable terminal output;
- automated tests;
- sample log data for development and demonstration;
- installation/package configuration;
- continuous integration;
- user-facing README documentation.

The implementation should make reasonable future extension possible without requiring Version 1 to implement those extensions.

### Explicitly Excluded

Version 1 will not include:

- a graphical user interface;
- a web frontend;
- a web API;
- a database;
- authentication or user accounts;
- cloud deployment;
- remote server administration;
- live remote log monitoring;
- machine-learning analysis;
- alerting or notification systems;
- arbitrary log-format support;
- distributed processing;
- unnecessary frameworks or infrastructure.

These exclusions may only be reconsidered where a future change provides meaningful engineering or portfolio value.

## Functional Requirements

1. LogLens shall accept a local log-file path through its command-line interface.
2. LogLens shall parse entries from the supported HTTP access-log format into structured records.
3. Parsed records shall expose the meaningful fields required by analysis, including where available:
   - client IP address;
   - timestamp;
   - HTTP method;
   - request path;
   - protocol;
   - HTTP response status;
   - response size.
4. LogLens shall handle malformed or unsupported entries without an uncontrolled application failure.
5. LogLens shall provide a summary operation for a supplied log file.
6. Summary output shall include useful aggregate information such as total requests and response-status categories.
7. LogLens shall support filtering by HTTP response status.
8. LogLens shall support filtering by HTTP request method.
9. LogLens shall support ranking or aggregation of frequently occurring values, including requested paths and/or client IP addresses.
10. LogLens shall display results in a readable terminal format.
11. LogLens shall provide useful errors for invalid file paths, invalid command arguments and unsupported input where appropriate.
12. LogLens shall contain sample data allowing its primary functionality to be demonstrated without an external server.
13. Exact CLI command syntax shall be finalised during the CLI-design work and documented in the README.

Functionality beyond these requirements should be treated as future work unless explicitly approved as a scope change.

## Technical Requirements

- Use a supported modern Python version documented by the repository.
- Organise the application as an installable Python package rather than a monolithic script.
- Separate CLI, parsing, data representation and analysis responsibilities where practical.
- Core analysis logic should be usable independently of terminal presentation.
- Prefer iterative file processing where this avoids unnecessary whole-file loading without creating needless complexity.
- Use appropriate type hints for significant interfaces.
- Provide automated tests for parsing, filtering, analysis, malformed input and important error conditions.
- Use deterministic sample/test data.
- Configure GitHub Actions to execute applicable automated quality checks.
- Do not commit secrets, virtual environments, caches, generated build artefacts or machine-specific configuration.
- Dependencies must be justified and proportionate to the project.
- Follow the Portfolio Repository Standard, AI Development Guide and Definition of Done.

## Architecture

LogLens should use a small modular architecture rather than placing all behaviour inside the CLI entry point.

```text
Local Log File
      |
      v
File/Input Layer
      |
      v
Access Log Parser
      |
      v
Structured Log Records
      |
      +------------------+
      |                  |
      v                  v
Filtering            Analysis
      |                  |
      +--------+---------+
               |
               v
          CLI Formatting
               |
               v
            Terminal
```

Expected responsibilities:

- **CLI layer:** argument handling, command selection, user-facing output and exit behaviour.
- **Input layer:** safe iteration over the supplied local file.
- **Parser:** conversion of supported log lines into structured records and identification of malformed input.
- **Domain/model:** representation of a parsed access-log record.
- **Analysis layer:** filtering, aggregation and summary calculations independent of terminal formatting.
- **Presentation:** conversion of results into readable command-line output.

Exact module names may be refined during repository scaffolding. Changes should preserve these responsibility boundaries unless there is a documented reason to alter the architecture.

## Repository Structure

The initial repository should follow standard Python packaging conventions.

A likely structure is:

```text
loglens/
├── .github/
│   └── workflows/
├── samples/
├── src/
│   └── loglens/
├── tests/
├── .gitignore
├── LICENSE
├── PROJECT.md
├── README.md
└── pyproject.toml
```

Additional directories such as `docs/` should only be introduced when useful.

Empty directories should not be created merely to match this example.

## Testing Strategy

Testing will be implemented alongside functionality rather than postponed until project completion.

### Unit Testing

Unit tests should cover:

- valid log-line parsing;
- malformed log-line handling;
- field extraction;
- status filtering;
- method filtering;
- aggregation;
- summary calculations;
- important edge cases.

### CLI Testing

The command-line interface should be tested where practical for:

- valid commands;
- invalid arguments;
- missing files;
- expected exit behaviour;
- representative output.

### Integration Testing

A small number of tests should exercise complete operations against deterministic sample log files.

### Regression Testing

Defects discovered during development should receive regression tests where practical.

### Continuous Integration

GitHub Actions should automatically run applicable tests and quality checks on relevant pushes and/or pull requests.

Coverage may be measured as supporting information, but meaningful behavioural testing takes priority over an arbitrary coverage target.

## Development Constraints

- Follow Portfolio Definition of Done.
- Follow Repository Standard.
- Follow AI Development Guide.
- Do not introduce technologies without justification.
- Do not expand scope without approval.
- AI-completed implementation moves to **Review**, not directly to **Done**.
- GitHub issues are the unit of implementation work.
- Work delegated to Codex must remain bounded by the current issue and this project brief.
- Significant architectural or scope changes require human review before implementation.
- Sam must be able to explain significant architecture and implementation decisions included in the finished repository.

## Milestones

### M1 — Foundation

Establish the repository and minimum application foundation.

Expected outcomes:

- repository configuration;
- Python package structure;
- development/test tooling;
- CLI entry point;
- structured log-record model;
- sample access-log data;
- initial parser;
- initial parser tests.

### M2 — Core Functionality

Implement the primary user-facing analysis functionality.

Expected outcomes:

- summary analysis;
- status filtering;
- method filtering;
- useful aggregation/ranking;
- readable CLI output;
- appropriate command validation and errors.

### M3 — Testing / Quality

Strengthen reliability and engineering quality.

Expected outcomes:

- malformed-input behaviour;
- expanded unit and integration tests;
- CLI tests;
- regression tests where required;
- performance/memory review;
- linting/static quality checks where justified;
- GitHub Actions CI.

### M4 — Portfolio Polish

Prepare the repository for public portfolio presentation.

Expected outcomes:

- installation/package configuration verified;
- README completed;
- usage examples;
- sample output or terminal demonstrations where useful;
- repository metadata/topics;
- final Definition of Done review;
- final human code review;
- project retrospective;
- portfolio-roadmap update.

## Completion Criteria

LogLens is portfolio-ready when:

- all approved Version 1 functional requirements are implemented;
- supported input format is clearly documented;
- malformed input and common user errors are handled appropriately;
- automated tests cover important behaviours and pass;
- CI passes;
- installation and documented commands have been manually verified;
- the repository follows the Portfolio Repository Standard;
- the README explains the problem, installation, usage, testing and relevant design decisions;
- the project contains no secrets, temporary development artefacts or unnecessary generated files;
- significant AI-generated code has been reviewed and is understood by Sam;
- all required Version 1 issues satisfy the Portfolio Definition of Done;
- the repository has completed a final portfolio review;
- `PORTFOLIO_ROADMAP.md` has been updated with the project's outcome and any resulting changes to future plans.
