# CheckoutGuard

> Agentic failure-recovery layer between an AI buyer and Razorpay's checkout APIs.

## What it does

CheckoutGuard sits between an AI buyer agent and Razorpay's test-mode payment APIs. When a payment fails, it:

1. **Classifies** the failure (soft decline, hard decline, timeout, expired token, missing consent)
2. **Decides** — retry with a corrective action, or escalate cleanly
3. **Logs** every decision with full reasoning for audit and explainability

Built for **Razorpay AI Buildathon 2026 — Track 1: AI Growth & Agentic Commerce**.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| Payment API | Razorpay Test Mode (Orders + Payments API) |
| Decision Engine | Rule-based classifier (+ optional LLM layer) |
| Audit Log | SQLite via SQLAlchemy (async) |
| Frontend | React (Vite) |

---

## Project Structure

```
checkout-guard/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── routers/         # API routes (Phase 1+)
│   │   ├── engine/          # Decision engine (Phase 4)
│   │   └── models/          # SQLAlchemy models (Phase 5)
│   ├── .env.example         # Copy to .env and fill in your keys
│   └── requirements.txt
├── frontend/                # Dashboard (Phase 6)
├── docs/                    # Architecture diagrams
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node 18+ (for frontend, Phase 6)
- Razorpay account with Test Mode enabled

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure secrets
copy .env.example .env
# Edit .env and fill in RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET

# Run
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API explorer.

---

## Architecture

```
AI Buyer → CheckoutGuard → Razorpay API
              ↓
         [Failure?]
              ↓
     Classify failure type
              ↓
     Retry / Escalate decision
              ↓
         Audit log
```

*(Full diagram in `/docs`)*

---

## License

MIT
