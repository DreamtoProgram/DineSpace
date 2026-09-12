# DineSpace — Backend Service 🍽️⚡

FastAPI backend service for **DineSpace**, a campus dining hall management web application.

---

## 1. Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point, CORS & lifespan
│   ├── config.py            # Pydantic Settings configuration & env loading
│   ├── database.py          # MongoDB client manager & collection accessors
│   ├── dependencies.py      # Auth dependency (get_current_student via Bearer JWT)
│   ├── models/              # Internal domain models (Student, MenuDocument)
│   ├── schemas/             # Pydantic validation schemas (Health, Auth, Menu)
│   ├── routes/              # API route controllers (/health, /auth, /menu)
│   ├── services/            # Business logic layer (security, auth, menu)
│   └── workers/             # Background tasks (e.g. 60s seat auto-timeout sweeper)
├── scripts/                 # Maintenance and seeding scripts (seed_students, seed_menu)
├── tests/                   # Automated tests with pytest & mongomock
├── .env.example             # Template environment variables
├── requirements.txt         # Minimal production & testing dependencies
└── README.md                # Documentation
```

---

## 2. Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- **MongoDB** (Local instance running on port 27017 or remote MongoDB Atlas URI)

---

## 3. Environment Setup & Installation

### Step 1: Create a Python Virtual Environment
Navigate to the `backend` directory and create a virtual environment:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. Configuration (`.env`)

Copy the template `.env.example` file to `.env`:

```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Configure the environment variables in `.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `"DineSpace Backend"` | Display name of the service |
| `DEBUG` | `True` | Enables Swagger UI at `/docs` when True |
| `API_V1_PREFIX` | `"/api"` | Route prefix for all API endpoints |
| `TIMEZONE` | `"Asia/Kolkata"` | Campus operational timezone |
| `TOTAL_SEATS` | `100` | Total virtual dining hall seat capacity |
| `DEFAULT_DINING_HALL` | `"Central Mess"` | Default dining hall facility |
| `CORS_ORIGINS` | `"http://localhost,..."` | Comma-separated list of allowed frontend origins |
| `MONGODB_URI` | `"mongodb://localhost:27017"` | MongoDB connection string (local or Atlas) |
| `MONGODB_DATABASE` | `"dinespace"` | Database name |
| `JWT_SECRET_KEY` | *(dev key)* | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | `"HS256"` | JWT cryptographic algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token lifespan (24 hours) |
| `DINESPACE_SEAT_TIMEOUT_MINUTES` | `25` | Occupied seat expiration timeout in minutes |
| `DINESPACE_SWEEPER_INTERVAL_SECONDS` | `60` | Background worker periodic check interval in seconds |

---

## 5. Seeding Demo Data

### Demo Students
Populate sample student records with bcrypt-hashed passwords:
```bash
python -m scripts.seed_students
```

**Local Testing Credentials (DEMO ONLY):**
- **Student 1:** `STU1042` / Password: `DineSpace2026!` (Sarah Chen, Active)
- **Student 2:** `STU1043` / Password: `DineSpace2026!` (Alex Sharma, Active)
- **Student 3:** `STU1044` / Password: `DineSpace2026!` (Rahul Singh, Active)
- **Student 4 (Inactive):** `STU9999` / Password: `DineSpace2026!` (Inactive User, Inactive)

### Demo Menus
Populate Lunch and Dinner menus for today:
```bash
python -m scripts.seed_menu
```
*(Optionally pass a custom date: `python -m scripts.seed_menu 2026-09-15`)*

---

## 6. Running the Backend Server

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

When running:
- **Interactive API Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 7. API Endpoints

### Health
- `GET /api/health` — Service liveness check.

### Authentication (Task 1)
- `POST /api/auth/login` — Authenticate student with `studentId` and `password`. Returns JWT token.
- `GET /api/auth/me` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns public student profile.

### Menu (Task 2)
- `GET /api/menu/today` — Returns all meal menus (Lunch, Dinner) for today in campus timezone.
- `GET /api/menu?date=YYYY-MM-DD` — Returns all meal menus for a specific date.
- `GET /api/menu?date=YYYY-MM-DD&mealType=Lunch` — Returns single meal menu for a date.

### Live Occupancy & Crowd Status (Task 3)
- `GET /api/status` — Returns real-time dining hall capacity, occupied count, available count, crowd percentage, crowd level (`Low`, `Moderate`, `Peak Rush`), and meal type. Polled every ~3 seconds by frontend dashboard.

### Entry Scan & Virtual Seat Assignment (Task 4)
- `POST /api/scan/entry` — Protected endpoint requiring `Authorization: Bearer <token>`. Validates student pass code (`passCode`), checks against duplicate active visits, and atomically allocates the next lowest available virtual seat (`1` to `TOTAL_SEATS`). Returns seat assignment and entry timestamp.

### My Visit / Active Session (Task 5)
- `GET /api/visits/current` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns the authenticated student's active dining visit (`seatNumber`, `diningHall`, `entryTime`, dynamic `durationMinutes`, `mealType`) or `{ "active": false, "visit": null }` if no active session exists.

### Tray Return / Exit Scan (Task 6)
- `POST /api/scan/exit` — Protected endpoint requiring `Authorization: Bearer <token>`. Accepts `{ "scanType": "tray_return" }` or empty body. Atomically completes the active dining visit (`status: "completed"`), records timezone-aware `exitTime`, calculates elapsed duration in minutes, releases the virtual seat, and automatically increases available seats on the live crowd status API.

### Automatic Seat Timeout & Sweeper Worker (Task 7)
- **Background Worker**: Managed automatically by the FastAPI lifespan context. Runs an `asyncio` task every 60 seconds (`DINESPACE_SWEEPER_INTERVAL_SECONDS`), querying for active sessions older than 25 minutes (`DINESPACE_SEAT_TIMEOUT_MINUTES`).
- **State Transition**: Matching active visits (`status: "occupied"`, `exitTime: null`, `entryTime < cutoff`) are atomically transitioned to `status: "expired"` with `exitReason: "timeout"` and `exitTime = now`.
- **Seat Release & Crowd Update**: Virtual seats are immediately freed and `GET /api/status` automatically reflects +1 available seat per expired visit. Records remain persisted in MongoDB for future visit history.

### Visit History (Task 8)
- `GET /api/visits/history?limit=20&offset=0` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns paginated past dining sessions (`status IN ["completed", "expired"]`) for the authenticated student, sorted newest first by `exitTime`. Includes on-the-fly `durationMinutes` calculation, `exitReason` (`tray_return` or `timeout`), and pagination metadata (`limit`, `offset`, `total`). Strict student data isolation enforced.

### Notifications (Task 9)
- `GET /api/notifications?type=all&limit=20&offset=0` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns student's paginated notifications with optional category filtering (`all`, `menu`, `crowd`, `visit`, `system`) and total `unreadCount` badge count across all categories.
- `PATCH /api/notifications/{notification_id}/read` — Protected endpoint. Marks a single notification as read (`404` if not found or unauthorized).
- `PATCH /api/notifications/read-all` — Protected endpoint. Marks all unread notifications for the authenticated student as read.
- **Event Integrations**: Automatic creation of `type="visit"` notifications upon tray return completion (`POST /api/scan/exit`) and background worker visit timeout.

### Find a Seat (Task 10)
- `GET /api/seats?diningHall=Central+Mess&status=available` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns real-time virtual seat map (`1` to `capacity`), total capacity, occupied count, available count, the student's own active seat (`mySeat`), the lowest available seat (`nextAvailableSeat`), and individual seat availability states. Complete student privacy enforced with bulk in-memory resolution.

### Settings (Task 11)
- `GET /api/settings` — Protected endpoint requiring `Authorization: Bearer <token>`. Returns student account profile (`studentId`, `name`), assigned dining hall (`Central Mess`), and application preferences (`notificationsEnabled`).
- `PATCH /api/settings` — Protected endpoint. Updates whitelisted preferences (`notificationsEnabled`) using targeted `$set`. Arbitrary fields and identifier tampering are strictly rejected.
- `PATCH /api/settings/password` — Protected endpoint. Securely validates current password against bcrypt hash, verifies length policy, and stores updated hash in MongoDB.
- **Preference Integration**: Future notification delivery respects `preferences.notificationsEnabled`, while preserving historical notifications.

---

## 8. Running Automated Tests & Smoke Tests

### Automated Test Suite (Pytest)
Run the complete regression suite (175 tests across 13 modules):
```bash
pytest tests/ -v
```
Tests run in-memory using `mongomock` and require no live database instance.

### Standalone Pre-Demo Smoke Test
Run the automated pre-demo smoke test exercising all 12 endpoints sequentially:
```bash
python smoke_test.py
```
Automatically falls back to `mongomock` if a local MongoDB instance is not currently active.

---

## 9. Hackathon Demo Checklist 🚀

Before pitching to judges, run through this verification checklist:

- [ ] **1. MongoDB Running**: Local daemon active (`mongod`) or Atlas connection string configured in `.env`.
- [ ] **2. Backend Running**: Started with `uvicorn app.main:app --reload` on port `8000`.
- [ ] **3. Demo Students Seeded**: Ran `python -m scripts.seed_students`.
- [ ] **4. Menus Seeded**: Ran `python -m scripts.seed_menu`.
- [ ] **5. Smoke Test Passes**: Ran `python smoke_test.py` -> `ALL 12 SMOKE TESTS PASSED`.
- [ ] **6. Student Login**: Sign in with `STU1042` / `DineSpace2026!` on the frontend.
- [ ] **7. Dashboard Initial State**: Confirmed `0/100 Occupied`, `100 Seats Available`, `Low Crowd`.
- [ ] **8. Entry Check-In**: Scanned QR / submitted `PASS-8842`. Virtual seat `#1` allocated.
- [ ] **9. Live Occupancy Update**: Available seats dropped to `99`. Student's "My Visit" card shows `#1`.
- [ ] **10. Tray Return**: Scanned tray return QR. Seat `#1` released immediately. Status back to `100 Available`.
- [ ] **11. Visit History**: Confirmed completed visit appears under Visit History with `18 min` duration and `tray_return` reason.
- [ ] **12. Notifications**: Confirmed "Visit completed" notification appears in Notifications tab.
- [ ] **13. Timeout Safety Net**: Demonstrated that visits older than 25 minutes automatically transition to `expired` without hardware sensors.
