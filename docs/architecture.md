# Architecture Diagrams

Architecture diagrams will be added here in Phase 8.

## System Overview

```
AI Buyer Agent
     │
     ▼
CheckoutGuard (this project)
  ├── Payment Router
  ├── Failure Classifier
  ├── Decision Engine (retry / escalate)
  └── Audit Logger
     │
     ▼
Razorpay Test-Mode APIs
  ├── Orders API
  └── Payments API
```
