# Elite Run — Full Stack Website

A complete club website with Flask backend, SQLite database, and a single-page HTML/CSS/JS frontend.

---

## Project Structure

```
elite-run/
├── app.py                  ← Flask server + all API routes
├── database.db             ← SQLite database (auto-created on first run)
├── requirements.txt
├── templates/
│   └── index.html          ← Single-page frontend (all sections)
└── static/
    └── style.css           ← All styles
```

---

## Quick Start

### 1. Install Flask
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python app.py
```

### 3. Open your browser
```
http://localhost:5000
```

The database and sample data are created automatically on first run.

---

## API Reference

### Events
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/events` | All events |
| GET | `/api/events?upcoming=true` | Only future events |
| GET | `/api/events/<id>` | Single event |
| POST | `/api/events` | Create an event |
| DELETE | `/api/events/<id>` | Delete an event |

**POST /api/events body:**
```json
{
  "name": "City 10K Sprint",
  "date": "2025-08-01",
  "time": "06:00 AM",
  "location": "Kanpur, UP",
  "description": "Fast flat 10K loop.",
  "distance": "10 KM",
  "difficulty": "moderate",
  "spots": 50
}
```

### Applications
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/apply` | Submit member/intern application |
| GET | `/api/applications` | All applications (admin) |
| GET | `/api/applications?type=intern` | Filter by type |

### Products
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/products` | All products |
| GET | `/api/products?category=shoes` | Filter by category |
| POST | `/api/products` | Add a product |
| DELETE | `/api/products/<id>` | Delete a product |

**POST /api/products body:**
```json
{
  "name": "Nike Pegasus 41",
  "brand": "Nike",
  "affiliate_url": "https://nike.com/pegasus",
  "category": "shoes",
  "description": "Versatile daily trainer.",
  "price": 130
}
```
Categories: `shoes`, `gadgets`, `nutrition`, `apparel`

### Contact
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/contact` | Save a contact message |

---

## Adding Data

Use any API client (curl, Postman, Insomnia) or write a quick Python script:

```python
import requests

# Add a new event
requests.post("http://localhost:5000/api/events", json={
    "name": "Saturday Long Run",
    "date": "2025-08-10",
    "time": "06:30 AM",
    "location": "Lal Bagh, Lucknow",
    "distance": "18 KM",
    "difficulty": "hard",
    "spots": 30
})
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | HTML · CSS · Vanilla JS |
| Backend | Python · Flask |
| Database | SQLite (file-based, zero setup) |
| Fonts | Barlow Condensed + Barlow (Google Fonts) |
| Images | Unsplash (placeholder, swap with real photos) |
