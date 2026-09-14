# DineSpace 🍽️⚡
> **Smart Campus Dining & Virtual Seat Allocation System**  
> Real-time crowd monitoring, automated seat assignment, and hybrid IoT-free table turnaround tracking for university dining facilities.

---

## 🚀 Overview

**DineSpace** eliminates dining hall congestion during peak meal times without requiring expensive physical sensors or overhead cameras. By pairing digital QR/NFC entrance check-ins with an intelligent dual-path seat release mechanism (tray-return QR scanner + automated background timeout sweeper), students can check live crowd levels, reserve seats dynamically, and view campus meal menus in real time.

```
┌────────────────────────┐         Polls Live Status (3s)         ┌─────────────────────────┐
│ Student Phone / Kiosk  │ ─────────────────────────────────────► │  FastAPI Backend Server │
│ Tailwind CSS + HTML/JS │ ◄───────────────────────────────────── │  Python 3.13 + Pydantic │
└────────────────────────┘                                        └───────────┬─────────────┘
                                                                              │
                                                                   PyMongo    │ Connection
                                                                              ▼
                                                                  ┌─────────────────────────┐
                                                                  │ Local MongoDB Database  │
                                                                  │ (students, menu, seats) │
                                                                  └─────────────────────────┘
```

---

## ✨ Features

- **Real-Time Crowd Gauge**: Live campus dining occupancy rate (%) with dynamic crowd level status (*Low*, *Moderate*, *Peak Rush*).
- **Interactive Virtual Seat Map**: Visual 10x10 seating matrix categorized into 4 zones (*Window Booths*, *Community Tables*, *Quiet Study*, *Express Dining*) with seat availability filtering and assigned seat tracking.
- **Automated Seat Allocation**: Kiosk entry scan verifies student dining passes and assigns the lowest available seat in milliseconds.
- **Hybrid Seat Release Engine**:
  - *Path A (Instant)*: Tray Return QR scan frees the virtual seat immediately upon dish return.
  - *Path B (Safety Net)*: 25-minute background timeout worker automatically frees abandoned seats.
- **Daily Dining Menu**: Filterable meal menu (*Breakfast*, *Lunch*, *Snacks*, *Dinner*) with dietary indicators (*Veg*, *Non-Veg*, *Chef Specials*), calories, protein, and allergen warnings.
- **Visit History & Auditing**: Searchable and paginated dining history logs with duration metrics and pass types.
- **Broadcast Notifications**: Category-filtered updates (*Crowd Alerts*, *Menu Updates*, *Pass Confirmations*).
- **Profile & Settings**: Security management, bcrypt password updates, and notification preference controls.

---

## 🔑 Demo Credentials

The database is pre-seeded with active student credentials for instant testing:

| Role / Name | Student ID | Password | Status |
| :--- | :--- | :--- | :--- |
| **Kunal Kumar Singh** | `P132-NNK` | `DineSpace2026!` | Active |
| **Sarah Chen** | `STU1042` | `DineSpace2026!` | Active |
| **Alex Sharma** | `STU1043` | `DineSpace2026!` | Active |
| **Rahul Singh** | `STU1044` | `DineSpace2026!` | Active |

> **Quick Demo**: On [`login.html`](frontend/login.html), click the **"Quick Demo Login"** button to auto-fill credentials with one click.

---

## 📱 Application Screens (All 12 Pages)

| Page | File | Description |
| :--- | :--- | :--- |
| **1. Login Portal** | [`frontend/login.html`](frontend/login.html) | Secure student authentication with demo autofill. |
| **2. Home Dashboard** | [`frontend/home.html`](frontend/home.html) | Live occupancy gauge, crowd metrics, and active meal pass banner. |
| **3. Entry Scanner** | [`frontend/entry_scan.html`](frontend/entry_scan.html) | Kiosk pass scanner with live laser animation. |
| **4. Entry Verified** | [`frontend/entry_success.html`](frontend/entry_success.html) | Dynamic seat allocation confirmation card. |
| **5. My Active Visit** | [`frontend/my_visit.html`](frontend/my_visit.html) | Live meal session timer and tray return prompt. |
| **6. Tray Return** | [`frontend/tray_return.html`](frontend/tray_return.html) | Exit station scanner to release seats. |
| **7. Visit Completed** | [`frontend/visit_completed.html`](frontend/visit_completed.html) | Dining summary with elapsed minutes. |
| **8. Visit History** | [`frontend/visit_history.html`](frontend/visit_history.html) | Paginated audit log of previous visits. |
| **9. Notifications** | [`frontend/notifications.html`](frontend/notifications.html) | Filterable alert feed and campus mess broadcasts. |
| **10. Find a Seat** | [`frontend/seats.html`](frontend/seats.html) | 4-zone virtual seat layout and availability matrix. |
| **11. Today's Menu** | [`frontend/menu.html`](frontend/menu.html) | Breakfast/Lunch/Snacks/Dinner tabs with nutrition badges. |
| **12. Settings & Profile** | [`frontend/settings.html`](frontend/settings.html) | Dietary preferences, notification toggles, and password change. |

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Tailwind CSS (via CDN), Google Fonts (*Plus Jakarta Sans*, *Playfair Display*).
- **Backend**: Python 3.13, FastAPI, Pydantic v2, Starlette.
- **Database**: MongoDB 8.3 (local service on `mongodb://localhost:27017` / PyMongo).
- **Testing & Verification**: Pytest (175 automated test cases), Playwright (headless browser cross-page navigation).

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- MongoDB Community Server (running on port `27017`)

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Activate Python virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies (if setting up fresh)
pip install -r requirements.txt

# Seed sample data into local MongoDB
python -m scripts.seed_students
python -m scripts.seed_menu
python -m scripts.seed_notifications

# Launch FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
Open [`frontend/index.html`](frontend/index.html) or [`frontend/login.html`](frontend/login.html) directly in any modern web browser. The frontend automatically hooks to `http://127.0.0.1:8000/api` or provides seamless standalone simulation if offline.

---

## 🧪 Testing & Quality Assurance

```bash
# Run full automated test suite (175 tests)
python -m pytest

# Run pre-demo smoke test across all 12 API flows
python smoke_test.py

# Verify frontend links and end-to-end user flows
python scripts/test_user_flows.py
```

---

## 📄 License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.