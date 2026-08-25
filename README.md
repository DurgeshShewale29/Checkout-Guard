# CheckoutGuard AI

CheckoutGuard is an agentic failure-recovery layer sitting between an AI buyer agent and backend checkout APIs (like Razorpay). 

## 🎯 Problem Statement

AI Agents attempting autonomous purchases frequently encounter complex, multi-step checkout flows and payment failures (e.g. expired tokens, 3DS consent challenges, hard bank declines). Most standard API clients simply crash or throw generic `HTTP 400` errors, requiring human intervention.

**CheckoutGuard** solves this by acting as an autonomous middle-layer. It intercepts raw payment errors, classifies them using a deterministic taxonomy, and uses a self-healing Agent Loop to automatically apply the correct fix (e.g. refreshing a token, requesting user consent) and retrying the transaction, or safely escalating unrecoverable errors. All actions are rigorously logged in an audit database for financial compliance.

## 🏗️ Architecture

```text
[ AI Buyer Agent ] 
       │ 
       ▼ (1) POST /api/payments
[ CheckoutGuard API (FastAPI) ] ── (2) Simulate API Call ──▶ [ Mock Razorpay / API ]
       │                                                              │
       ▼ (3) If Error                                                 ▼ 
[ Decision Engine ] ◀─────────────────────── (4) Return Error Payload ─┘
       │
       ▼ (5) Classify & Decide Action
[ Agent Loop (agent.py) ]
       │
       ├─▶ IF RETRYABLE: Apply fix (e.g. Real Razorpay Payment Link creation), Increment retry count, GOTO (2)
       │
       └─▶ IF ESCALATE: Halt cleanly, return structured reason to AI Buyer
       │
       ▼ (6) Log every attempt
[ SQLite Audit Database ] ◀── [ Web Dashboard ]
```

## 🌍 Real vs Simulated Interactions
To safely test failure loops without relying on flaky third-party testing sandboxes, most initial failures are **simulated** (e.g. returning a mock `token_expired` JSON response). However, when the Agent Loop applies a corrective action, it executes **genuine API calls to Razorpay's live Test servers**:
1. **Missing Consent**: The initial consent missing error is simulated. To correct this, the Agent generates a *real* Razorpay Payment Link (`POST /v1/payment_links`) to re-request consent, producing a verifiable S2S `200 OK` success metric.
2. **Subscription Failure (Second Scenario)**: Proving that the decision engine generalizes beyond a standard checkout, we added a recurring payment failure scenario. It simulates an expired saved card, which the engine successfully identifies and maps to the existing `token_expired` rule, automatically attempting a token refresh.

## ✨ Advanced Features (Stretch Goals)
- **LLM-Based Classifier Fallback:** If the rule-based decision engine encounters a completely unknown or ambiguous error structure, it falls back to a Gemini 2.5 Flash LLM prompt. The LLM dynamically maps the unstructured error to the known taxonomy.
- **Confidence Scores:** Every decision made by the engine is assigned a Confidence Score (0-100%). Rule-based matches score 100%, while LLM fallbacks provide their own computed confidence, which is tracked in the SQLite DB and displayed in the UI.
- **Rate-Limiting / Abuse Protection:** An in-memory sliding window rate limiter protects the backend from infinite loops by halting execution and escalating if an `order_id` triggers more than 5 attempts within a 60-second window.

## 💻 Tech Stack
- **Backend:** Python 3, FastAPI, HTTPX
- **AI/LLM:** Google Generative AI (`gemini-2.5-flash`)
- **Persistence:** SQLite (Built-in)
- **Frontend Dashboard:** Vanilla HTML/JS/CSS (Dense, utilitarian engineering UI with no build step required)
- **Design Pattern:** Rule-based Autonomous Agent Loop with LLM Fallback

## 🚀 How to Run Locally

1. **Clone the repository and enter the directory:**
   ```bash
   git clone <repo-url>
   cd Checkout-Guard
   ```

2. **Set up the virtual environment (Windows):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```env
   RAZORPAY_KEY_ID=your_key_here
   RAZORPAY_KEY_SECRET=your_secret_here
   GEMINI_API_KEY=your_gemini_key_here  # Required for LLM Fallback
   ```

4. **Start the FastAPI Server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

4. **View the Dashboard:**
   Open your browser and navigate to:
   [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
   *(Be sure to include the trailing slash!)*

5. **Run the Demo:**
   Use the buttons at the top of the dashboard to trigger live simulated failures and watch the Agent Loop autonomously recover or escalate them!

6. **Run the Automated Tests:**
   You can run the terminal test harness to see the agent logic execute directly in the console (including max-retries and rate-limiter enforcement).
   ```powershell
   python test_agent_loop.py
   ```
