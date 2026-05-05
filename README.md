# Bingo Blast

Bingo Blast is a full-stack bingo game with a FastAPI backend, MongoDB persistence, a React Native / Expo frontend, live multiplayer rooms, computer matches, missions, battle pass progression, guilds, cosmetics, and a browser-based backend dashboard for testing.

## Project Layout

- `backend/` - FastAPI API, WebSockets, MongoDB integration, backend tests, smoke scripts, and the dashboard
- `frontend/` - Expo Router mobile / web client
- `graphify-out/` - Graphify knowledge graph artifacts for architecture exploration
- `tests/` - repository-level helper fixtures and scripts

## Main Features

- Guest login and user profiles
- Bingo room creation and joining
- Live WebSocket multiplayer games
- Computer match flow with dab, bingo claims, and powerups
- Daily streaks and spin wheel rewards
- Missions, battle pass, achievements, collection, VIP, cosmetics
- Guild creation and membership
- Shop items and Razorpay mock / live flows
- Backend dashboard with live test running

## Backend Overview

The backend lives in `backend/server.py` and exposes all API routes under `/api`.

### Key collections in MongoDB

- `users`
- `rooms`
- `matches`
- `transactions`
- `guilds`

### Important backend endpoints

- `GET /api/`
- `POST /api/guest/login`
- `GET /api/user/{user_id}`
- `POST /api/user/update`
- `GET /api/avatars/list`
- `POST /api/daily-reward/claim`
- `GET /api/streak/{user_id}`
- `POST /api/spin-wheel/spin`
- `GET /api/rooms`
- `POST /api/rooms`
- `GET /api/rooms/{room_id}`
- `POST /api/rooms/{room_id}/join`
- `POST /api/computer-match`
- `POST /api/computer-match/call`
- `POST /api/computer-match/dab`
- `POST /api/computer-match/use-powerup`
- `POST /api/computer-match/claim-bingo`
- `GET /api/missions/{user_id}`
- `POST /api/missions/claim`
- `GET /api/battle-pass/{user_id}`
- `POST /api/battle-pass/claim`
- `POST /api/battle-pass/activate-premium`
- `GET /api/collection/{user_id}`
- `POST /api/collection/claim`
- `GET /api/event/current`
- `GET /api/leaderboard`
- `GET /api/tournaments`
- `POST /api/tournament/register`
- `GET /api/achievements/{user_id}`
- `GET /api/friends/{user_id}`
- `POST /api/friends/add`
- `GET /api/transactions/{user_id}`
- `GET /api/shop/items`
- `GET /api/payments/razorpay/config`
- `POST /api/payments/razorpay/create-order`
- `POST /api/payments/razorpay/verify`
- `POST /api/matchmaking/join`
- `GET /api/matchmaking/status/{entry_id}`
- `POST /api/matchmaking/cancel/{entry_id}`
- `GET /api/vip/info/{user_id}`
- `POST /api/vip/activate`
- `GET /api/cosmetics/{user_id}`
- `POST /api/cosmetics/equip`
- `POST /api/guilds/create`
- `GET /api/guilds/list`
- `GET /api/guilds/{guild_id}`
- `POST /api/guilds/join`
- `POST /api/guilds/leave`
- `POST /api/push/register`
- `GET /api/dashboard/data`
- `POST /api/dashboard/test-runs`
- `GET /api/dashboard/test-runs`
- `GET /api/dashboard/test-runs/{run_id}`

## Backend Dashboard

The backend includes a full static dashboard at:

- `/dashboard/`

It contains:

- Overview cards
- API explorer
- Data model view
- Testing panel
- Operations notes
- Live test runner for pytest and smoke tests

The dashboard also reads:

- `GET /api/dashboard/data`

## Environment Variables

### Backend

Create `backend/.env` with:

```bash
MONGO_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=bingo_blast

USE_REAL_RAZORPAY=false
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

### Frontend

Create `frontend/.env` with:

```bash
EXPO_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

For production, replace it with your deployed API URL.

## MongoDB Atlas Setup

1. Create an Atlas cluster.
2. Create a database user with read / write access.
3. Add your IP under Network Access.
4. For serverless or dynamic hosts, allow `0.0.0.0/0` temporarily or use a more secure network strategy.
5. Copy the connection string from Atlas Drivers and paste it into `MONGO_URL`.

The backend now uses `certifi` explicitly for TLS validation with Atlas.

## Local Development

### Backend

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend docs:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/dashboard/`
- `http://127.0.0.1:8000/api/dashboard/data`

### Frontend

```bash
cd frontend
yarn install
yarn start
```

## Running Tests

The backend test suite is split into three main parts:

- `backend/tests/test_bingo_blast.py`
- `backend/tests/test_api_extended.py`
- `backend/tests/test_engagement_phases.py`

Run everything:

```bash
cd backend
source .venv/bin/activate
pytest
```

Run a single test file:

```bash
pytest tests/test_api_extended.py
pytest tests/test_engagement_phases.py
pytest tests/test_bingo_blast.py
```

### Smoke Test Script

Run the live smoke script against a running API:

```bash
python scripts/smoke_test_apis.py --base-url http://127.0.0.1:8000
```

Optional WebSocket check:

```bash
python scripts/smoke_test_apis.py --base-url http://127.0.0.1:8000 --skip-ws
```

## Git Workflow

This repository is now set up with:

- local git history
- remote origin: `git@github.com:byrty7/bingo-blast-prod.git`
- `main` tracking `origin/main`

### Typical workflow

```bash
git status
git add .
git commit -m "your message"
git push
```

### Helpful commands

Show current branch and tracking:

```bash
git status --short --branch
```

Show remotes:

```bash
git remote -v
```

Fetch latest remote changes:

```bash
git fetch origin
```

### Notes on this repo

- `.env` files are ignored and should not be committed.
- `frontend/.metro-cache/` and Graphify caches should remain untracked.
- If you add new dashboard or test artifacts, keep them in the backend and document them here.

## Graphify

The repo includes Graphify outputs under `graphify-out/`.

Useful files:

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`
- `graphify-out/graph.json`

These help inspect backend architecture, community structure, and high-connectivity functions.

## Deployment Notes

- Backend needs a Python host that supports FastAPI and WebSockets.
- MongoDB Atlas is recommended for production.
- Frontend needs `EXPO_PUBLIC_BACKEND_URL` set at build time.
- If you deploy the Expo web app separately, point it to the live backend URL.

## Contributing

1. Create a branch.
2. Make your changes.
3. Run tests locally.
4. Update the dashboard or README if you add routes or features.
5. Commit and push.

## License

See `LICENSE` if present in the remote repository.
