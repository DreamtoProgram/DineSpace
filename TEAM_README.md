# DineSpace — Hackathon Team Playbook 🍽️⚡
> **Read time:** 3–5 minutes. Written for everyone on the team (no deep backend/database knowledge required).

---

## 1. What is DineSpace? (In 3 Sentences)
**DineSpace** is a lightweight, responsive web app that solves campus dining hall chaos during peak rush hours. Instead of wandering around with a heavy tray looking for an empty table, students can check their phones in real time to see current crowd levels (Low / Medium / High), available seat counts, and today’s meal menu. 

We track seats **digitally without expensive hardware sensors** by combining entry QR check-ins with an intelligent auto-timeout and tray-return exit system.

---

## 2. Who Does What? (The 30-Second Tech Breakdown)

Our stack was chosen deliberately so we have **zero build friction** and can ship a complete demo in under 24 hours:

```
[Student Phone / Browser]  <--- Polls every 3s --->  [FastAPI Backend]  <--->  [MongoDB]
   Tailwind CSS + Alpine.js                            Python API Server          3 Simple Collections
   (No npm, no build step)                             + Background Sweeper      (students, occupancy, menu)
```

| Layer | Technology | What it does in our project |
| :--- | :--- | :--- |
| **Frontend** | **Tailwind CSS + Alpine.js (via CDN)** | The live mobile-friendly dashboard students see. Loaded directly in the browser via simple `<script>` tags (no `npm install`, no Webpack/Vite build steps). It asks the backend for fresh numbers every 3–5 seconds and updates the screen instantly. |
| **Backend** | **Python (FastAPI)** | The brain. Validates student QR scans, assigns open virtual seat numbers, serves the API endpoints (`/status`, `/scan/entry`, `/scan/exit`), and runs a 60-second background task to clean up abandoned seats. |
| **Database** | **MongoDB** | Stores student records, active seat occupancy, and the daily menu. Easy to inspect and query with JSON-like documents. |

---

## 3. A Student's Visit: Step-by-Step Flow

Here is exactly what happens during a student's lunch visit:

1. **Before leaving the dorm:**  
   The student opens `dinespace.campus.edu` on their phone. They see:
   - Crowd status badge: **"LOW CROWD — 42 Seats Available"**
   - Today's lunch menu: *Paneer Butter Masala, Dal Makhani, Rice, Roti*.
2. **At the Mess Entrance:**  
   The student scans their student pass / QR code at the entrance scanner (or their phone camera scans the entrance QR).
3. **Backend assigns a seat:**  
   - FastAPI checks the pass against the `students` database.
   - If valid, the backend grabs the next open virtual seat slot (e.g., Seat #24 out of 100 total capacity).
   - A new document is saved in `occupancy` with `status: "occupied"` and the current `entryTime`.
   - The entrance screen shows: *"Welcome, Alex! Seat #24 reserved."*
4. **Live website updates:**  
   Within 3 seconds, all other students' screens see available seats drop from 42 to 41.
5. **Student finishes & leaves:**  
   The seat is released back to the open pool via our seat-freeing system (see Section 4).

---

## 4. The "Seat-Freeing" Problem & Our Hybrid Solution

### Why is this the hardest problem?
We do **not** have physical weight sensors or overhead cameras at every chair (impossible to build in 24 hours). If students check in at the door, how do we know when they actually get up and leave? If we never free seats, the mess will permanently show "100% Full" after 45 minutes!

### Our 2-Layer Hybrid Solution:
We combine **human habit** with an **automated safety net**:

```
[Student Finished Eating]
       │
       ├─► Path A: Student scans QR at Tray Return Point ────► Immediately Frees Seat! (Accuracy Layer)
       │
       └─► Path B: Student forgets and just walks out ────────► 25–30 Min Auto-Timeout! (Safety Net)
                                                                 (Background worker checks every 60s)
```

1. **The Accuracy Layer (Tray-Return QR Scan):**  
   Near the tray drop-off / dish-return station, there is a QR code: *"Scan to Return Tray"*. When scanned, it instantly marks that student's seat as `"available"` and records `exitTime`. Students who want to help keep the tracker accurate do this on their way out.
2. **The Safety Net (Auto-Timeout Sweeper):**  
   Most students will forget to scan when leaving, and that’s okay! A lightweight background loop inside FastAPI runs **every 60 seconds**. It checks:
   > *"Is any seat still marked 'occupied' whose `entryTime` was more than 25 minutes ago?"*  
   If yes, the system automatically marks it `"available"`.
   
**Why judges will love this:** It's realistic, fault-tolerant, and requires zero physical IoT hardware to work effectively.

---

## 5. Our 3 Database Collections (Cheat Sheet)

You don't need to know MongoDB commands—just understand what data lives where:

### 1. `students` (Who is allowed in)
*Seeded once from university CSV export:*
```json
{
  "studentId": "STU1042",
  "name": "Sarah Chen",
  "passCode": "PASS-8842"
}
```

### 2. `occupancy` (Who is sitting where right now)
*Updated live on entry/exit/timeout:*
```json
{
  "seatNumber": 24,
  "entryTime": "2026-09-11T12:30:00Z",
  "exitTime": null,
  "status": "occupied", 
  "mealType": "Lunch"
}
```

### 3. `menu` (What's cooking today)
*Static/seeded so students have a reason to open the website:*
```json
{
  "date": "2026-09-11",
  "mealType": "Lunch",
  "items": ["Paneer Butter Masala", "Dal Tadka", "Steamed Rice", "Roti", "Gulab Jamun"]
}
```

> **University Integration Note:** Real university ERPs don't give API keys to hackathon students. We simulate the university database with `students.csv` + a 10-line Python import script (`import_students.py`). The code is written so swapping this for a real REST API later takes only one function change!

---

## 6. How the Live UI Works (No Complicated Setup!)

The frontend does not use React, Node, or webpack. It is a clean HTML file powered by:
- **Tailwind CSS (CDN):** For instant, modern styling.
- **Alpine.js (CDN):** For live reactivity in simple HTML attributes:
  ```html
  <div x-data="crowdTracker()" x-init="startPolling()">
    <span x-text="availableSeats"></span> Seats Available
    <span class="badge" x-text="crowdLevel"></span> <!-- Low / Med / High -->
  </div>
  ```
- **Polling Loop:** Alpine calls `GET /api/status` every 3 seconds. The backend responds with:
  ```json
  {
    "totalSeats": 100,
    "occupiedSeats": 58,
    "availableSeats": 42,
    "crowdLevel": "Medium",
    "mealType": "Lunch"
  }
  ```
  Alpine automatically updates the progress bar and badges without reloading the page!

---

## 7. 24-Hour Work Division (Who Owns What)

To avoid stepping on each other's toes, we split into 3 clear roles:

### 👤 Role 1: Backend & Core Engine (FastAPI)
- [ ] Set up FastAPI project + MongoDB connection (`pymongo` or `motor`).
- [ ] Build `GET /api/status` (returns seat totals, available count, crowd level).
- [ ] Build `POST /api/scan/entry` (checks student pass, assigns lowest available seat number, sets status to `occupied`).
- [ ] Build `POST /api/scan/exit` (marks seat as `available`).
- [ ] Implement the background cleanup task (runs every 60s to auto-expire seats > 25 mins).

### 🎨 Role 2: Frontend & Live Dashboard (Tailwind + Alpine.js)
- [ ] Build `index.html` with responsive mobile-first UI.
- [ ] Prominent Crowd-o-Meter card: Big percentage ring or bar + color-coded badge:
  - **Green / "Low Crowd"** (< 50% full)
  - **Yellow / "Moderate"** (50%–80% full)
  - **Red / "Peak Rush"** (> 80% full)
- [ ] Available seat counter card (e.g. `42 / 100 Seats Free`).
- [ ] "Today's Menu" tab/card showing Lunch/Dinner specials.
- [ ] Connect Alpine.js `setInterval` to fetch `/api/status` every 3 seconds.

### 📱 Role 3: Scanner Simulator & Data Seeder
- [ ] Prepare `students.csv` (sample names, IDs, pass codes).
- [ ] Write `import_students.py` to seed MongoDB on startup.
- [ ] Create a simple test/demo page (`scanner.html`):
  - A mock "Entry Scanner" button (select student or enter ID → hit Enter → see seat assigned).
  - A mock "Tray Return Scanner" button (enter seat or student ID → free seat).
  - *(Optional stretch: HTML5 camera QR reader using `html5-qrcode` library)*.

---

## 8. 24-Hour Scope Guardrails (What's IN vs. What's OUT)

| ✅ What's IN (Must Demo for Judges) | ❌ What's OUT (Do Not Attempt!) |
| :--- | :--- |
| Capacity-based virtual seat count (e.g., 100 seats) | Physical IoT chair sensors or pressure mats |
| Simulated student pass import via CSV | Live university LDAP / SSO OAuth integration |
| 3-second live polling with Alpine.js | Complex WebSockets or Redis pub/sub |
| Tray-return scan + 25-minute auto-expiry logic | AI camera crowd-density computer vision |
| Responsive mobile view (students check from phone) | Native iOS / Android apps |

---

## 9. Quick Demo Script for Pitch Time 🎤
1. **Show empty mess:** Dashboard shows `100 / 100 Seats Available` (Green - Low Crowd).
2. **Simulate entry rush:** Click "Simulate 60 Students Entering" (or scan 2–3 passes). Dashboard dynamically flips to `40 Available` (Yellow - Moderate).
3. **Show accuracy exit:** Scan a tray-return QR code → seat immediately bumps up by 1.
4. **Show auto-timeout safety net:** Fast-forward or trigger the 25-min timeout worker → abandoned seats automatically release.
5. **Pitch punchline:** *"Zero hardware cost, 100% real-time clarity for students, deployed with zero friction."*

---
## 10. System Architecture Diagram

![DineSpace System Architecture](architecture_diagram.png)

*Vector source: [architecture_diagram.svg](architecture_diagram.svg) | High-res image: [architecture_diagram.png](architecture_diagram.png)*

