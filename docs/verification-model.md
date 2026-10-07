# AI-VERIFY Verification Model

## 1. Purpose

AI-VERIFY is an evidence-first requirement verification system.

Its verification model defines how the system moves from a concrete software requirement to an authoritative verification result.

The central principle is:

> **AI assists. Evidence decides.**

The system does not determine requirement satisfaction from code appearance, test pass rate alone, or AI-generated opinion.

Instead, it separates:

```text
Requirement
    ↓
Invariant
    ↓
Verification Plan
    ↓
Evidence
    ↓
Deterministic Decision
```

This document defines the meaning and relationship of these elements.

---

## 2. Verification Question

AI-VERIFY is designed to answer:

> **Does the available evidence support the claim that this requirement is satisfied?**

This is different from asking:

> "Does the code look correct?"

or:

> "Did the tests pass?"

A passing test may provide supporting evidence, but it does not automatically establish complete requirement satisfaction.

Likewise, source code may appear correct while an alternate execution path violates the requirement.

The verification model therefore treats evidence as the basis for the final determination.

---

## 3. Requirement

A requirement is the concrete software behavior that must be verified.

Example:

```text
An order must not be marked as paid unless
the corresponding payment has been successfully completed.
```

A requirement should describe an observable or enforceable condition.

The requirement is an input to the verification workflow.

It is not itself evidence.

```text
Requirement ≠ Evidence
```

---

## 4. Invariant

An invariant expresses the essential condition that must remain true for the requirement to be satisfied.

For the example requirement:

```text
order.status == "paid"
    implies
payment.status == "completed"
```

The invariant provides a precise representation of the requirement that can guide verification activities.

An invariant does not prove that the requirement is satisfied.

It defines what must be demonstrated.

```text
Invariant ≠ Evidence
```

---

## 5. Verification Plan

The verification plan defines the evidence that should be sought.

The current MVP organizes verification around three conceptual categories:

```text
Positive Path
Negative Path
Edge Case
```

### Positive Path

Tests or observes the expected successful behavior.

Example:

```text
Successful payment
    ↓
Payment completed
    ↓
Order may become paid
```

### Negative Path

Tests behavior when the required condition is not satisfied.

Example:

```text
Payment fails
    ↓
Order must not become paid
```

### Edge Case

Tests a boundary or alternate condition that could bypass the intended requirement.

Example:

```text
Payment processing returns an unexpected failure
    ↓
Order must still not become paid
```

The verification plan describes what evidence is required.

It does not count as evidence itself.

```text
Verification Plan ≠ Evidence
```

---

## 6. Evidence

Evidence is an observed result that can be evaluated against the requirement or invariant.

AI-VERIFY represents evidence using three primary statuses:

```text
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

### SUPPORTS

The evidence provides support for the requirement.

Example:

```text
A controlled execution completed successfully
and demonstrated the required behavior.
```

### CONTRADICTS

The evidence demonstrates behavior that violates the requirement.

Example:

```text
Payment failed,
but the order was still marked as paid.
```

This is contradictory evidence.

### INCONCLUSIVE

The evidence does not establish either satisfaction or violation.

Example:

```text
The verification command timed out.
```

A timeout does not prove that the requirement is violated.

Therefore:

```text
Execution timeout
    ↓
INCONCLUSIVE evidence
```

---

## 7. Evidence Types

AI-VERIFY distinguishes several evidence types:

```text
STATIC
TEST
RUNTIME
STRUCTURAL
```

### STATIC

Evidence derived from static inspection or source-level observations.

### TEST

Evidence produced by test execution.

### RUNTIME

Evidence observed from actual runtime behavior.

### STRUCTURAL

Evidence describing repository or implementation structure.

These categories preserve the provenance and nature of the observation.

They do not independently determine the final verification result.

---

## 8. Evidence Provenance

Evidence must preserve enough information to identify where the observation came from.

Evidence may include:

* evidence ID
* status
* description
* source
* evidence type
* observation
* execution ID

This creates a traceable relationship:

```text
Evidence
   ↓
Observation
   ↓
Source / Execution
```

The purpose is reproducibility and auditability.

Evidence should never be treated as an unexplained assertion.

---

## 9. Execution Status vs Evidence Status

AI-VERIFY deliberately separates execution state from evidence status.

Execution states are:

```text
COMPLETED
FAILED
TIMED_OUT
```

Evidence states are:

```text
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

These are different concepts.

For example:

```text
Execution
    ↓
FAILED
    ↓
Evidence
    ↓
INCONCLUSIVE
```

A failed verification command does not automatically mean that the requirement is violated.

Similarly:

```text
Execution
    ↓
TIMED_OUT
    ↓
Evidence
    ↓
INCONCLUSIVE
```

This prevents infrastructure or execution problems from being incorrectly interpreted as software defects.

---

## 10. Evidence Collection

Evidence is collected through the verification evidence pipeline:

```text
Execution Request
        ↓
Controlled Executor
        ↓
Execution Result
        ↓
Evidence Adapter
        ↓
Evidence Observation
        ↓
Evidence Collector
        ↓
Structured Evidence
```

The controlled executor produces execution information.

The evidence adapter interprets that execution result into an evidence status.

The evidence collector validates the resulting observation and creates the structured evidence object.

This separation prevents execution mechanics from being confused with verification semantics.

---

## 11. Supporting Evidence Threshold

The current MVP uses:

```text
Required supporting evidence = 3
```

The threshold is associated with the verification plan.

It prevents a single successful observation from automatically being treated as complete verification.

For example:

```text
1 supporting observation
0 contradictions
    ↓
PARTIALLY VERIFIED
```

The threshold does not mean that exactly three tests are always sufficient in every possible future system.

It is the current MVP evidence requirement.

---

## 12. Contradiction Precedence

Contradictory evidence has the highest priority.

If contradictory evidence exists:

```text
CONTRADICTS
    ↓
NOT VERIFIED
```

This remains true even when supporting evidence also exists.

Example:

```text
SUPPORTS
SUPPORTS
SUPPORTS
CONTRADICTS
```

Result:

```text
NOT VERIFIED
```

This rule prevents a collection of successful cases from hiding a demonstrated violation.

The governing principle is:

> **Contradiction wins.**

---

## 13. Partial Verification

A requirement is `PARTIALLY VERIFIED` when:

* no contradictory evidence has been identified, and
* the required amount of supporting evidence has not been reached.

Example:

```text
SUPPORTS
INCONCLUSIVE
INCONCLUSIVE
```

If the required supporting evidence count is three:

```text
Supporting evidence = 1
Required evidence = 3
```

Result:

```text
PARTIALLY VERIFIED
```

Partial verification therefore represents incomplete or insufficient evidence rather than proven failure.

---

## 14. Verified

A requirement is `VERIFIED` when:

* the required amount of supporting evidence is present, and
* no contradictory evidence exists.

For the current MVP:

```text
Supporting evidence >= 3
Contradictory evidence = 0
```

Result:

```text
VERIFIED
```

This means that the available evidence satisfies the current verification threshold.

It does not claim that the software is universally bug-free.

---

## 15. Not Verified

A requirement is `NOT VERIFIED` when contradictory evidence exists.

Example:

```text
SUPPORTS
SUPPORTS
CONTRADICTS
```

Result:

```text
NOT VERIFIED
```

The presence of contradiction takes precedence over the number of supporting observations.

`NOT VERIFIED` therefore means that the available evidence contains a demonstrated conflict with the requirement.

---

## 16. Deterministic Decision Rules

The decision engine applies the following rules in order.

### Rule 1 — Contradiction

```text
IF contradictory evidence exists
THEN
    NOT VERIFIED
```

### Rule 2 — Insufficient Support

```text
IF no contradiction exists
AND supporting evidence < required evidence count
THEN
    PARTIALLY VERIFIED
```

### Rule 3 — Sufficient Support

```text
IF no contradiction exists
AND supporting evidence >= required evidence count
THEN
    VERIFIED
```

Conceptually:

```text
                    Evidence
                       │
                       ▼
             Any contradiction?
                 /          \
               YES           NO
                │             │
                ▼             ▼
         NOT VERIFIED   Enough support?
                           /      \
                         NO        YES
                         │          │
                         ▼          ▼
                  PARTIALLY     VERIFIED
                  VERIFIED
```

The decision is deterministic.

The same evidence produces the same result.

---

## 17. Evidence Does Not Equal Test Pass Rate

A test suite passing does not automatically mean that a requirement is verified.

For example:

```text
122 tests passed
```

may be strong evidence, but the system still evaluates:

* what requirement is being verified
* what invariant represents it
* which evidence was actually collected
* whether relevant paths were covered
* whether contradictory evidence exists
* whether the required evidence threshold was satisfied

Therefore:

```text
Test Pass Rate ≠ Verification Result
```

Test execution is one source of evidence.

It is not the decision engine itself.

---

## 18. Positive, Negative, and Edge-Case Evidence

A robust verification process should not rely only on the expected successful path.

For a requirement involving a condition:

```text
Required condition
```

verification should consider:

```text
Positive Path
    ↓
Does the intended behavior work?

Negative Path
    ↓
Does the system reject invalid behavior?

Edge Case
    ↓
Can an alternate or boundary path bypass the requirement?
```

This structure was validated during the AI-VERIFY experiments, including cross-component verification.

---

## 19. Cross-Component Verification

Requirements may depend on multiple components.

For example:

```text
API
 ↓
Order Service
 ↓
Payment Service
 ↓
Payment Repository
```

A requirement involving payment state cannot always be verified by examining one file or one component.

The verification model therefore supports evidence that spans:

* multiple source files
* multiple services
* repository components
* tests
* runtime behavior

This is important because a defect may occur at the boundary between components even when each component appears correct in isolation.

---

## 20. Missing Evidence

Missing evidence is not automatically treated as contradictory evidence.

For example:

```text
No evidence for an alternate path
```

does not mean:

```text
The alternate path is broken
```

Instead, insufficient evidence may produce:

```text
PARTIALLY VERIFIED
```

This distinction is essential:

```text
Missing evidence
    ≠
Contradictory evidence
```

The system therefore avoids converting uncertainty into false failure.

---

## 21. AI's Role in the Verification Model

AI may assist with parts of the investigation.

Potential AI-assisted activities include:

```text
Requirement interpretation
Invariant extraction
Verification planning
Path investigation
Natural-language explanation
Report assistance
```

However, AI output is treated as untrusted.

AI cannot:

```text
Override the deterministic result
Fabricate evidence
Fabricate execution results
Claim unexecuted tests passed
Claim uncovered paths were covered
Modify authoritative evidence
Silently change verification scope
Declare the final verification result
```

The authoritative flow remains:

```text
Evidence
   ↓
Deterministic Decision
   ↓
Verification Result
```

not:

```text
AI Opinion
   ↓
Verification Result
```

---

## 22. Verification Result Semantics

The three result states have distinct meanings.

| Result               | Meaning                                                                        |
| -------------------- | ------------------------------------------------------------------------------ |
| `VERIFIED`           | Required supporting evidence exists and no contradiction was found.            |
| `PARTIALLY VERIFIED` | No contradiction was found, but available supporting evidence is insufficient. |
| `NOT VERIFIED`       | Contradictory evidence was found.                                              |

These states should not be interpreted as:

```text
VERIFIED          = bug-free
PARTIALLY VERIFIED = probably correct
NOT VERIFIED      = every part is broken
```

Instead, they describe the state of the available evidence relative to the verification rules.

---

## 23. Reproducibility

A verification run preserves the information required to reproduce and inspect the result.

The run package includes:

* run ID
* requirement
* invariant
* scope
* verification plan
* evidence
* decision
* provenance
* schema version

Given the same authoritative inputs and evidence, the deterministic decision engine should produce the same verification result.

This was explicitly validated during the evaluation phase.

---

## 24. Evidence and Reporting

The verification result is preserved in the verification run before reporting.

The reporting flow is:

```text
Evidence
    ↓
Decision
    ↓
Verification Run
    ↓
Verification Report
    ↓
JSON / Markdown
```

Reports are presentation layers.

They must not change:

* evidence
* decision status
* decision rule
* rationale
* provenance

Therefore:

```text
Report ≠ Decision Engine
```

---

## 25. Example — VERIFIED

Requirement:

```text
An order must not be marked as paid unless
the corresponding payment has completed.
```

Invariant:

```text
order.status == "paid"
implies
payment.status == "completed"
```

Evidence:

```text
Positive path → SUPPORTS
Negative path → SUPPORTS
Edge case    → SUPPORTS
```

No contradiction exists.

Result:

```text
VERIFIED
```

---

## 26. Example — PARTIALLY VERIFIED

Same requirement and invariant.

Evidence:

```text
Positive path → SUPPORTS
Negative path → INCONCLUSIVE
Edge case    → INCONCLUSIVE
```

Supporting evidence:

```text
1
```

Required supporting evidence:

```text
3
```

No contradiction exists.

Result:

```text
PARTIALLY VERIFIED
```

This means the requirement has not been disproven, but the available evidence is insufficient for full verification.

---

## 27. Example — NOT VERIFIED

Same requirement and invariant.

Evidence:

```text
Positive path → SUPPORTS
Negative path → CONTRADICTS
Edge case    → SUPPORTS
```

A contradictory observation exists.

Result:

```text
NOT VERIFIED
```

The contradiction wins even though supporting evidence also exists.

---

## 28. Security-Relevant Semantics

The verification model is intentionally conservative around uncertainty.

The system avoids these unsafe assumptions:

```text
Command failed
    ≠
Requirement violated
```

```text
Test passed
    ≠
Requirement completely verified
```

```text
No evidence
    ≠
Requirement contradicted
```

```text
AI says correct
    ≠
Requirement verified
```

These distinctions reduce the risk of false verification conclusions.

---

## 29. Relationship Between the Core Concepts

The complete model can be summarized as:

```text
Requirement
    │
    ▼
Invariant
    │
    ▼
Verification Plan
    │
    ▼
Verification Activities
    │
    ▼
Execution
    │
    ▼
Evidence
    │
    ├───────────────┐
    │               │
    ▼               ▼
SUPPORTS       CONTRADICTS
    │               │
    └───────┬───────┘
            ▼
   Deterministic Decision
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
 VERIFIED  PARTIAL  NOT VERIFIED
```

Execution failures and timeouts can produce:

```text
INCONCLUSIVE
```

which contributes to incomplete evidence rather than automatically becoming contradiction.

---

## 30. Verification Model Invariants

The following principles are fundamental to the model:

1. A requirement is not evidence.
2. An invariant is not evidence.
3. A verification plan is not evidence.
4. An unexecuted activity is not execution evidence.
5. Execution status is distinct from evidence status.
6. Evidence status is distinct from verification status.
7. Failed execution does not automatically mean contradiction.
8. Timeout does not automatically mean contradiction.
9. Missing evidence does not automatically mean failure.
10. Contradictory evidence takes precedence.
11. Supporting evidence must satisfy the required threshold for `VERIFIED`.
12. AI cannot override the deterministic decision.
13. Reports cannot modify the authoritative result.
14. Evidence provenance must be preserved.
15. The same authoritative evidence must produce a deterministic result.

---

## 31. Summary

AI-VERIFY treats requirement verification as an **evidence evaluation problem**.

The model deliberately separates:

```text
Requirement
    ≠
Invariant
    ≠
Verification Plan
    ≠
Execution
    ≠
Evidence
    ≠
Decision
```

The final classification is determined by explicit rules:

```text
Contradiction
    → NOT VERIFIED

No contradiction + insufficient support
    → PARTIALLY VERIFIED

No contradiction + sufficient support
    → VERIFIED
```

The purpose of the model is not to claim absolute correctness.

Its purpose is to provide a reproducible, evidence-backed answer to a narrower and more defensible question:

> **Does the available evidence support the claim that this requirement is satisfied?**

That principle is the foundation of AI-VERIFY.
