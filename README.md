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
       ├─▶ IF RETRYABLE: Apply fix (e.g. refresh token), Increment retry count, GOTO (2)
       │
       └─▶ IF ESCALATE: Halt cleanly, return structured reason to AI Buyer
       │
       ▼ (6) Log every attempt
[ SQLite Audit Database ] ◀── [ Web Dashboard ]
```

## 💻 Tech Stack
- **Backend:** Python 3, FastAPI, HTTPX
- **Persistence:** SQLite (Built-in)
- **Frontend Dashboard:** Vanilla HTML/JS/CSS (Served statically by FastAPI, no separate frontend build step required)
- **Design Pattern:** Rule-based Autonomous Agent Loop

## 🚀 How to Run Locally

1. **Clone the repository and enter the backend directory:**
   ```bash
   git clone <repo-url>
   cd CheckoutGuard/backend
   ```

2. **Set up the virtual environment (Windows):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the FastAPI Server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

4. **View the Dashboard:**
   Open your browser and navigate to:
   [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
   *(Be sure to include the trailing slash!)*

5. **Run the Demo:**
   Use the buttons at the top of the dashboard to trigger live simulated failures and watch the Agent Loop autonomously recover or escalate them!
