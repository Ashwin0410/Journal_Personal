# Journal.

A warm, personal journal app for you and your people. No fancy AI, no bloat — just a clean place to write, capture, and remember.

## Features

- **Daily Timeline** — Add text notes, photos, voice notes, videos, tasks, and gratitude entries. Everything groups by date.
- **Calendar View** — Browse past entries by date. Dots show which days have entries.
- **On This Day** — See what you wrote on this date in previous months and years. Memories surface automatically.
- **Mood Tracking** — Optional mood tags on entries.
- **Simple Auth** — Email + password login. No Google, no OAuth, no fuss.
- **Mobile Friendly** — Responsive design with collapsible sidebar.

## Tech Stack

- **Backend:** FastAPI + PostgreSQL + SQLAlchemy
- **Frontend:** React (single HTML file, CDN-loaded)
- **Auth:** JWT (30-day tokens, bcrypt password hashing)
- **Hosting:** Render (free tier)

## Deploy to Render

### Option 1: Blueprint (Easiest)

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your GitHub repo
5. Render reads `render.yaml` and sets up everything (database + web service)
6. Wait for deploy — done!

### Option 2: Manual Setup

1. **Create a PostgreSQL database** on Render (free tier)
2. **Create a Web Service:**
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Set environment variables:**
   - `DATABASE_URL` — from your Render Postgres (Internal Database URL)
   - `SECRET_KEY` — any random string (click "Generate" in Render)

## Run Locally

```bash
# Clone and enter directory
cd journal-app

# Install dependencies
pip install -r requirements.txt

# Run (uses SQLite locally by default)
uvicorn app.main:app --reload

# Open http://localhost:8000
```

To use PostgreSQL locally, set:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/journal"
```

## Project Structure

```
journal-app/
├── app/
│   ├── main.py          # FastAPI app, routes, serves frontend
│   ├── models.py         # SQLAlchemy models (User, Entry)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT + bcrypt auth utilities
│   └── database.py       # Database connection setup
├── static/
│   └── index.html        # React frontend (single file)
├── requirements.txt
├── render.yaml           # Render deployment blueprint
└── README.md
```

## Notes

- **Media storage:** Images, voice notes, and videos are stored as base64 in the database. This is simple and works great for a small group. For heavy media use, consider switching to S3/Cloudinary.
- **Free tier limits:** Render's free Postgres gives 1GB storage. Plenty for text entries, but media will use it faster.
- **Local dev:** Without `DATABASE_URL` set, it falls back to SQLite (`journal.db` in the project root).
