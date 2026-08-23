# CheckoutGuard — Build Task List

**Track:** Track 1 — AI Growth & Agentic Commerce (Razorpay AI Buildathon 2026)
**Project:** An agentic failure-recovery layer that sits between an AI buyer and Razorpay's test-mode checkout APIs — classifies why a payment failed, decides retry vs escalate, and logs every decision.

---

## Phase 0 — Setup

- [ ] Create Razorpay account and enable **Test Mode**
- [ ] Generate Test Mode API Key ID + Key Secret
- [ ] Set up project folder structure (`/backend`, `/frontend`, `/docs`)
- [ ] Initialize backend (FastAPI or Express — pick one)
- [ ] Set up `.env` for API keys (never commit this)
- [ ] Initialize git repo, create public GitHub repo
- [ ] Write initial `README.md` with project name + one-line description

---

## Phase 1 — Baseline Payment Flow (Happy Path)

- [ ] Integrate Razorpay Orders API — create a test order
- [ ] Integrate Razorpay Payments API — attempt a payment against that order
- [ ] Confirm a successful test payment works end to end (use Razorpay test card `4111 1111 1111 1111`)
- [ ] Log the successful transaction (order id, payment id, status, timestamp)
- [ ] Verify webhook or polling method to confirm payment status

**Checkpoint:** You can create an order and complete a successful test payment programmatically, no UI needed yet.

---

## Phase 2 — Failure Simulation

- [ ] Use Razorpay test card numbers that simulate **declines** (check Razorpay test card docs for decline codes)
- [ ] Simulate a **timeout** failure (mock this — Razorpay won't natively give you one, so build a controlled test hook)
- [ ] Simulate a **missing consent / auth failure** (mock this too, as a controlled failure injection)
- [ ] Simulate an **expired token** failure (mock via forcing an invalid/expired auth reference)
- [ ] Confirm each simulated failure returns a distinguishable error code/message from your system

**Checkpoint:** You can deliberately trigger at least 4 distinct failure types on demand.

---

## Phase 3 — Failure Taxonomy

- [ ] Define a taxonomy table mapping failure type → {retryable / not retryable} → suggested corrective action
  - [ ] Soft decline → retryable → retry with same method
  - [ ] Hard decline → not retryable → escalate
  - [ ] Expired token → retryable → refresh token, retry
  - [ ] Missing consent → retryable → re-request consent, retry
  - [ ] Timeout → retryable (limited attempts) → retry once, then escalate
- [ ] Store this taxonomy as a config file (JSON/YAML) so it's easy to explain and modify later

**Checkpoint:** You have a documented, defensible rulebook for retry vs escalate decisions.

---

## Phase 4 — Decision Engine

- [ ] Build a classifier function: input = failure response → output = failure category (using the taxonomy)
- [ ] Build a decision function: input = failure category + current retry count for this transaction → output = {retry with corrected action} or {escalate}
- [ ] Implement a **bounded retry limit** (e.g., max 2 retries per transaction) to prevent infinite loops
- [ ] Implement the actual retry action (re-attempt payment with corrected parameter — e.g., different payment method or refreshed token)
- [ ] Implement the escalate action (halt cleanly, return a clear structured reason)

**Checkpoint:** Given any simulated failure, the system automatically decides and acts — retry or escalate — without manual intervention.

---

## Phase 5 — Audit Logging

- [ ] Design log schema: `transaction_id, attempt_number, failure_type, action_taken, outcome, timestamp, reasoning`
- [ ] Log every attempt (not just the final outcome) — this is your core evidence for "failure recovery"
- [ ] Store logs in SQLite or a structured JSON file
- [ ] Add a way to query/export the full audit trail for a given transaction

**Checkpoint:** You can pull up any transaction and see a full, explainable timeline of what happened and why.

---

## Phase 6 — Dashboard (Minimal, Not Fancy)

- [ ] Build a simple frontend (React or plain HTML/JS) — one page is enough
- [ ] Table view: transaction id, status, failure type, action taken, final outcome
- [ ] Detail view: click a transaction → see full attempt-by-attempt log with reasoning
- [ ] "Trigger demo failure" buttons for the pitch (so you're not relying on live flaky test conditions during the demo)

**Checkpoint:** You can visually walk a panel through a transaction's failure-and-recovery story in under 60 seconds.

---

## Phase 7 — Demo Script Prep

- [ ] Prepare Demo Flow A: failure that gets auto-corrected and succeeds on retry
- [ ] Prepare Demo Flow B: failure that correctly escalates after hitting retry limit
- [ ] Time both flows — should take under 2 minutes combined
- [ ] Write down the "what broke while building this" story with specifics (real bug, real fix)

**Checkpoint:** Your two demo flows are reliable and repeatable — no live flakiness risk during the pitch.

---

## Phase 8 — Documentation & Submission

- [ ] Finish README: problem statement, architecture diagram, how to run locally, tech stack used
- [ ] Add architecture diagram (simple boxes-and-arrows is fine — AI buyer → CheckoutGuard → Razorpay API)
- [ ] Clean up repo: remove dead code, add comments to core decision engine logic
- [ ] Record 5-minute pitch video (problem → live demo → architecture → what broke & how you fixed it → why it matters)
- [ ] Fill out application form: Project Name, Objectives, GitHub URL, Pitch Video Link
- [ ] Submit before deadline (**September 5**)

---

## Stretch Goals (only if core flow is solid and you have time left)

- [ ] Add an LLM-based classifier for ambiguous/unstructured failure messages (on top of the rule-based one)
- [ ] Add a second AI-buyer simulation scenario (e.g., subscription payment retry instead of one-time purchase)
- [ ] Add basic rate-limiting/abuse protection on the retry engine
- [ ] Add a confidence score to each classification decision
