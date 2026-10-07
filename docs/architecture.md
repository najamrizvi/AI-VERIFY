# AI-VERIFY Architecture

## 1. Overview

AI-VERIFY is an **evidence-first requirement verification system** designed to determine whether a concrete software requirement is supported by sufficient evidence from a Python repository.

The system is intentionally **CLI-first**.

Its core architectural principle is:

> **AI assists. Evidence decides.**

The verification engine does not treat source-code appearance, test pass rate, or AI-generated reasoning as sufficient on their own. Instead, it separates requirement definition, verification planning, evidence collection, deterministic decision-making, and reporting.

---

## 2. Architectural Goal

The architecture is designed to answer a specific question:

> **Does the available evidence support the claim that this requirement is satisfied?**

The system therefore follows this pipeline:

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
Verification Run
     ↓
Verification Report
     ↓
JSON + Markdown
```

Each stage has a defined responsibility.

---

## 3. High-Level Architecture

```text
┌───────────────────────────────────────────────┐
│                    CLI                        │
│         User requirement + invariant          │
│         repository + explicit command         │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              Verification Service             │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│          Verification Orchestrator            │
│                                               │
│  ┌────────────────┐  ┌─────────────────────┐ │
│  │ Repository     │  │ Verification Scope  │ │
│  │ Analyzer       │  │ Builder             │ │
│  └────────────────┘  └─────────────────────┘ │
│                                               │
│  ┌──────────────────────────────────────────┐ │
│  │ Verification Planner                     │ │
│  └──────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│          Verification Activity Runner         │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│               Evidence Pipeline               │
│                                               │
│  Controlled Executor                          │
│        ↓                                      │
│  Evidence Adapter                             │
│        ↓                                      │
│  Evidence Collector                           │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│          Deterministic Decision Engine        │
│                                               │
│  CONTRADICTS → NOT VERIFIED                   │
│  insufficient → PARTIALLY VERIFIED            │
│  sufficient support → VERIFIED                │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              Verification Run                 │
│      Evidence + Decision + Provenance         │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│               Report Builder                  │
└───────────────────────┬───────────────────────┘
                        │
                 ┌──────┴──────┐
                 ▼             ▼
              JSON          Markdown
```

---

## 4. Architectural Layers

### 4.1 Interface Layer

The current interface is the command-line interface.

```text
src/ai_verify/cli/main.py
```

The CLI accepts:

* repository path
* requirement
* invariant
* run ID
* optional output directory
* explicit verification command

The CLI does not implement verification logic itself.

Instead, it constructs the verification activity and delegates execution to the verification service.

This keeps the interface separate from the verification core.

---

### 4.2 Service Layer

```text
src/ai_verify/verification/service.py
```

`VerificationService` provides the main application-level entry point.

Its responsibility is to coordinate:

```text
Orchestrator
     ↓
Verification Run
     ↓
Report Builder
     ↓
Report Serialization
```

The service does not independently determine whether a requirement is verified.

The authoritative decision remains inside the deterministic verification pipeline.

---

### 4.3 Orchestration Layer

```text
src/ai_verify/verification/orchestrator.py
```

The orchestrator coordinates the major verification stages:

1. repository analysis
2. scope construction
3. verification planning
4. activity execution
5. evidence collection
6. verification run construction

Conceptually:

```text
Repository
    ↓
RepositoryAnalyzer
    ↓
VerificationScope
    ↓
VerificationPlan
    ↓
VerificationActivityRunner
    ↓
Evidence
    ↓
VerificationRun
```

The orchestrator coordinates components rather than duplicating their responsibilities.

---

## 5. Repository Analysis

```text
src/ai_verify/repository/analyzer.py
```

The repository analyzer identifies Python files within the selected repository.

The analyzer:

* validates the repository root
* stays within the selected repository
* discovers Python files
* produces deterministic relative paths
* ignores known environment/cache directories
* does not execute repository code
* does not invoke AI
* does not modify repository files

Ignored directories include common development environments and caches such as:

```text
.git
.hg
.svn
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
node_modules
```

The analyzer provides structural information for later verification stages.

It does not decide whether a requirement is satisfied.

---

## 6. Verification Scope

```text
src/ai_verify/verification/scope.py
```

The scope builder converts repository analysis into a structured verification scope.

Each discovered file is represented with information such as:

* relative path
* absolute path
* role

The current implementation distinguishes basic source and test roles.

This creates an explicit boundary around the repository material considered during verification.

The scope is preserved in the verification run and report.

---

## 7. Verification Planning

```text
src/ai_verify/verification/planner.py
```

The planner creates a structured verification plan.

The MVP plan contains three conceptual verification categories:

```text
Positive Path
Negative Path
Edge Case
```

The planner also establishes the required supporting evidence count.

In the current MVP:

```text
Required supporting evidence = 3
```

This requirement is deliberate.

The system does not weaken its evidence threshold merely because a single command succeeds.

The plan therefore represents **what evidence is required**, not evidence that has already been collected.

---

## 8. Verification Activities

```text
src/ai_verify/verification/activity_runner.py
```

A verification activity describes an executable evidence-producing operation.

Activities contain information such as:

* activity ID
* execution request
* evidence ID
* description
* success evidence status
* failure evidence status

The activity runner executes the supplied activities in a deterministic order.

Important distinction:

```text
Verification Plan
       ≠
Verification Activity
       ≠
Evidence
```

A planned activity is not evidence until it has actually been executed and adapted into a structured evidence observation.

---

## 9. Controlled Execution

```text
src/ai_verify/core/execution.py
src/ai_verify/verification/executor.py
```

The controlled execution layer executes explicit commands supplied by the verification workflow.

Execution uses:

```python
shell=False
```

The execution request contains:

* command
* working directory
* timeout

The executor validates:

* repository root
* working directory
* command
* timeout

The working directory must remain within the selected repository.

Execution states are:

```text
COMPLETED
FAILED
TIMED_OUT
```

### Execution state is not verification status

This distinction is fundamental.

```text
ExecutionStatus
    ≠
EvidenceStatus
    ≠
VerificationStatus
```

For example:

```text
Process exits with non-zero code
        ↓
Execution = FAILED
        ↓
Evidence = INCONCLUSIVE
```

A failed command does not automatically prove that the requirement is violated.

---

## 10. Evidence Pipeline

The evidence pipeline connects execution to structured evidence.

```text
ExecutionRequest
       ↓
ControlledExecutor
       ↓
ExecutionResult
       ↓
ExecutionEvidenceAdapter
       ↓
EvidenceObservation
       ↓
EvidenceCollector
       ↓
Evidence
```

### Controlled Executor

Produces authoritative execution information such as:

* command
* working directory
* execution status
* exit code
* stdout
* stderr
* timeout configuration

### Evidence Adapter

Converts execution results into verification evidence.

For completed executions:

```text
exit code = 0
      ↓
success status
```

```text
exit code ≠ 0
      ↓
failure status
```

For failed or timed-out executions:

```text
FAILED / TIMED_OUT
      ↓
INCONCLUSIVE
```

### Evidence Collector

Validates the evidence observation and creates the structured evidence object.

Evidence contains provenance information linking the observation to its source and, where applicable, execution identity.

---

## 11. Evidence Model

The core evidence model uses three statuses:

```text
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

It also distinguishes evidence types:

```text
STATIC
TEST
RUNTIME
STRUCTURAL
```

This allows the system to preserve the difference between:

* what was observed statically
* what was demonstrated by tests
* what happened at runtime
* what structural information was discovered

Evidence is treated as authoritative input to the deterministic decision engine.

---

## 12. Deterministic Decision Engine

```text
src/ai_verify/core/decision.py
```

The decision engine is intentionally deterministic.

It does not use AI to make the final classification.

The decision rules are:

### Rule 1 — Contradiction wins

If contradictory evidence exists:

```text
CONTRADICTS
     ↓
NOT VERIFIED
```

### Rule 2 — Insufficient evidence

If no contradiction exists but the required amount of supporting evidence has not been reached:

```text
insufficient support
       ↓
PARTIALLY VERIFIED
```

### Rule 3 — Sufficient support

If the required supporting evidence exists and no contradiction exists:

```text
sufficient support
       ↓
VERIFIED
```

This produces three deterministic states:

```text
VERIFIED
PARTIALLY VERIFIED
NOT VERIFIED
```

AI cannot override this result.

---

## 13. Verification Run

```text
src/ai_verify/core/run_package.py
src/ai_verify/verification/run.py
```

The verification run is the structured representation of a completed verification process.

It preserves:

* run ID
* requirement
* invariant
* scope
* verification plan
* evidence
* deterministic decision
* provenance
* schema version

The run package is the authoritative structured record from which reporting information is derived.

---

## 14. Integrity

```text
src/ai_verify/core/integrity.py
```

AI-VERIFY provides deterministic integrity checking for verification run packages.

The current implementation:

1. serializes the run into a canonical representation
2. creates a SHA-256 hash
3. compares the calculated hash with an expected hash

This provides lightweight integrity validation.

It is intentionally **not described as a production-grade cryptographic tamper-resistance system**.

---

## 15. Reporting

```text
src/ai_verify/reporting/
```

Reporting is separated from verification.

The reporting pipeline is:

```text
VerificationRun
       ↓
VerificationReportBuilder
       ↓
VerificationReport
       ↓
serialize_report()
       ↓
ReportWriter
       ├── JSON
       └── Markdown
```

The report preserves authoritative information from the verification run.

The writer does not:

* recalculate the verification decision
* modify evidence
* change the verification status
* introduce new verification logic

Reports are therefore presentation layers over the authoritative verification result.

---

## 16. JSON Reporting

JSON provides structured machine-readable output.

It includes:

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

JSON is useful for:

* automation
* future integrations
* CI systems
* programmatic inspection
* reproducibility

---

## 17. Markdown Reporting

Markdown provides a human-readable representation of the same verification result.

It presents:

* verification status
* decision rule
* rationale
* requirement
* invariant
* scope
* verification plan
* evidence
* provenance

Markdown is intended for engineers and project documentation.

---

## 18. Trust Boundaries

AI-VERIFY deliberately separates trusted and untrusted information.

### Trusted

```text
Deterministic decision rules
Evidence schema
Execution policy
Scope rules
Provenance rules
Run package structure
```

### Untrusted

```text
Repository source
Repository tests
Repository documentation
Repository configuration
Raw execution output before adaptation
AI output
External text
```

The purpose of this separation is to prevent untrusted content from silently becoming authoritative verification logic.

---

## 19. AI Boundary

AI assistance is intentionally subordinate to deterministic verification.

AI may assist with:

```text
Requirement interpretation
Invariant extraction
Verification planning
Investigation
Explanation
Reporting assistance
```

AI may not:

```text
Override the decision
Fabricate evidence
Fabricate execution
Claim uncovered paths were covered
Modify authoritative evidence
Change verification scope silently
Declare the final verification result
```

This produces the architectural relationship:

```text
             AI
              │
              │ assists
              ▼
     ┌──────────────────┐
     │ Verification     │
     │ Workflow         │
     └────────┬─────────┘
              │
              ▼
       Structured Evidence
              │
              ▼
   Deterministic Decision
              │
              ▼
      Authoritative Result
```

The current production CLI does not require an AI model to perform the deterministic verification flow.

---

## 20. Repository Boundary

AI-VERIFY operates only within the repository explicitly supplied to the verification workflow.

The execution layer prevents the working directory from escaping the selected repository.

This protects the verification workflow from accidentally operating on unrelated directories.

The repository boundary is therefore part of the verification architecture rather than an optional UI feature.

---

## 21. Failure and Timeout Handling

Execution failures and timeouts are explicitly represented.

```text
Command execution
       │
       ├── COMPLETED
       │
       ├── FAILED
       │
       └── TIMED_OUT
```

Failed and timed-out executions are adapted into:

```text
INCONCLUSIVE
```

unless structured contradictory evidence is supplied through an appropriate evidence path.

This prevents a technical execution problem from being incorrectly interpreted as proof that the requirement itself is violated.

---

## 22. CLI-First Design

The current MVP intentionally uses a CLI rather than a web dashboard.

The interface is:

```text
User
 ↓
PowerShell / Terminal
 ↓
AI-VERIFY CLI
 ↓
Verification Service
 ↓
Verification Engine
 ↓
JSON + Markdown Reports
```

This choice keeps the project focused on its core engineering problem:

> evidence-first requirement verification.

A future web interface, dashboard, CI integration, IDE integration, or GitHub integration can be placed above the existing service and verification layers without changing the fundamental decision architecture.

These interfaces are **future possibilities, not current MVP capabilities**.

---

## 23. End-to-End Example

A simplified verification run looks like this:

```text
User provides:

Requirement
"The order must not be marked as paid unless
the corresponding payment has completed."

Invariant
"order.status == 'paid' implies
payment.status == 'completed'"
```

Then:

```text
Repository Analysis
        ↓
Scope
        ↓
Verification Plan
        ↓
Activities
        ↓
Controlled Execution
        ↓
Evidence
        ↓
Deterministic Decision
        ↓
Verification Run
        ↓
JSON + Markdown Report
```

If contradictory evidence demonstrates that an order becomes paid after an unsuccessful payment:

```text
Contradictory evidence
        ↓
NOT VERIFIED
```

If there is no contradiction but evidence is incomplete:

```text
Insufficient evidence
        ↓
PARTIALLY VERIFIED
```

If the required supporting evidence is present and no contradiction exists:

```text
Sufficient evidence
        ↓
VERIFIED
```

---

## 24. Architectural Invariants

The following principles are treated as architectural invariants:

1. Requirement and evidence are separate concepts.
2. Verification plans do not count as evidence.
3. Execution status does not equal verification status.
4. Failed execution does not automatically equal contradiction.
5. Contradictory evidence takes precedence.
6. Missing evidence does not automatically mean failure.
7. AI cannot override the deterministic result.
8. Reports cannot change authoritative decisions.
9. Verification scope must remain explicit.
10. Execution must remain within the selected repository boundary.
11. Explicit user commands must not be silently rewritten.
12. Verification provenance must be preserved.

---

## 25. Current Architectural Limitations

The current architecture intentionally has several boundaries:

* repository analysis currently focuses on Python files
* activities must be explicitly supplied
* automatic discovery of every behavioral path is not guaranteed
* controlled execution is not a complete operating-system sandbox
* integrity checking is lightweight
* AI assistance is optional rather than mandatory
* the current interface is CLI-first
* multi-language analysis is outside the MVP
* web dashboards are outside the MVP
* CI/CD and GitHub integration are outside the MVP

These limitations are deliberate scope decisions rather than unfinished core architecture.

---

## 26. Architectural Summary

AI-VERIFY is structured around a simple principle:

```text
Do not ask:
"Does the code look correct?"

Ask:
"What evidence supports the requirement?"
```

The architecture enforces that principle by separating:

```text
Requirement
    ≠
Verification Plan
    ≠
Evidence
    ≠
Decision
```

and:

```text
Execution Status
    ≠
Evidence Status
    ≠
Verification Status
```

The result is a verification system where:

> **AI can assist the investigation, but evidence and deterministic rules decide the outcome.**
