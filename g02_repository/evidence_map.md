# G-02 Requirement Evidence Map

## Requirement

REQ-G02-001:

An order must not be marked as paid unless the corresponding payment has been successfully completed.

## Invariant

order.status == "paid" => payment.status == "completed"

## Components

- api/order_api.py
- services/order_service.py
- services/payment_service.py
- domain/repository.py
- domain/models.py

## Execution Paths

### Path 1 — Create Order

OrderAPI.create_order()
-> OrderService.create_order()
-> OrderRepository.save()

Expected:
order.status == "pending"

Evidence:
Existing API test.

### Path 2 — Successful Payment

OrderAPI.pay_order()
-> OrderService.pay_order()
-> PaymentService.process_payment()
-> payment.status = "completed"
-> order.status = "paid"

Expected:
Payment succeeds before order becomes paid.

Evidence:
Existing order test.
Existing API payment test.
Existing end-to-end runtime validation.

### Path 3 — Missing Order

OrderAPI.pay_order()
-> OrderService.pay_order()
-> order lookup returns None
-> returns False

Evidence:
Source path exists.
No dedicated baseline test.

### Path 4 — Payment Failure

OrderAPI.pay_order()
-> OrderService.pay_order()
-> PaymentService.process_payment()
-> payment failure
-> order must NOT become paid

Current state:
NOT EXERCISED.

Reason:
Current PaymentService implementation always returns True.

Required evidence:
Controlled failure-path test.

### Path 5 — Cross-Component Invariant

PaymentService result
must control whether OrderService sets:

order.status = "paid"

Current state:
PARTIALLY EVIDENCED.

Reason:
Successful path is tested, but failure behavior is not.

## Existing Evidence

- 7 baseline tests pass.
- Payment success is tested.
- Order paid state after successful payment is tested.
- API payment flow is tested.
- Cross-component success path is exercised.

## Missing Evidence

- Explicit payment failure test.
- Proof that failed payment cannot produce a paid order.
- Evidence covering the failure branch.
- Evidence sufficient to verify the invariant across the failure path.

## Current Verification State

PARTIALLY VERIFIED

Reason:

The successful execution path is evidenced, but the requirement's failure/safety path has not yet been exercised.
