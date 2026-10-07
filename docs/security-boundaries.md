# AI-VERIFY Security Boundaries

## 1. Purpose

AI-VERIFY verifies software requirements by collecting and evaluating evidence from a user-selected repository.

Because verification involves repository files, test execution, command execution, and optional AI assistance, the system must maintain explicit security boundaries.

The central security principle is:

> **Untrusted repository content and AI output must never silently become authoritative verification logic.**

This document defines the security boundaries of the current AI-VERIFY MVP.

---

## 2. Security Philosophy

AI-VERIFY follows a conservative trust model.

The system separates:

```text
Trusted Verification Logic
        ↓
Untrusted Repository / Execution / AI Inputs
        ↓
Validated Evidence
        ↓
Deterministic Decision
```

The objective is not to claim that AI-VERIFY is a complete security sandbox.

The objective is to prevent common verification-integrity failures such as:

* executing outside the selected repository
* silently rewriting user commands
* treating AI output as authoritative
* treating execution failure as proof of a requirement violation
* hiding failed or inconclusive evidence
* silently changing verification scope
* allowing reports to alter authoritative decisions

---

## 3. Security Boundary Overview

The current architecture contains several important boundaries:

```text
User
  │
  ▼
CLI Boundary
  │
  ▼
Repository Boundary
  │
  ▼
Execution Boundary
  │
  ▼
Evidence Boundary
  │
  ▼
Decision Boundary
  │
  ▼
Reporting Boundary
```

AI assistance is outside the authoritative decision boundary:

```text
                 AI
                  │
                  │ untrusted assistance
                  ▼
        Verification Workflow
                  │
                  ▼
        Structured Evidence
                  │
                  ▼
      Deterministic Decision
```

---

## 4. Trusted Components

The following components are part of the trusted verification core:

```text
Deterministic decision rules
Evidence model
Evidence validation
Execution policy
Repository boundary checks
Verification scope rules
Run package structure
Provenance handling
Report serialization rules
```

These components determine how verification information is interpreted.

Their behavior must not be replaced by arbitrary repository instructions or AI-generated conclusions.

---

## 5. Untrusted Inputs

The following information is treated as untrusted:

```text
Repository source code
Repository tests
Repository documentation
Repository configuration
Repository-provided instructions
Raw stdout
Raw stderr
External text
AI-generated output
```

Untrusted does not mean useless.

Repository content and execution output are essential sources of evidence.

The security boundary means that these inputs cannot silently redefine the verification system's authoritative rules.

---

## 6. Repository Boundary

AI-VERIFY operates on the repository explicitly supplied to the verification workflow.

The repository analyzer validates the selected repository root.

The execution layer also validates the working directory.

The fundamental rule is:

```text
Execution Working Directory
        ↓
Must remain inside
        ↓
Selected Repository
```

This prevents the verification workflow from intentionally or accidentally using an unrelated working directory through the controlled execution interface.

---

## 7. Repository File Discovery

The repository analyzer is deliberately limited.

It:

* discovers Python files
* stays inside the selected repository
* produces deterministic relative paths
* ignores known environment and cache directories
* does not execute repository code
* does not invoke AI
* does not modify repository files

Common ignored directories include:

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

This reduces noise and prevents common generated or environment content from being treated as normal source material.

---

## 8. No Silent Repository Modification

AI-VERIFY does not silently modify repository source files as part of verification.

The verification workflow is observational.

It should:

```text
Read / analyze
      ↓
Execute explicit verification activity
      ↓
Collect evidence
      ↓
Decide
      ↓
Report
```

It should not:

```text
Analyze
   ↓
Modify source
   ↓
Re-run
   ↓
Claim original repository was verified
```

This distinction is essential for evidence integrity.

---

## 9. Controlled Execution Boundary

The controlled execution layer is responsible for executing explicit verification commands.

The execution request contains:

* command
* working directory
* timeout

The executor validates these inputs before execution.

Execution uses:

```python
shell=False
```

This means commands are passed to the subprocess execution mechanism without enabling a shell interpretation layer.

The executor also uses captured output rather than relying on interactive shell behavior.

---

## 10. Explicit Command Preservation

AI-VERIFY must not silently rewrite an explicit user-supplied command.

For example, if the user supplies:

```text
python -m pytest
```

the verification workflow preserves the command as supplied.

The system must not silently replace it with:

```text
.venv\Scripts\python.exe -m pytest
```

or another command merely because that command may be more convenient.

This preserves execution provenance.

The result must describe what was actually requested and executed.

---

## 11. Python Interpreter Boundary

On Windows, the command:

```text
python
```

may resolve to a different interpreter depending on the execution environment.

AI-VERIFY therefore does not silently rewrite:

```text
python
```

to another interpreter.

This is an intentional boundary.

If a specific interpreter is required, the user can explicitly provide it in the command.

For example:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

This keeps interpreter selection explicit and reproducible.

---

## 12. Shell Execution Policy

The controlled executor uses:

```python
shell=False
```

The MVP does not accept arbitrary shell scripts through a shell interpreter as part of its controlled execution mechanism.

This reduces shell interpretation risks and keeps command execution closer to the explicit argument list supplied by the verification workflow.

However:

> `shell=False` is a command-execution control, not a complete security sandbox.

---

## 13. Operating-System Sandbox Limitation

AI-VERIFY's controlled execution layer is **not a complete operating-system sandbox**.

It does not provide:

* container isolation
* virtual-machine isolation
* filesystem permission virtualization
* network isolation
* process privilege isolation
* operating-system capability restrictions
* malicious-code containment

Therefore, repository code executed by the verification process should be treated as potentially capable of performing actions permitted to the executing user account.

The current MVP deliberately does not claim full sandbox security.

---

## 14. Timeout Boundary

Controlled execution accepts an explicit timeout.

If the process exceeds the configured timeout:

```text
Process exceeds timeout
        ↓
ExecutionStatus = TIMED_OUT
        ↓
EvidenceStatus = INCONCLUSIVE
```

A timeout does not automatically prove that the software requirement is violated.

This distinction prevents an infrastructure or execution problem from becoming a false verification failure.

---

## 15. Failed Execution Boundary

If an executed command terminates unsuccessfully:

```text
ExecutionStatus = FAILED
```

the execution evidence adapter maps the result to:

```text
EvidenceStatus = INCONCLUSIVE
```

unless contradictory evidence is supplied separately through an appropriate evidence path.

Therefore:

```text
Command failure
    ≠
Requirement contradiction
```

This prevents the system from confusing inability to complete an observation with proof of incorrect behavior.

---

## 16. Raw Execution Output

Execution output includes information such as:

```text
stdout
stderr
exit code
execution status
command
working directory
timeout
```

Raw output is not itself the final verification decision.

It must pass through the evidence adaptation process.

Conceptually:

```text
Raw Execution Result
        ↓
Evidence Adapter
        ↓
Structured Evidence
        ↓
Deterministic Decision
```

This keeps execution mechanics separate from verification semantics.

---

## 17. Evidence Integrity Boundary

Evidence must contain structured information describing its origin.

Evidence includes fields such as:

```text
evidence_id
status
description
source
evidence_type
observation
execution_id
```

This preserves provenance.

Evidence should not be accepted as an unexplained assertion.

The verification system should be able to answer:

> **Where did this observation come from?**

---

## 18. Evidence Status Boundary

Evidence can have three statuses:

```text
SUPPORTS
CONTRADICTS
INCONCLUSIVE
```

These statuses must not be confused.

### SUPPORTS

Provides evidence consistent with the requirement.

### CONTRADICTS

Provides evidence that the requirement is violated.

### INCONCLUSIVE

Does not establish either satisfaction or contradiction.

This distinction is particularly important for execution failures and timeouts.

---

## 19. Deterministic Decision Boundary

The final verification result is determined by deterministic rules.

The decision engine recognizes:

```text
VERIFIED
PARTIALLY VERIFIED
NOT VERIFIED
```

The decision rules are:

```text
Contradiction exists
    ↓
NOT VERIFIED
```

```text
No contradiction
+
Insufficient support
    ↓
PARTIALLY VERIFIED
```

```text
No contradiction
+
Sufficient support
    ↓
VERIFIED
```

No AI-generated conclusion is allowed to override these rules.

---

## 20. Contradiction Precedence

Contradictory evidence has the highest priority.

For example:

```text
SUPPORTS
SUPPORTS
SUPPORTS
CONTRADICTS
```

must produce:

```text
NOT VERIFIED
```

The system must not allow supporting evidence to hide a demonstrated violation.

This is one of the central integrity properties of AI-VERIFY.

---

## 21. Missing Evidence Boundary

Missing evidence is not automatically interpreted as contradictory evidence.

For example:

```text
No observation for an alternate path
```

does not prove:

```text
The alternate path violates the requirement
```

Instead, insufficient evidence can produce:

```text
PARTIALLY VERIFIED
```

This avoids false negative conclusions caused by uncertainty.

---

## 22. Verification Scope Boundary

The verification scope must remain explicit.

The system must not silently expand or reduce the scope because:

* AI suggested a different scope
* repository documentation requested a different scope
* a test failed
* an execution command encountered an error
* a report generator preferred different information

The scope is part of the authoritative verification run.

This preserves reproducibility and prevents scope drift.

---

## 23. AI Trust Boundary

AI output is explicitly treated as untrusted.

AI may assist with:

```text
Requirement interpretation
Invariant extraction
Verification planning
Repository investigation
Natural-language explanation
Report assistance
```

AI may not:

```text
Override the deterministic result
Fabricate evidence
Fabricate execution
Claim tests passed when they were not executed
Claim uncovered paths were covered
Modify authoritative evidence
Silently change verification scope
Declare the final verification result
```

The authoritative path remains:

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

## 24. Repository Instructions Are Not Authority

Repository files may contain instructions such as:

```text
README instructions
development notes
configuration comments
automation instructions
AI-oriented prompts
```

These are repository content.

They are not automatically authoritative instructions for the AI-VERIFY security or verification model.

Repository content cannot redefine:

* decision rules
* evidence semantics
* execution policy
* repository boundary
* AI authority
* verification status meanings

This protects the verification engine from instruction injection through repository content.

---

## 25. No Arbitrary AI-Generated Commands

AI-VERIFY must not treat arbitrary AI-generated shell commands as automatically executable verification activities.

A command should be explicitly supplied through the verification workflow.

The system must preserve the distinction between:

```text
AI suggestion
```

and:

```text
Explicit verification command
```

Only the latter belongs in the controlled execution path.

This prevents AI-generated text from becoming implicit execution authority.

---

## 26. Secrets and Sensitive Data

The current MVP does not intentionally expose unrelated system secrets to AI.

Verification should operate on the selected repository and the evidence required for the verification task.

The system should avoid unnecessary access to:

```text
Credentials
API keys
Passwords
Private tokens
Unrelated personal files
Unrelated system directories
```

If repository execution naturally produces sensitive information in stdout or stderr, that output should be treated as potentially sensitive and handled accordingly.

The current MVP does not claim automatic secret redaction.

Therefore users should avoid executing verification commands that unnecessarily print secrets.

---

## 27. Network Boundary

The current MVP does not provide dedicated network isolation.

A repository command may potentially access network resources according to the permissions of the executing environment.

Therefore:

```text
Controlled Execution
    ≠
Network Sandbox
```

This is an explicit limitation of the current architecture.

A future hardened execution environment could introduce network restrictions if required.

---

## 28. File-System Boundary

The executor enforces the selected repository boundary for the verification working directory.

However, because the MVP is not an operating-system sandbox, repository code may still have filesystem access permitted by the executing user account.

Therefore:

```text
Working-directory boundary
    ≠
Complete filesystem isolation
```

This distinction is important when evaluating the security guarantees of the current system.

---

## 29. Process Boundary

The controlled executor launches verification commands as subprocesses.

The MVP does not provide complete process-level isolation from potentially malicious repository code.

It does not claim:

* privilege separation
* process containment
* process capability restrictions
* kernel-level isolation

Future hardened execution environments could add these protections.

---

## 30. Report Integrity Boundary

Reports are generated from the structured verification result.

The report writer does not independently determine whether a requirement is verified.

Therefore:

```text
Verification Decision
        ↓
Report
```

rather than:

```text
Evidence
        ↓
Report decides result
```

The report cannot legitimately change:

* verification status
* decision rule
* rationale
* evidence
* provenance

This preserves the distinction between authoritative data and presentation.

---

## 31. Run Package Integrity

AI-VERIFY supports lightweight deterministic integrity checking for verification run packages.

The current implementation:

1. serializes the run into a canonical representation
2. calculates a SHA-256 hash
3. compares it against an expected hash

This helps detect changes to the represented run data.

However:

> This is not a complete production-grade tamper-resistance mechanism.

It does not provide a secure external key-management or signing infrastructure.

---

## 32. Reproducibility Boundary

A verification run preserves:

```text
Run ID
Requirement
Invariant
Scope
Verification Plan
Evidence
Decision
Provenance
Schema Version
```

This supports reproducibility and inspection.

However, complete environmental reproducibility may still depend on:

* Python version
* installed packages
* operating system
* repository state
* external services
* environment configuration

Therefore the MVP should distinguish:

```text
Deterministic decision logic
```

from:

```text
Complete environmental reproducibility
```

---

## 33. Security Validation

Security and boundary behavior were explicitly validated during the BUILD-19 phase.

The focused validation covered:

```text
Executor boundary      10/10
CLI boundary           11/11
Serialization + writer 13/13
Integration             3/3
```

Total:

```text
37/37 focused security/boundary tests passed
```

The full regression suite remained:

```text
122/122 tests passed
```

These results validate the implemented security boundaries of the MVP.

They do not constitute a claim of complete security against arbitrary malicious code.

---

## 34. Security Model Limitations

The current MVP intentionally does not provide:

* complete OS sandboxing
* container isolation
* VM isolation
* network isolation
* privilege separation
* automatic secret redaction
* production cryptographic signing
* multi-tenant isolation
* malicious repository containment

These are explicit limitations rather than hidden capabilities.

---

## 35. Security Invariants

The following security properties are treated as architectural invariants:

1. Verification operates only on the explicitly selected repository.
2. The working directory must remain within the selected repository.
3. Controlled execution uses `shell=False`.
4. Explicit commands must not be silently rewritten.
5. AI output is untrusted.
6. Repository instructions are untrusted.
7. AI cannot override deterministic verification results.
8. AI cannot fabricate evidence or execution.
9. Failed execution does not automatically become contradictory evidence.
10. Timed-out execution becomes inconclusive evidence.
11. Missing evidence does not automatically become contradiction.
12. Verification scope must remain explicit.
13. Reports cannot modify authoritative decisions.
14. Provenance must be preserved.
15. The system must not claim sandbox capabilities that it does not provide.

---

## 36. Security Boundary Summary

The current AI-VERIFY security model can be summarized as:

```text
                 UNTRUSTED
┌──────────────────────────────────────┐
│ Repository                           │
│ Tests                                │
│ Documentation                        │
│ Configuration                        │
│ Raw Execution Output                 │
│ AI Output                            │
└───────────────────┬──────────────────┘
                    │
                    ▼
          Controlled Validation
                    │
                    ▼
          Structured Evidence
                    │
                    ▼
       Deterministic Decision Engine
                    │
                    ▼
          Authoritative Result
                    │
                    ▼
             JSON / Markdown
```

The fundamental security principle remains:

> **AI-VERIFY does not trust what should be proven. It validates evidence and applies deterministic rules.**

At the same time, the current MVP is honest about its execution-security limitations:

> **Controlled execution is process control, not a complete operating-system sandbox.**

This distinction is essential to the credibility of the system.
