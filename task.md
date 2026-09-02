# CheckoutGuard — Build Task List

**Track:** Track 1 — AI Growth & Agentic Commerce (Razorpay AI Buildathon 2026)
**Project:** An agentic failure-recovery layer that sits between an AI buyer and Razorpay's test-mode checkout APIs — classifies why a payment failed, decides retry vs escalate, and logs every decision.

---

## Phase 0 — Setup

- [x] Create Razorpay account and enable **Test Mode**
- [x] Generate Test Mode API Key ID + Key Secret
- [x] Set up project folder structure (`/backend`, `/frontend`, `/docs`)
- [x] Initialize backend (FastAPI — Python 3.14, all 29 deps installed)
- [x] Set up `.env` for API keys — `.env.example` committed, real `.env` gitignored
- [x] Initialize git repo — initial commit `9f1ebdb` done (13 files)
- [x] Create public GitHub repo and push
- [x] Write initial `README.md` with project name + one-line description

---

## Phase 1 — Baseline Payment Flow (Happy Path)

- [x] Integrate Razorpay Orders API — create a test order
- [x] Integrate Razorpay Payments API — attempt a payment against that order (simulated via headless UI since S2S restricted)
- [x] Confirm a successful test payment works end to end (use Razorpay test card `4100 2800 0000 1007`)
- [x] Log the successful transaction (order id, payment id, status, timestamp)
- [x] Verify webhook or polling method to confirm payment status (done locally via `/verify` endpoint)

**Checkpoint:** You can create an order and complete a successful test payment programmatically, no UI needed yet.

---

## Phase 2 — Failure Simulation

- [x] Use Razorpay test card numbers that simulate **declines** (mocked in API layer since test UI automation is flaky)
- [x] Simulate a **timeout** failure (mocked via `GET /api/simulate/pay`)
- [x] Simulate a **missing consent / auth failure** (mocked)
- [x] Simulate an **expired token** failure (mocked via forcing an invalid/expired auth reference)
- [x] Confirm each simulated failure returns a distinguishable error code/message from your system

**Checkpoint:** You can deliberately trigger at least 4 distinct failure types on demand.

---

## Phase 3 — Failure Taxonomy

- [x] Define a taxonomy table mapping failure type → {retryable / not retryable} → suggested corrective action
  - [x] Hard decline → not retryable → escalate
  - [x] Expired token → retryable → refresh token, retry
  - [x] Missing consent → retryable → re-request consent, retry
  - [x] Timeout → retryable (limited attempts) → retry once, then escalate
- [x] Store this taxonomy as a config file (JSON) so it's easy to explain and modify later
- [x] A rule-based classifier function mapping a raw error JSON to its taxonomy category
- [x] A decision engine function handling retry logic based on the taxonomy

**Checkpoint:** You have a documented, defensible rulebook for retry vs escalate decisions.

---

## Phase 4 — Decision Engine

- [x] Build a classifier function: input = failure response → output = failure category (using the taxonomy)
- [x] Build a decision function: input = failure category + current retry count for this transaction → output = {retry with corrected action} or {escalate}
- [x] Implement a **bounded retry limit** (e.g., max 2 retries per transaction) to prevent infinite loops
- [x] Implement the actual retry action (re-attempt payment with corrected parameter — e.g., different payment method or refreshed token)
- [x] Implement the escalate action (halt cleanly, return a clear structured reason)

**Checkpoint:** Given any simulated failure, the system automatically decides and acts — retry or escalate — without manual intervention.

---

## Phase 5 — Audit Logging

- [x] Design log schema (transaction_id, attempt_number, failure_type, action_taken, outcome, timestamp, reasoning)
- [x] Implement persistent logging function (SQLite is fine for local test)
- [x] Inject logging into the decision engine loop to record every outcome
- [x] Create a query function to retrieve the full step-by-step history of a transaction

**Checkpoint:** You can run a full failure-and-recovery loop and then print a chronological log showing exactly why the agent did what it did.

---

## Phase 6 — Dashboard (Minimal, Not Fancy)

- [x] Create a minimal HTML/JS frontend to visualize the database
- [x] View 1: A list/table of all transactions and their final outcome
- [x] View 2: Click a transaction to see its step-by-step audit log (attempt 1, attempt 2, etc.)
- [x] Add "Trigger Demo" buttons for each failure type (Decline, Timeout, Consent, Expired Token) so you can run the system live during a presentation without flaky test scripts.

**Checkpoint:** You can click a button, watch the system simulate a failure, and instantly see the full recovery log appear in the dashboard. 60 seconds.

---

## Phase 7 — Demo Script Prep

- [x] Prepare Demo Flow A: failure that gets auto-corrected and succeeds on retry
- [x] Prepare Demo Flow B: failure that correctly escalates after hitting retry limit
- [x] Time both flows — should take under 2 minutes combined
- [x] Write down the "what broke while building this" story with specifics (real bug, real fix)

**Checkpoint:** Your two demo flows are reliable and repeatable — no live flakiness risk during the pitch.

---

## Phase 8 — Documentation & Submission

- [x] Finalize `README.md` with a clear "Problem & Solution" statement for the judges
- [x] Create a simple architecture diagram in the README (text-based is fine)
- [x] Clean up code: remove scratch files, dead routes, add final comments to the decision engine
- [x] Push all code to GitHub (ensure repo is public!)
- [x] Deploy live on Render — public URL: `https://checkout-guard.onrender.com/dashboard/`
- [x] Fix production bugs found post-deploy (pkg_resources/Python version pin, hardcoded loopback URL)

**Checkpoint:** The repo is polished, public, and the live dashboard is verified working end to end in production, not just locally.

---

## Phase 9 — Additional Work (Pre-Submission Hardening)

*Goal: close the "is this real or simulated?" gap and show the engine generalizes beyond one scenario, before recording the final pitch video.*

- [x] **Make one corrective action real (not simulated)** — pick the simplest one (e.g. retry the `missing_consent` scenario by genuinely calling Razorpay's Payment Links API) and replace the current `scenario='success'` shortcut with an actual corrected API call
- [x] Confirm the real corrective action still logs correctly in the audit trail (attempt 0 failed → real corrective action applied → attempt 1 succeeded, with the actual action recorded)
- [x] **Add a second AI-buyer transaction scenario** — e.g. a subscription/recurring-payment retry flow — routed through the same existing decision engine (no new engine logic, just a new entry point/scenario)
- [x] Add a "Trigger" button or flow for the new scenario on the dashboard
- [x] **Add a summary metric to the dashboard** — e.g. "X% of failures auto-recovered / Y% escalated" computed from the audit log, shown above or beside the transactions table
- [x] Test all of the above on the live Render deployment, not just locally
- [x] Update README to reflect what's now real vs. simulated, and describe the second scenario
- [x] Do a full cold-start retest of both original demo flows (A and B) to confirm nothing broke from these changes

**Checkpoint:** At least one corrective action is genuinely real, a second transaction type proves the engine generalizes, and a summary metric gives judges an at-a-glance proof point — all verified live on Render.

---

## Stretch Goals (only if Phase 9 is done early and time remains)

- [x] Add an LLM-based classifier for ambiguous/unstructured failure messages (on top of the rule-based one)
- [x] Add basic rate-limiting/abuse protection on the retry engine
- [x] Add a confidence score to each classification decision


## Phase 10 — UI Polish ✅

- [x] Moved dashboard away from generic dark/pill-badge AI-default look
- [x] Clean light-background, high-contrast, minimal style with plain-text status labels
- [x] Restrained accent color, subtle card depth/shadow, hover states
- [x] Verified readable and professional, not decorated

---

## Phase 11 — AI Buyer Agent (New, Big Addition)

*Goal: cover the OTHER half of Track 1's brief ("makes a merchant transactable by an AI buyer end to end") — not just recovery, but the full loop: an agent that decides to buy, executes the purchase, and lets CheckoutGuard recover from failure autonomously. No changes needed to the existing decision engine, taxonomy, or audit logging — this sits on top as a new trigger source.*

- [x] Build a small mock product catalog (5-10 items, hardcoded JSON — name, price, description)
- [x] Add an LLM call (Anthropic or OpenAI API) that takes a natural-language buying intent (e.g. "buy a birthday gift under ₹1000") and selects a matching product from the catalog
- [x] Wire the LLM's product decision into the existing checkout flow as a new request source (reuse existing Orders/Payments integration — no new payment logic)
- [x] Confirm that when this new flow hits a failure, the existing CheckoutGuard decision engine/taxonomy/audit logging handles it exactly as it does for manual triggers — no special-casing
- [x] Add a simple chat-style input to the dashboard: "Tell the AI Buyer what to purchase" → show the agent's reasoning/choice → show the resulting transaction flow through CheckoutGuard
- [x] Test the full loop end to end locally: natural-language input → product selection → checkout attempt → (optional) failure → recovery/escalation → logged
- [ ] Test the full loop on the live Render deployment
- [x] Keep the existing manual "Trigger" buttons working as-is — this is additive, not a replacement, so they remain a safe fallback demo path
- [ ] Update README to describe the AI Buyer Agent and how it fits with the existing recovery layer
- [ ] Update the 5-min pitch script to lead with this fuller "decide → buy → recover" story instead of just the recovery layer alone

**Checkpoint:** The AI Buyer Agent can take a plain-English purchase instruction, pick a product, attempt checkout, and — if it fails — CheckoutGuard recovers or escalates automatically, all without manual button-clicking. Both the new autonomous flow and the original manual triggers work reliably on the live deployment.

---

## Phase 12 — Final Pitch Prep (Do Last)

- [ ] Re-record the 5-minute pitch video reflecting the AI Buyer Agent + CheckoutGuard as one complete story
- [ ] Do at least 3 full timed dry runs of the pitch, live demo included (both the AI Buyer flow and the manual fallback triggers)
- [ ] Prepare honest answers for likely panel questions:
  - "How would this work with real production APIs, not test mode?"
  - "Which parts are simulated vs. real right now?"
  - "Why rule-based instead of an LLM for the core decision engine, but LLM-based for product selection?"
  - "What happens if the AI Buyer picks something unexpected?"
- [ ] Fill out application form: Project Name, Objectives, GitHub URL, Pitch Video Link
- [ ] Submit before deadline (**September 5**)

**Final Milestone:** Pitch is rehearsed, weak points have honest answers ready, and the form is submitted.
