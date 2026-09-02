# CheckoutGuard AI

CheckoutGuard is an end-to-end autonomous purchasing pipeline and failure-recovery layer. It enables AI agents to make purchasing decisions from a catalog and execute them, while a self-healing middleware layer intercepts and resolves any complex backend payment errors (like those from Razorpay).

## 🎯 Problem Statement

AI Agents attempting autonomous purchases frequently encounter complex, multi-step checkout flows and payment failures (e.g. expired tokens, 3DS consent challenges, hard bank declines). Most standard API clients simply crash or throw generic `HTTP 400` errors, requiring human intervention.

**CheckoutGuard** solves this by providing a full "decide → buy → recover" loop. First, an **Autonomous AI Buyer** translates natural language into a concrete product purchase. Then, the **CheckoutGuard Middleware** intercepts raw payment errors, classifies them using a deterministic taxonomy, and uses a self-healing Agent Loop to automatically apply the correct fix (e.g. requesting user consent, refreshing a token) and retry the transaction. All actions are rigorously logged in an audit database for financial compliance.

## 🏗️ Architecture

```text
[ Natural Language Intent ]
       │
       ▼ (1) POST /api/dashboard/trigger_ai_buyer
[ AI Buyer Agent (Groq LLM) ] ──▶ Translates intent to Product ID
       │ 
       ▼ (2) POST /api/payments/orders
[ CheckoutGuard API ] ─────────── (3) Simulate API Call ──▶ [ Mock Razorpay / API ]
       │                                                              │
       ▼ (4) If Error                                                 ▼ 
[ Decision Engine ] ◀─────────────────────── (5) Return Error Payload ─┘
       │
       ▼ (6) Classify & Decide Action
[ Agent Loop (agent.py) ]
       │
       ├─▶ IF RETRYABLE: Apply fix (e.g. Real Payment Link), Increment retry, GOTO (3)
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
- **Full Autonomous Purchasing Loop:** Users can chat directly with the dashboard to state a buying intent (e.g. "buy a birthday gift for my sister"). The AI Buyer parses the catalog, triggers the order, and routes it directly into the CheckoutGuard recovery loop.
- **LLM-Based Classifier Fallback:** If the rule-based decision engine encounters a completely unknown or ambiguous error structure, it falls back to a Groq LLM prompt. The LLM dynamically maps the unstructured error to the known taxonomy.
- **Confidence Scores:** Every decision made by the engine is assigned a Confidence Score (0-100%). Rule-based matches score 100%, while LLM fallbacks provide their own computed confidence.
- **Rate-Limiting / Abuse Protection:** An in-memory sliding window rate limiter protects the backend from infinite loops by halting execution and escalating if an `order_id` triggers more than 5 attempts within a 60-second window.

## 💻 Tech Stack
- **Backend:** Python 3, FastAPI, HTTPX
- **AI/LLM:** Groq (`qwen/qwen3.6-27b` for intent matching and `llama-3.1-8b-instant` for fallback classification)
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
   GROQ_API_KEY=your_groq_key_here  # Required for AI Buyer & LLM Fallback
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
