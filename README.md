# AI-VERIFY — Evidence-First Requirement Verification System

> **AI assists. Evidence decides.**

AI-VERIFY is an evidence-first software requirement verification system that determines whether a concrete engineering requirement is supported by sufficient evidence from a Python repository.

It is **not** a generic AI code reviewer.

AI-VERIFY separates repository analysis, verification planning, controlled execution, evidence collection, and deterministic decision-making so that AI can assist the process without becoming the authority that decides whether a requirement is satisfied.

---

## Problem

Traditional approaches often answer questions such as:

* Does the code look correct?
* Do the tests pass?
* Can an AI model judge whether this requirement is implemented?

These signals can be useful, but they are not equivalent to requirement verification.

A test suite may pass while an important path remains untested. A source-code inspection may look correct while runtime behavior contradicts the requirement. An AI model may provide a convincing explanation while reaching the wrong conclusion.

AI-VERIFY therefore treats **evidence as the basis for the final decision**.

---

## Core Principle

```text
Requirement
     ↓
Invariant
     ↓
Repository Analysis
     ↓
Verification Scope
     ↓
Verification Plan
     ↓
Controlled Execution
     ↓
Evidence Collection
     ↓
Deterministic Decision
     ↓
Verification Report
     ↓
JSON + Markdown
```

> **AI assists. Evidence decides.**

---

## Verification Results

| Result                 | Meaning                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| **VERIFIED**           | Sufficient supporting evidence exists and no contradictory evidence was found.           |
| **PARTIALLY VERIFIED** | No contradiction was found, but available evidence is insufficient or inconclusive.      |
| **NOT VERIFIED**       | Contradictory evidence demonstrates that the requirement cannot be considered satisfied. |

### Decision precedence

```text
Contradictory evidence
        ↓
   NOT VERIFIED

No contradiction
        ↓
Insufficient / inconclusive evidence
        ↓
PARTIALLY VERIFIED

Required supporting evidence
+ no contradiction
        ↓
   VERIFIED
```

Contradiction takes precedence over supporting evidence.

Missing evidence alone does **not** mean that the requirement is false.

---

## Evidence Model

AI-VERIFY distinguishes:

* Static evidence
* Test evidence
* Runtime evidence
* Structural evidence

Evidence has an explicit status:

```text
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

Execution state and verification result are deliberately separated.

For example:

```text
Execution fails
      ↓
Execution status = FAILED
      ↓
Evidence = INCONCLUSIVE
```

A failed execution does **not** automatically prove that a requirement is violated.

---

## Architecture

```text
CLI / Interface
      ↓
Verification Service
      ↓
Verification Orchestrator
      ├── Repository Analyzer
      ├── Verification Scope
      └── Verification Planner
              ↓
       Activity Runner
              ↓
      Evidence Pipeline
        ├── Controlled Executor
        ├── Evidence Adapter
        └── Evidence Collector
              ↓
       Deterministic Decision
              ↓
        Verification Run
              ↓
       Verification Report
          ├── JSON
          └── Markdown
```

### Trusted components

* deterministic decision engine
* evidence model
* verification scope rules
* execution policy
* provenance rules
* run package
* report data derived from the run package

### Untrusted inputs

* repository source code
* repository tests
* repository documentation
* repository configuration
* repository instructions
* raw execution output before validation
* AI-generated output
* external textual content

---

## Security and Boundary Model

AI-VERIFY:

* operates on the selected repository
* rejects invalid repository roots
* prevents controlled execution from using a working directory outside the repository
* executes commands with `shell=False`
* validates commands and timeout values
* records execution status and output
* handles timeouts explicitly
* does not silently rewrite user commands
* does not silently modify repository source files
* does not allow AI output to override deterministic decisions

### Important limitation

The controlled execution layer provides **process control and repository-boundary enforcement**.

It is not a complete operating-system sandbox or hostile-code isolation mechanism.

---

## CLI

AI-VERIFY provides a CLI-first interface.

```powershell
python -m ai_verify.cli.main `
  --repository <repository-path> `
  --requirement "<requirement>" `
  --invariant "<invariant>" `
  --run-id "<run-id>" `
  --command <explicit-verification-command>
```

The `--command` argument must be the final CLI option because its remaining arguments are passed directly to the controlled execution layer.

### Example

```powershell
& ".\.venv\Scripts\python.exe" -m ai_verify.cli.main `
  --repository . `
  --requirement "The verification command must complete successfully." `
  --invariant "verification command exits with code 0" `
  --run-id "BUILD-20-MVP-003" `
  --output-directory "reports\BUILD-20-MVP-003" `
  --command ".\.venv\Scripts\python.exe" -m pytest
```

Example result:

```text
Status: PARTIALLY VERIFIED
Rule: INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE
```

This result is intentional: the CLI supplies one evidence-producing activity while the verification plan requires three supporting evidence items.

AI-VERIFY does not manufacture evidence simply to produce a VERIFIED result.

---

## Reports

`ReportWriter` writes JSON and Markdown files into the output directory supplied to it.

With the CLI default:

```text
reports/
├── <RUN-ID>.json
└── <RUN-ID>.md
```

If a run-specific output directory is supplied, for example:

```text
reports/<RUN-ID>/
├── <RUN-ID>.json
└── <RUN-ID>.md
```

JSON preserves structured verification information including:

* run ID
* requirement
* invariant
* status
* decision rule
* rationale
* scope
* verification plan
* evidence
* provenance

Markdown presents the same authoritative information in human-readable form.

> Reports are presentation layers and cannot change authoritative evidence or decisions.

---

## Reproducibility and Provenance

Each verification run has a unique run ID and preserves provenance.

During evaluation, equivalent verification inputs were executed twice:

```text
Run A → VERIFIED
Run B → VERIFIED

Authoritative results → STABLE
Provenance preserved  → PASS
```

This demonstrated stable authoritative verification while retaining separate run identities.

---

## AI Role

AI can assist with:

* requirement interpretation
* invariant extraction
* verification-plan suggestions
* investigation assistance
* natural-language explanations
* report explanations

AI cannot:

* override the deterministic result
* fabricate evidence
* claim a command succeeded when it was not executed
* claim uncovered paths were covered
* modify authoritative evidence
* silently change verification scope
* make the final verification decision

The deterministic verification core remains authoritative.

> AI assistance is an evaluated design capability; the current production CLI does not require an AI model to perform its deterministic verification flow.

---

## Validation

AI-VERIFY was validated through focused experiments, deterministic prototypes, unit tests, integration tests, behavioral scenarios, security tests, and evaluation gates.

### Final regression

```text
122 passed
```

### Test gates

```text
CLI / End-to-End / Reporting
25/25 passed

Evidence & Decision Semantics
28/28 passed

Repository / Scope / Orchestration
30/30 passed

Controlled Execution & Security Boundary
24/24 passed

Run Package / Integrity / Reporting
24/24 passed

Integration
3/3 passed
```

### Behavioral validation

```text
38 behavioral tests
29 passed
9 deliberately failed
```

The nine failures represented deliberately introduced requirement violations in behavioral fixtures. They were used to demonstrate that contradictory behavior can be distinguished from successful verification. They were not failures of the AI-VERIFY production test suite.

### Evaluation gates

```text
MVP Acceptance Criteria       PASS
Three-State Semantics         PASS
Reproducibility & Provenance  PASS
Failure & Safety Behavior     PASS
```

---

## Technology

AI-VERIFY is intentionally lightweight.

* Python 3.12+
* pytest
* Python standard library
* local filesystem
* subprocess-based controlled execution

Design constraints:

* zero-cost development
* no mandatory cloud services
* no mandatory paid AI API
* no GPU requirement
* no vector database
* no dashboard-first architecture
* no uncontrolled autonomous coding
* minimal external dependencies

---

## Current MVP Scope

The completed MVP provides:

* requirement input
* invariant input
* repository analysis
* verification scope
* verification planning
* positive-path activities
* negative-path activities
* edge-case activities
* controlled execution
* structured evidence
* deterministic verification decisions
* three-state results
* run-package preservation
* provenance
* JSON reports
* Markdown reports
* failure handling
* timeout handling
* repository boundary enforcement
* CLI integration
* reproducibility validation

---

## Known Limitations

AI-VERIFY intentionally does not claim to solve every form of software verification.

1. The current repository analyzer focuses on Python files.
2. Verification activities must be explicitly supplied to the CLI/service layer.
3. The MVP does not automatically discover every relevant behavioral path.
4. Controlled subprocess execution is not a complete security sandbox.
5. The integrity mechanism provides lightweight deterministic SHA-256 integrity checking, not production-grade tamper resistance.
6. AI assistance is optional and non-authoritative rather than a fully autonomous verification agent.
7. Multi-language analysis, CI/CD integration, IDE integration, repository-wide campaigns, dashboards, team collaboration, and advanced AI orchestration are outside the current MVP scope.

These are intentional scope boundaries.

---

## Future Direction

Potential future extensions include:

* richer Python path discovery
* additional language support
* GitHub / pull-request integration
* CI verification
* repository-wide verification campaigns
* verification history and search
* IDE integration
* richer evidence visualization
* additional AI-assisted investigation
* stronger execution isolation

These are future possibilities and are **not current MVP capabilities**.

---

## Development Journey

```text
DISCOVER
    ↓
VALIDATE
    ↓
DEFINE
    ↓
DESIGN
    ↓
PROTOTYPE
    ↓
BUILD
    ↓
TEST
    ↓
EVALUATE
    ↓
DOCUMENT
    ↓
DEPLOY / DISTRIBUTE
```

The prototype phase was deliberately closed after the validated decision kernel and run-package/integrity prototypes.

The production implementation was then built incrementally through BUILD-01 to BUILD-20.

---

## Project Status

```text
DISCOVER       ✅ COMPLETE
VALIDATE       ✅ COMPLETE
DEFINE         ✅ COMPLETE
DESIGN         ✅ COMPLETE
PROTOTYPE      ✅ CLOSED
BUILD          ✅ COMPLETE
TEST           ✅ COMPLETE
EVALUATE       ✅ COMPLETE
DOCUMENT       ✅ COMPLETE
DEPLOY         ✅ COMPLETE
PORTFOLIO      🔵 IN PROGRESS
```

---

## Philosophy

> **A convincing explanation is not evidence.**

A requirement should be considered verified because the available evidence supports it under explicit deterministic rules—not because the code looks right, a test suite happens to pass, or an AI model sounds confident.

# AI assists. Evidence decides.
