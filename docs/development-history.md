# AI-VERIFY Development History

## 1. Purpose

This document records the development history of **AI-VERIFY — Evidence-First Requirement Verification System**.

It explains how the project progressed from problem discovery through validation, architecture, implementation, testing, evaluation, and documentation.

The project was developed using an evidence-driven workflow rather than beginning with implementation immediately.

The guiding principle throughout development was:

> **AI assists. Evidence decides.**

---

## 2. Development Philosophy

The project followed a controlled development lifecycle:

```text id="5u4m3a"
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
DEPLOY / PORTFOLIO
```

The development process deliberately avoided:

* premature coding
* unnecessary redesign
* dashboard-first development
* mandatory paid AI services
* uncontrolled scope expansion
* AI-controlled verification decisions
* claims unsupported by evidence

The project prioritized a smaller, validated system over a larger unfinished platform.

---

## 3. DISCOVER

The project began by identifying a specific problem:

> How can a system determine whether a software requirement is actually satisfied by implementation?

Existing approaches often rely heavily on:

* source-code appearance
* test pass rates
* static analysis
* AI-generated code opinions

These approaches do not necessarily answer whether a specific requirement is actually demonstrated by sufficient evidence.

The project therefore focused on an evidence-first model.

The core positioning became:

> **AI-VERIFY is an evidence-first requirement verification system, not a generic AI code reviewer.**

---

## 4. Initial Problem Definition

The central verification distinction was established:

```text id="q4z0y1"
Requirement satisfied
        ≠
Code looks correct
```

and:

```text id="d2j8ml"
Requirement satisfied
        ≠
All tests passed
```

The project instead focused on:

```text id="e8x4ob"
Requirement
    ↓
Evidence
    ↓
Deterministic Evaluation
    ↓
Verification Result
```

This became the foundation for the rest of the project.

---

## 5. VALIDATE

Before production implementation, the verification concept was experimentally validated.

The goal was to determine whether the proposed evidence-first approach could identify requirement satisfaction and violation in realistic repository scenarios.

The validation phase included G-01, G-01A, local AI evaluation, and G-02.

---

## 6. G-01 — Authorization Verification Experiment

The first major experiment used the requirement:

```text id="6w5q9x"
An authenticated user must only be able to retrieve
an invoice belonging to that user.
```

Invariant:

```text id="0d7j0m"
invoice.user_id == authenticated_user.id
```

The experiment tested whether different forms of evidence were sufficient to establish authorization correctness.

It demonstrated that:

* test pass rate alone is insufficient
* source inspection alone is insufficient
* alternate paths matter
* negative behavior matters
* behavioral evidence is important

The experiment supported the core evidence-first hypothesis.

**G-01: PASS**

---

## 7. G-01A — Validation Requirement Experiment

The next experiment used:

```text id="t3ry4v"
An invoice creation request must be rejected
when invoice amount is negative.
```

Invariant:

```text id="9j0k2p"
amount >= 0
```

Ten cases were evaluated.

Observed results:

```text id="h4y9r1"
VERIFIED:           4
PARTIALLY VERIFIED: 2
NOT VERIFIED:       4
```

This demonstrated that verification results depend on the actual evidence available rather than a simple binary test outcome.

**G-01A: PASS**

---

## 8. Local AI Validation

Local AI was evaluated using Ollama with the `qwen3:1.7b` model.

AI assistance was tested for:

* requirement interpretation
* invariant extraction
* verification planning
* investigation assistance
* explanation
* reporting assistance

The evaluation demonstrated useful assistance but also important weaknesses.

Observed weaknesses included:

* authorization reasoning
* alternate-path discovery
* edge-case discovery
* final classification

In one security-related case, the AI incorrectly classified a case as `PARTIALLY VERIFIED` while the deterministic result was `NOT VERIFIED`.

This led to a permanent architectural rule:

> **AI may assist the investigation, but AI cannot make the authoritative verification decision.**

---

## 9. G-02 — Cross-Component Experiment

The project then moved to a realistic cross-component repository.

The repository contained:

```text id="jv6t7n"
g02_repository/
├── domain/
│   ├── models.py
│   └── repository.py
├── services/
│   ├── order_service.py
│   └── payment_service.py
├── api/
│   └── order_api.py
└── tests/
    ├── test_orders.py
    ├── test_payments.py
    └── test_api.py
```

Requirement:

```text id="7n4f6p"
REQ-G02-001:

An order must not be marked as paid unless
the corresponding payment has been successfully completed.
```

Invariant:

```text id="4m5f3x"
order.status == "paid"
implies
payment.status == "completed"
```

---

## 10. G-02 Deliberate Defect

A deliberate defect was introduced by omitting the check of the result from:

```text id="5t7xq9"
process_payment()
```

The intended implementation required:

```text id="0a9p4s"
payment_successful = self.payment_service.process_payment(payment)

if not payment_successful:
    return False

order.status = "paid"
```

The defect allowed the order to become paid even when payment processing failed.

---

## 11. G-02 Results

Baseline:

```text id="e6t5p2"
7 tests passed
```

After introducing the deliberate defect:

```text id="2k3c7q"
7 passed
1 failed
```

The failing behavioral case demonstrated contradictory evidence.

Deterministic result:

```text id="y4m8z1"
NOT VERIFIED
```

After restoring the correct implementation:

```text id="j2n6s4"
8 tests passed
```

The experiment demonstrated that the verification concept could identify a cross-component behavioral violation.

**G-02: PASS**

---

## 12. DEFINE

After experimental validation, the MVP scope was defined.

### MUST

The system must provide:

* requirement input
* requirement → invariant representation
* repository analysis
* verification scope
* evidence model
* verification plan
* positive-path verification
* negative-path verification
* edge-case verification
* cross-component evidence
* deterministic decision engine
* three-state result
* evidence-backed report
* reproducible execution
* failure handling
* controlled execution policy

### SHOULD

The system should support:

* local AI requirement interpretation
* AI verification-plan suggestions
* natural-language explanations
* evidence visualization
* verification history
* CLI improvements
* configuration
* improved path discovery
* Markdown/JSON reports

### COULD

Future possibilities included:

* multiple languages
* IDE integration
* GitHub/PR/CI integration
* repository-wide campaigns
* dashboards
* history/search
* team collaboration
* plugins
* advanced models
* cloud integrations

### NOT NOW

The project explicitly excluded:

* generic AI code reviewer positioning
* full static-analysis replacement
* autonomous coding agent
* bug-free certification
* giant multi-language platform
* mandatory cloud
* mandatory paid AI APIs
* dashboard-first development
* uncontrolled scope

---

## 13. MVP Definition

The MVP was defined as:

> **AI-VERIFY takes a concrete software requirement and a Python repository, gathers structured evidence across relevant execution paths and components, and deterministically reports whether that requirement is VERIFIED, PARTIALLY VERIFIED, or NOT VERIFIED.**

This definition became the scope boundary for implementation.

---

## 14. DESIGN

The architecture was designed around separation of responsibilities.

High-level architecture:

```text id="w3f8r7"
CLI
 ↓
Verification Service
 ↓
Verification Orchestrator
 ↓
Repository Analyzer
Verification Scope
Verification Planner
 ↓
Verification Activities
 ↓
Controlled Execution
 ↓
Evidence Pipeline
 ↓
Deterministic Decision
 ↓
Verification Run
 ↓
Report Builder
 ↓
JSON + Markdown
```

The architecture intentionally separated:

```text id="c2j7n4"
Requirement
    ≠
Verification Plan
    ≠
Evidence
    ≠
Decision
```

and:

```text id="z5m3k8"
Execution Status
    ≠
Evidence Status
    ≠
Verification Status
```

---

## 15. Security Design Decisions

Security boundaries were designed before the production implementation was considered complete.

Permanent decisions included:

* operate only on the selected repository
* prevent working-directory escape
* use `shell=False`
* preserve explicit commands
* never silently rewrite commands
* never silently modify source files
* treat repository content as untrusted
* treat AI output as untrusted
* never allow AI to override deterministic decisions
* preserve evidence provenance
* do not expose unrelated secrets unnecessarily
* do not claim complete OS sandboxing

These decisions later became part of BUILD-19 validation.

---

## 16. PROTOTYPE Phase

The prototype phase validated the architecture before production implementation.

Only two focused prototypes were completed.

### PROTOTYPE-01 — Decision Kernel

The decision kernel was tested against the required semantics.

Result:

```text id="g5v2p1"
10/10 tests passed
```

Validated:

* contradiction precedence
* insufficient evidence → partial
* deterministic classification
* AI non-authority
* repeated evaluation stability

**PROTOTYPE-01: PASS**

### PROTOTYPE-02 — Run Package and Integrity

The run package was validated for:

* serialization
* reload
* evidence preservation
* decision preservation
* provenance preservation
* integrity checking
* deterministic re-evaluation
* AI metadata independence

Result:

```text id="s1j7q5"
10/10 tests passed
```

**PROTOTYPE-02: PASS**

The prototype phase was then closed.

No unnecessary prototype expansion was performed.

---

## 17. BUILD Phase

The production implementation progressed through BUILD-01 to BUILD-20.

Each build introduced a focused capability and was validated before moving forward.

---

## 18. BUILD-01 — Decision Core

Implemented:

```text id="5r4c2k"
src/ai_verify/core/models.py
src/ai_verify/core/decision.py
```

Introduced:

* `VerificationStatus`
* `EvidenceStatus`
* `EvidenceType`
* `Evidence`
* `DecisionResult`
* deterministic decision rules

Core rule:

```text id="2v7n3m"
CONTRADICTS
    ↓
NOT VERIFIED
```

---

## 19. BUILD-02 — Run Package and Integrity

Implemented structured verification runs and deterministic SHA-256 integrity checking.

The run package preserved:

* requirement
* invariant
* scope
* verification plan
* evidence
* decision
* provenance
* schema version

A regression involving run serialization was identified and corrected during development.

The final implementation was validated before continuing.

---

## 20. BUILD-03 — Repository Analysis

Implemented repository analysis with:

* repository validation
* Python file discovery
* deterministic paths
* ignored environment/cache directories
* repository boundary enforcement
* no source execution
* no AI invocation
* no source modification

---

## 21. BUILD-04 — Verification Scope

Implemented explicit verification scope.

Files were represented with:

* relative path
* absolute path
* role

The current implementation distinguishes basic source and test roles.

---

## 22. BUILD-05 — Verification Planning

Implemented the verification planner.

The MVP plan includes:

```text id="7n8m4k"
Positive Path
Negative Path
Edge Case
```

The planner establishes:

```text id="3k5v7p"
Required supporting evidence = 3
```

This threshold prevents one successful observation from automatically becoming complete verification.

---

## 23. BUILD-06 — Evidence Model

Implemented:

* evidence observations
* evidence collection
* evidence validation
* provenance fields

Evidence statuses:

```text id="1w6p3q"
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

---

## 24. BUILD-07 — Controlled Execution

Implemented controlled subprocess execution.

The executor validates:

* repository root
* working directory
* command
* timeout

Execution uses:

```python id="m7f2q8"
shell=False
```

Execution states:

```text id="9r4v2s"
COMPLETED
FAILED
TIMED_OUT
```

---

## 25. BUILD-08 — Evidence Adapter

Execution results were adapted into structured evidence.

Semantics:

```text id="w3n6p2"
COMPLETED + exit 0
    ↓
Success evidence
```

```text id="j8v4k1"
COMPLETED + non-zero exit
    ↓
Failure evidence
```

```text id="q2m7s5"
FAILED / TIMED_OUT
    ↓
INCONCLUSIVE
```

This preserved the distinction between execution failure and requirement contradiction.

---

## 26. BUILD-09 — Evidence Pipeline

Connected:

```text id="c7x2n5"
Executor
 ↓
Evidence Adapter
 ↓
Evidence Collector
```

The pipeline ensured that execution results became validated structured evidence before entering the decision process.

---

## 27. BUILD-10 — Verification Run

Connected collected evidence to the deterministic decision engine and created the structured verification run.

The run preserved the verification context and authoritative decision.

---

## 28. BUILD-11 — Activity Runner

Implemented deterministic execution of verification activities.

Activities preserved:

* activity ID
* execution request
* evidence ID
* description
* success status
* failure status

---

## 29. BUILD-12 — Orchestrator

Connected the major verification stages:

```text id="x9c5m2"
Repository Analysis
 ↓
Scope
 ↓
Planning
 ↓
Activity Execution
 ↓
Evidence
 ↓
Verification Run
```

This established the production verification workflow.

---

## 30. BUILD-13 — Report Model

Implemented the structured verification report.

The report preserved:

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

---

## 31. BUILD-14 — Report Serialization

Implemented JSON-compatible report serialization.

Focused validation confirmed:

```text id="n8w2r4"
10/10 report and serialization tests passed
```

The report serialization remained a presentation transformation and did not alter authoritative verification decisions.

---

## 32. BUILD-15 — End-to-End Verification Flow

Connected the production components into an end-to-end service.

The completed flow became:

```text id="u7m3q9"
Requirement
 ↓
Invariant
 ↓
Repository
 ↓
Scope
 ↓
Plan
 ↓
Execution
 ↓
Evidence
 ↓
Decision
 ↓
Run
 ↓
Report
```

The end-to-end integration tests passed.

---

## 33. BUILD-16 — CLI Integration

The CLI became the primary user interface.

Required inputs included:

* repository
* requirement
* invariant
* run ID
* explicit command

The CLI preserves the explicit command supplied by the user.

A parsing issue was identified when command arguments such as:

```text id="a4v7q2"
-m pytest
```

were initially incompatible with the argument parser.

The CLI was corrected to use:

```text id="m6x2r8"
argparse.REMAINDER
```

for the explicit command.

The final CLI behavior was validated.

---

## 34. BUILD-17 — JSON and Markdown Reporting

Implemented the report writer.

Each verification report can be written as:

```text id="c4n7s1"
JSON
Markdown
```

The writer supports:

* output directories
* run-ID filenames
* nested directories
* structured JSON
* human-readable Markdown

Focused writer validation passed.

---

## 35. BUILD-18 — Failure and Edge-Case Hardening

Failure semantics were reviewed across:

* executor
* evidence adapter
* evidence pipeline
* decision engine
* orchestrator
* verification run

Focused validation:

```text id="j7p2m4"
44/44 focused tests passed
```

Full regression remained:

```text id="x5r8n1"
119/119 passed
```

No production changes were required.

This confirmed that the existing implementation already handled the targeted failure cases correctly.

---

## 36. BUILD-19 — Security and Boundary Validation

Security boundaries were explicitly validated.

Focused results:

```text id="k3m7q2"
Executor boundary:       10/10
CLI boundary:            11/11
Serialization + writer:  13/13
Integration:              3/3
```

Total:

```text id="v8n2c5"
37/37 focused tests passed
```

Full regression:

```text id="p4x7m1"
119/119 passed
```

The validation confirmed:

* repository boundary behavior
* CLI boundary behavior
* command preservation
* `shell=False`
* reporting behavior
* serialization integrity
* integration behavior

---

## 37. BUILD-20 — Final MVP Integration

BUILD-20 completed the MVP integration.

The final intended pipeline was:

```text id="n4q8s2"
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

A real CLI demonstration was executed.

The CLI produced:

```text id="x6m3p8"
Status: PARTIALLY VERIFIED
Rule: INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE
```

The underlying verification command completed successfully.

The result remained `PARTIALLY VERIFIED` because only one supporting evidence item was supplied while the current plan requires three.

This was considered correct behavior.

BUILD-20 was therefore closed and locked.

---

## 38. TEST Phase

The formal TEST phase was performed after the production build was complete.

Six focused validation gates were executed.

### Gate 1

```text id="a8m4v2"
25 passed
```

Validated:

* CLI
* end-to-end integration
* reporting

### Gate 2

```text id="k6p2r9"
28 passed
```

Validated:

* decision semantics
* evidence
* evidence adapter
* evidence pipeline

### Gate 3

```text id="t3v7m1"
30 passed
```

Validated:

* repository analyzer
* scope
* planner
* orchestrator
* activity runner

### Gate 4

```text id="q9n5x4"
24 passed
```

Validated:

* executor
* CLI boundaries
* timeout behavior
* shell policy
* command preservation

### Gate 5

```text id="m2r8k6"
24 passed
```

Validated:

* run package
* reports
* serialization
* writer

### Gate 6

Integration:

```text id="c7v3p1"
3 passed
```

The behavioral fixtures contained deliberate failing cases.

Across those individual behavioral fixtures:

```text id="f5n9q2"
38 tests
29 passed
9 deliberate failures
```

The deliberate failures represented intentionally incorrect software behavior.

They were not production regression failures.

---

## 39. Final Regression

After completing the TEST phase:

```text id="r8m3k7"
122/122 tests passed
```

The complete suite was executed using the project virtual environment.

This became the final regression checkpoint for the MVP.

---

## 40. EVALUATE Phase

The EVALUATE phase tested whether the implemented system met its defined MVP acceptance criteria.

Four evaluation gates were completed.

---

## 41. EVALUATE Gate 1 — MVP Acceptance

Validated:

* requirement input
* invariant input
* repository analysis
* verification scope
* verification plan
* controlled execution
* structured evidence
* positive-path verification
* negative-path verification
* edge-case verification
* deterministic decision
* three-state result
* evidence-backed reporting
* JSON reporting
* Markdown reporting
* reproducibility
* failure handling
* timeout handling
* repository boundary
* AI non-authority

Result:

```text id="w5n2r8"
PASS
```

---

## 42. EVALUATE Gate 2 — Three-State Demonstration

The deterministic decision engine was evaluated for all three states.

```text id="j8m4q2"
EVAL-VERIFIED-CORRECT
Expected: VERIFIED
Actual:   VERIFIED
PASS

EVAL-PARTIAL-CORRECT
Expected: PARTIALLY VERIFIED
Actual:   PARTIALLY VERIFIED
PASS

EVAL-NOT-VERIFIED-CORRECT
Expected: NOT VERIFIED
Actual:   NOT VERIFIED
PASS
```

Final:

```text id="s3p7k1"
FINAL: PASS
```

---

## 43. EVALUATE Gate 3 — Reproducibility

Two runs using the same authoritative activities and inputs were compared.

Results:

```text id="v4n8m2"
Run A status: VERIFIED
Run B status: VERIFIED
```

Stable fields included:

```text id="q6r3p9"
status
decision_rule
rationale
requirement
invariant
scope
verification_plan
evidence
provenance
```

The run IDs were intentionally different.

Result:

```text id="m7k2x5"
Authoritative results: STABLE
Run IDs intentionally different: True
FINAL: PASS
```

---

## 44. EVALUATE Gate 4 — Failure and Safety

Validated:

* invalid repository root
* invalid working directory
* invalid command
* invalid timeout
* non-zero exit
* failed execution
* timeout
* timed-out evidence
* repository boundary

Result:

```text id="p2r8v4"
25 passes
```

The critical semantic behavior was:

```text id="n6m3q7"
FAILED
    ↓
INCONCLUSIVE
```

and:

```text id="x4k9s2"
TIMED_OUT
    ↓
INCONCLUSIVE
```

Result:

```text id="c8v5m1"
PASS
```

---

## 45. DOCUMENT Phase

After implementation, testing, and evaluation were completed, the project entered documentation.

The documentation set was deliberately limited to the documents necessary to explain the system professionally.

Current documentation structure:

```text id="z7m3q9"
README.md
docs/
├── architecture.md
├── verification-model.md
├── security-boundaries.md
├── evaluation.md
└── development-history.md
```

The documentation explains:

* what AI-VERIFY is
* how it is architected
* how verification works
* what security boundaries exist
* how the system was evaluated
* how the project evolved

Documentation is derived from the implemented and evaluated system rather than from an aspirational future design.

---

## 46. Locked Development Decisions

Several decisions remained locked throughout the project.

### CLI-First

The MVP uses a CLI rather than a web dashboard.

### Deterministic Decision Engine

The final verification decision is not delegated to AI.

### Three-State Result

The system uses:

```text id="r5m8x2"
VERIFIED
PARTIALLY VERIFIED
NOT VERIFIED
```

### Contradiction Precedence

Contradictory evidence always wins.

### Failure Semantics

Failed or timed-out execution does not automatically become contradiction.

### Evidence Threshold

The current MVP requires three supporting evidence items for `VERIFIED`.

### Explicit Commands

User-supplied commands are not silently rewritten.

### Repository Boundary

Execution remains within the selected repository working-directory boundary.

### Controlled Execution

The executor uses `shell=False`.

### Lightweight Integrity

Run packages support deterministic SHA-256 integrity checking.

### No Mandatory Paid AI

The core verification flow does not require a paid AI service.

---

## 47. What Was Deliberately Not Built

The project deliberately stopped before adding:

* web dashboard
* hosted SaaS
* mandatory cloud services
* multi-language support
* CI/CD integration
* GitHub integration
* IDE plugins
* team collaboration
* large-scale repository campaigns
* advanced autonomous agents
* full OS sandboxing
* production-grade cryptographic signing

These are future possibilities, not missing MVP requirements.

---

## 48. Current Project State

The current project state is:

```text id="m4n8q2"
DISCOVER       ✅ COMPLETE
VALIDATE      ✅ COMPLETE
DEFINE         ✅ COMPLETE
DESIGN         ✅ COMPLETE
PROTOTYPE      ✅ CLOSED
BUILD          ✅ COMPLETE
TEST           ✅ COMPLETE
EVALUATE       ✅ COMPLETE
DOCUMENT       🔵 IN PROGRESS
DEPLOY         ⏳ PENDING
PORTFOLIO      ⏳ PENDING
```

The engineering core is complete for the current MVP scope.

The remaining work is documentation finalization, deployment/distribution preparation, and portfolio presentation.

---

## 49. Development Outcome

The project evolved from a hypothesis:

> Can software requirements be verified using structured evidence rather than AI opinion?

into a working CLI-first verification system with:

* repository analysis
* verification planning
* controlled execution
* structured evidence
* deterministic decision-making
* verification run packages
* integrity checking
* JSON reporting
* Markdown reporting
* security boundaries
* reproducibility
* tested failure semantics

The final system was validated through experiments and automated tests rather than accepted on implementation appearance alone.

---

## 50. Final Development Principle

The entire development history can be summarized by one rule:

```text id="x8m4p2"
Do not build first and justify later.

Discover.
Validate.
Define.
Design.
Prototype.
Build.
Test.
Evaluate.
Document.
```

And the project's core principle remains:

> **AI assists. Evidence decides.**

AI-VERIFY was intentionally built around that principle from discovery through evaluation.

That is the foundation of the system and the reason its verification result is deterministic rather than an AI opinion.
