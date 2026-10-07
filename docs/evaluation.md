# AI-VERIFY Evaluation

## 1. Purpose

AI-VERIFY was evaluated using controlled experiments, focused test gates, integration validation, security validation, reproducibility checks, and a final full regression suite.

The purpose of evaluation was to determine whether the implemented system satisfies the defined MVP requirements and whether its core verification semantics behave as designed.

The evaluation principle was:

> **Do not claim that AI-VERIFY works because the code exists. Demonstrate that its behavior satisfies the defined verification model.**

---

## 2. Evaluation Strategy

The evaluation followed the project's evidence-first development philosophy:

```text
Requirement
    ↓
Experiment / Test
    ↓
Observed Evidence
    ↓
Expected Behavior
    ↓
Comparison
    ↓
Evaluation Decision
```

Evaluation focused on:

* deterministic decision correctness
* evidence semantics
* repository analysis
* verification scope
* verification planning
* controlled execution
* failure handling
* timeout handling
* reporting
* CLI behavior
* security boundaries
* end-to-end integration
* reproducibility
* three-state verification behavior

---

## 3. Evaluation Principles

The evaluation followed several principles.

### 3.1 Evidence over appearance

Passing unit tests alone was not considered sufficient proof of the overall verification concept.

Behavioral experiments were used to test whether the system could detect actual requirement violations.

### 3.2 Deterministic decision-making

The final verification result had to come from explicit deterministic rules rather than AI opinion.

### 3.3 Failure must remain distinguishable from contradiction

Execution failure and timeout were evaluated separately from actual contradictory evidence.

### 3.4 Reproducibility

The same authoritative inputs and evidence should produce the same verification result.

### 3.5 Security honesty

The evaluation does not claim that the MVP is a complete operating-system sandbox or a complete security platform.

---

## 4. G-01 — Behavioral Requirement Verification Experiment

The first major experiment tested whether evidence was necessary beyond simple test pass rates.

The requirement was:

```text
An authenticated user must only be able to retrieve
an invoice belonging to that user.
```

Invariant:

```text
invoice.user_id == authenticated_user.id
```

The experiment demonstrated that a requirement involving authorization cannot be established solely from a generic test pass result.

The experiment considered:

* positive authorization behavior
* alternate access paths
* negative authorization behavior
* behavioral evidence
* source-level evidence

### Evaluation result

The experiment demonstrated that:

```text
Test pass rate alone
        ≠
Requirement verification
```

The result supported the core AI-VERIFY premise that requirement verification must be evidence-oriented and behavior-aware.

**G-01: PASS**

---

## 5. G-01A — Negative Validation Experiment

A second experiment evaluated a simpler validation requirement:

```text
An invoice creation request must be rejected
when invoice amount is negative.
```

Invariant:

```text
amount >= 0
```

Ten verification cases were evaluated.

The observed outcomes were:

```text
VERIFIED:          4
PARTIALLY VERIFIED: 2
NOT VERIFIED:      4
```

This experiment demonstrated that different evidence conditions can produce different deterministic verification states.

It also demonstrated that:

```text
Missing / incomplete evidence
        ≠
Contradictory evidence
```

**G-01A: PASS**

---

## 6. Local AI Evaluation

The project also evaluated the usefulness and limitations of local AI assistance.

A local Ollama model using `qwen3:1.7b` was tested for tasks such as:

* requirement interpretation
* invariant extraction
* verification planning
* investigation assistance
* explanation
* reporting assistance

The evaluation showed that AI could provide useful assistance but was not sufficiently reliable to control the final verification decision.

Observed weaknesses included:

* authorization reasoning
* alternate-path discovery
* edge-case discovery
* final classification

In one security-related case, the AI incorrectly classified a case as `PARTIALLY VERIFIED` while the deterministic result was `NOT VERIFIED`.

This was an important evaluation result.

It confirmed the architectural rule:

> **AI output must remain subordinate to deterministic evidence evaluation.**

### AI evaluation conclusion

```text
AI assistance
    → Useful

AI as final decision-maker
    → Rejected
```

The AI role was therefore constrained to assistance rather than authority.

---

## 7. G-02 — Cross-Component Verification Experiment

The G-02 experiment evaluated whether AI-VERIFY could reason about a requirement spanning multiple repository components.

The repository contained:

```text
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

```text
REQ-G02-001:

An order must not be marked as paid unless
the corresponding payment has been successfully completed.
```

Invariant:

```text
order.status == "paid"
implies
payment.status == "completed"
```

---

## 8. G-02 Deliberate Defect

A deliberate defect was introduced into the payment flow.

The defect omitted checking the return value of:

```text
process_payment()
```

This allowed the order to become paid even when payment processing failed.

The intended behavior was:

```text
payment_successful = process_payment(payment)

if not payment_successful:
    return False

order.status = "paid"
```

---

## 9. G-02 Baseline

Before introducing the defect:

```text
7 tests passed
```

The repository therefore established a clean baseline.

A controlled failure probe was also executed.

The baseline behavior was confirmed before the defect was introduced.

---

## 10. G-02 Defect Detection

After introducing the deliberate defect:

```text
7 tests passed
1 test failed
```

The failing behavioral test demonstrated contradictory evidence against the requirement.

The deterministic verification result was:

```text
NOT VERIFIED
```

This was important because the defect was not detected merely by source-code appearance.

The verification process observed behavior that violated the invariant.

---

## 11. G-02 Restoration

After restoring the correct implementation:

```text
8 tests passed
```

The repository returned to the expected state.

The corrected implementation explicitly checked the payment result before changing the order status.

### G-02 conclusion

The experiment demonstrated that AI-VERIFY could support:

* cross-component verification
* deliberate defect detection
* behavioral evidence collection
* contradiction detection
* deterministic `NOT VERIFIED` classification

**G-02: PASS**

---

## 12. Prototype Validation

Before the production build was completed, two focused prototypes validated important architectural assumptions.

### PROTOTYPE-01 — Decision Kernel

The deterministic decision kernel was tested against the required decision semantics.

Result:

```text
10/10 tests passed
```

The prototype validated:

* contradiction precedence
* incomplete evidence → partial verification
* deterministic results
* AI non-authority
* repeated evaluation stability

**PROTOTYPE-01: PASS**

### PROTOTYPE-02 — Run Package and Integrity

The run package serialization and integrity behavior was validated.

Result:

```text
10/10 tests passed
```

The prototype validated preservation of:

* requirement
* invariant
* scope
* verification plan
* evidence
* provenance
* decision

It also validated:

* serialization and reload
* tamper detection
* deterministic re-evaluation
* independence from AI metadata

The integrity mechanism was intentionally evaluated as lightweight deterministic integrity checking rather than production cryptographic tamper resistance.

**PROTOTYPE-02: PASS**

---

## 13. BUILD Validation

The production build progressed through BUILD-01 to BUILD-20.

The implementation was continuously validated after each major build stage.

The final build state included:

```text
Decision Core
Run Package
Integrity
Repository Analyzer
Verification Scope
Verification Planner
Evidence Model
Controlled Execution
Evidence Adapter
Evidence Pipeline
Verification Run
Activity Runner
Orchestrator
Report Model
Report Serialization
CLI
Report Writer
Failure Hardening
Security Boundaries
MVP Integration
```

The completed build was validated through focused tests and regression testing.

---

## 14. TEST Phase

The formal TEST phase used multiple validation gates.

### Gate 1 — CLI, Integration, and Reporting

```text
CLI tests
End-to-end tests
Writer tests
```

Result:

```text
25 passed
```

Validated:

* CLI behavior
* end-to-end flow
* JSON reporting
* Markdown reporting

---

### Gate 2 — Evidence and Decision Semantics

Validated:

```text
Decision
Evidence
Evidence Adapter
Evidence Pipeline
```

Result:

```text
28 passed
```

Validated:

* supporting evidence counts
* contradiction → `NOT VERIFIED`
* inconclusive evidence
* failed execution → `INCONCLUSIVE`
* timeout → `INCONCLUSIVE`
* contradiction plus support
* missing evidence → `PARTIALLY VERIFIED`

---

### Gate 3 — Repository and Verification Workflow

Validated:

```text
Repository Analyzer
Scope
Planner
Orchestrator
Activity Runner
```

Result:

```text
30 passed
```

Validated:

* repository boundaries
* deterministic path discovery
* scope construction
* verification plan generation
* orchestration
* activity execution

---

### Gate 4 — Execution and CLI Boundaries

Validated:

```text
Controlled Executor
CLI
```

Result:

```text
24 passed
```

Validated:

* invalid repository handling
* working-directory escape prevention
* invalid command handling
* timeout handling
* non-zero exit handling
* `shell=False`
* CLI required arguments
* explicit command preservation
* no silent command rewriting

---

### Gate 5 — Run Package and Reporting Integrity

Validated:

```text
Run Package
Report
Serialization
Writer
```

Result:

```text
24 passed
```

Validated:

* run information
* integrity behavior
* AI metadata non-authority
* schema version
* report preservation
* serialization
* JSON output
* Markdown output
* nested output directories
* run-ID filenames

---

### Gate 6 — Integration

The integration suite was executed separately.

Result:

```text
3 integration tests passed
```

The behavioral fixture collection contained deliberate failing cases.

Across the individual behavioral fixtures:

```text
38 tests
29 passed
9 deliberate failures
```

These failures were intentional verification scenarios used to demonstrate detection of incorrect implementations.

They were not production regression failures.

The initial top-level collection issue caused by repeated fixture module names was identified as a test-fixture organization issue rather than a production implementation failure.

---

## 15. Final Regression

After completing the TEST and EVALUATE phases, the complete test suite was executed using the project virtual environment.

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -v
```

Final result:

```text
122 passed
```

The final regression completed successfully.

This is the final implementation regression result for the current MVP.

---

## 16. EVALUATE Gate 1 — MVP Acceptance

The MVP acceptance evaluation checked the defined acceptance criteria.

Validated capabilities included:

```text
Requirement input
Invariant input
Repository analysis
Verification scope
Verification plan
Controlled execution
Structured evidence
Positive-path verification
Negative-path verification
Edge-case verification
Deterministic decision
Three-state result
Evidence-backed report
JSON output
Markdown output
Reproducibility
Failure handling
Timeout handling
Repository boundary
AI non-authority
```

All defined MVP acceptance criteria passed.

**Gate 1: PASS**

---

## 17. EVALUATE Gate 2 — Three-State Demonstration

The three verification states were explicitly demonstrated through the real deterministic decision path.

Expected and actual results:

```text
EVAL-VERIFIED-CORRECT
Expected: VERIFIED
Actual:   VERIFIED
Result:   PASS

EVAL-PARTIAL-CORRECT
Expected: PARTIALLY VERIFIED
Actual:   PARTIALLY VERIFIED
Result:   PASS

EVAL-NOT-VERIFIED-CORRECT
Expected: NOT VERIFIED
Actual:   NOT VERIFIED
Result:   PASS
```

Final evaluation:

```text
FINAL: PASS
```

This confirmed that the three-state decision engine behaves according to the defined semantics.

**Gate 2: PASS**

---

## 18. EVALUATE Gate 3 — Reproducibility

The same authoritative activities and inputs were evaluated twice using different run IDs.

The results were:

```text
Run A status: VERIFIED
Run B status: VERIFIED
```

The following remained stable:

```text
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

Therefore:

```text
Authoritative results: STABLE
Run IDs intentionally different: True
FINAL: PASS
```

This demonstrated deterministic reproducibility of the authoritative verification result.

**Gate 3: PASS**

---

## 19. EVALUATE Gate 4 — Failure and Safety

Failure and safety behavior was validated using:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest `
    tests\unit\test_executor.py `
    tests\unit\test_evidence_adapter.py `
    tests\unit\test_evidence_pipeline.py -v
```

Result:

```text
25 passed
```

The evaluation covered:

* invalid repository root
* invalid working directory
* invalid command
* invalid timeout
* non-zero exit
* failed execution
* timeout
* timed-out evidence
* repository boundary enforcement

The key semantic result was:

```text
Execution failure
    ↓
INCONCLUSIVE evidence
```

rather than automatic contradiction.

**Gate 4: PASS**

---

## 20. Security Evaluation

Security and boundary validation was completed during BUILD-19.

Focused validation results:

```text
Executor boundary:       10/10
CLI boundary:            11/11
Serialization + writer:  13/13
Integration:              3/3
```

Total:

```text
37/37 focused security/boundary tests passed
```

The complete regression suite remained:

```text
122/122 passed
```

The evaluation validated:

* repository boundaries
* controlled execution policy
* shell handling
* command preservation
* CLI boundaries
* report integrity behavior
* AI non-authority
* evidence provenance

This evaluation does not establish complete OS-level sandbox security.

---

## 21. Real CLI MVP Demonstration

The completed MVP was executed through its actual CLI interface.

Example:

```powershell
& ".\.venv\Scripts\python.exe" -m ai_verify.cli.main `
  --repository . `
  --requirement "The verification command must complete successfully." `
  --invariant "verification command exits with code 0" `
  --run-id "BUILD-20-MVP-003" `
  --command python -m pytest -v
```

The CLI produced:

```text
Status: PARTIALLY VERIFIED
Rule: INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE
```

The executed verification command itself completed successfully.

The generated JSON report recorded the execution as completed with exit code `0`.

The overall verification remained:

```text
PARTIALLY VERIFIED
```

because the CLI supplied one evidence item while the current verification plan requires three supporting evidence items.

This was an intentional and correct result.

The system did not weaken its evidence threshold merely because the command passed.

---

## 22. Important Evaluation Finding

One of the most important evaluation findings was:

```text
Successful execution
        ≠
Automatically VERIFIED
```

The real CLI demonstration proved this.

The verification command succeeded, but the evidence threshold was not satisfied.

Therefore:

```text
Execution success
    ↓
Supporting evidence
    ↓
Decision still requires sufficient evidence
```

This behavior directly supports the evidence-first design.

---

## 23. Evaluation of AI Authority

The AI evaluation demonstrated that AI assistance can be useful but can also make incorrect verification judgments.

Therefore the final architecture deliberately separates:

```text
AI assistance
        ↓
Investigation / planning / explanation
```

from:

```text
Evidence
        ↓
Deterministic Decision
        ↓
Authoritative Result
```

The evaluation therefore supports the principle:

> **AI assists. Evidence decides.**

---

## 24. Evaluation of Failure Semantics

The system was explicitly evaluated against the dangerous assumption:

```text
Command failed
    ↓
Requirement failed
```

AI-VERIFY rejects this assumption.

Instead:

```text
Command failed
    ↓
ExecutionStatus = FAILED
    ↓
EvidenceStatus = INCONCLUSIVE
```

Similarly:

```text
Command timed out
    ↓
ExecutionStatus = TIMED_OUT
    ↓
EvidenceStatus = INCONCLUSIVE
```

This protects the verification result from confusing infrastructure problems with software requirement violations.

---

## 25. Evaluation of Contradiction Semantics

The decision engine was evaluated to ensure that contradiction takes precedence.

The validated rule is:

```text
Any CONTRADICTS evidence
        ↓
NOT VERIFIED
```

even when supporting evidence is also present.

This prevents successful cases from hiding a demonstrated violation.

The behavior was validated in both focused decision tests and broader evaluation scenarios.

---

## 26. Evaluation of Missing Evidence

The evaluation also confirmed that missing evidence does not automatically produce `NOT VERIFIED`.

Instead:

```text
No contradiction
+
Insufficient supporting evidence
        ↓
PARTIALLY VERIFIED
```

This preserves the distinction between:

```text
Unknown / insufficient evidence
```

and:

```text
Demonstrated violation
```

This distinction is central to trustworthy requirement verification.

---

## 27. Known Evaluation Limitations

The evaluation has several important limitations.

### Repository Language

The current implementation focuses on Python repositories.

### Behavioral Coverage

The system cannot guarantee discovery of every possible execution path.

### Environment

Results may depend on the local operating environment, installed dependencies, and repository state.

### Security Isolation

Controlled execution is not a complete OS sandbox.

### AI Evaluation

AI behavior was evaluated as assistance rather than as an authoritative verification mechanism.

### Fixture Organization

Some behavioral fixtures intentionally contain failing tests to demonstrate requirement violations.

These should not be confused with production regression failures.

---

## 28. Evaluation Summary

The current MVP passed its defined evaluation gates.

Summary:

```text
G-01 behavioral experiment        PASS
G-01A validation experiment       PASS
Local AI evaluation               PASS as assistance / rejected as authority
G-02 cross-component experiment   PASS
PROTOTYPE-01                      10/10 PASS
PROTOTYPE-02                      10/10 PASS

TEST Gate 1                       25 PASS
TEST Gate 2                       28 PASS
TEST Gate 3                       30 PASS
TEST Gate 4                       24 PASS
TEST Gate 5                       24 PASS
TEST Gate 6                        3 PASS

Security validation               37/37 PASS
Final regression                  122/122 PASS

EVALUATE Gate 1                  PASS
EVALUATE Gate 2                  PASS
EVALUATE Gate 3                  PASS
EVALUATE Gate 4                  PASS
```

---

## 29. Final Evaluation Conclusion

The evaluation provides evidence that the current AI-VERIFY MVP correctly implements its defined verification model.

The evaluated system demonstrates:

* deterministic requirement classification
* structured evidence handling
* contradiction precedence
* incomplete evidence handling
* controlled execution
* explicit failure semantics
* timeout semantics
* repository boundary enforcement
* evidence provenance
* reproducibility
* JSON and Markdown reporting
* AI non-authority
* CLI-first end-to-end verification

The final regression result was:

```text
122/122 tests passed
```

The correct conclusion is not:

> "AI-VERIFY proves software is bug-free."

The defensible conclusion is:

> **AI-VERIFY provides an evidence-first mechanism for determining whether the available evidence supports, incompletely supports, or contradicts a concrete software requirement.**

That is the capability the evaluation was designed to validate.

---

## 30. Evaluation Principle

The complete evaluation can be summarized as:

```text
Do not trust the claim.
        ↓
Define the requirement.
        ↓
Define the invariant.
        ↓
Collect evidence.
        ↓
Test positive, negative, and edge paths.
        ↓
Preserve failures and uncertainty.
        ↓
Apply deterministic rules.
        ↓
Reproduce the result.
        ↓
Report the evidence.
```

The result is consistent with the project's core principle:

> **AI assists. Evidence decides.**
