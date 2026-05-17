"""
Elite Run — Flask Backend
=========================
Run with:  python app.py
Visit:     http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB_PATH = "database.db"


# ─────────────────────────────────────────
#  Database helpers
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Events — includes difficulty, distance, time, spots
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            date        TEXT NOT NULL,
            time        TEXT,
            location    TEXT NOT NULL,
            description TEXT,
            distance    TEXT,
            difficulty  TEXT DEFAULT 'moderate',
            spots       INTEGER,
            image_url   TEXT
        )
    """)

    # Applications — join / intern requests from the website
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            email        TEXT NOT NULL,
            type         TEXT NOT NULL CHECK(type IN ('member','intern')),
            message      TEXT,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Products — affiliate gear links
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            brand         TEXT,
            affiliate_url TEXT NOT NULL,
            category      TEXT,
            description   TEXT,
            price         REAL,
            image_url     TEXT
        )
    """)

    # Contact messages
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            email        TEXT NOT NULL,
            message      TEXT NOT NULL,
            received_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables ready.")


def seed_db():
    """Adds realistic sample data if tables are empty."""
    conn = get_db()
    c = conn.cursor()

    if c.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
        events = [
            ("Sunrise Coastal 10K",    "2026-07-18", "06:00 AM", "Marine Drive Promenade, Mumbai",
             "Catch the first light over the bay with a flat, fast 10K loop. Pacers available for every group.",
             "10 KM", "moderate", 40, ""),
            ("Park Tempo Tuesdays",    "2026-07-21", "06:30 PM", "Greenfield Park, North Gate",
             "Weekly community 5K. Beginner-friendly. Stick around for stretch + coffee.",
             "5 KM", "easy", 88, ""),
            ("Hill Crusher Half",      "2026-08-08", "06:30 AM", "Ridgeview Trailhead",
             "A challenging half-marathon through three signature climbs. Hydration every 3K.",
             "21.1 KM", "hard", 17, ""),
            ("Night Stride Neon 8K",   "2026-08-15", "08:00 PM", "Central Boulevard Loop",
             "Glow-in-the-dark community run. Free LED bands for first 100 runners.",
             "8 KM", "moderate", 33, ""),
            ("Dawn Half Marathon",     "2026-09-03", "06:00 AM", "Lucknow Heritage Route",
             "An early morning 21 km run through the city's heritage routes. Medals for all finishers.",
             "21.1 KM", "hard", 60, ""),
            ("Elite Endurance Camp",   "2026-09-20", "07:00 AM", "Jim Corbett, Uttarakhand",
             "A two-day residential training camp. Coaching, nutrition sessions, and trail runs included.",
             "Variable", "hard", 25, ""),
        ]
        c.executemany(
            "INSERT INTO events (name,date,time,location,description,distance,difficulty,spots,image_url) VALUES (?,?,?,?,?,?,?,?,?)",
            events
        )
        print("[DB] Sample events added.")

    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Pro Race Carbon Trainer",   "Nike",   "https://www.nike.com",    "shoes",
             "Carbon-plated speed shoe for race day PRs.",                               249, ""),
            ("Daily Cushion Trainer",     "Hoka",   "https://www.hoka.com",    "shoes",
             "Plush daily mileage workhorse with broad base.",                           149, ""),
            ("Multisport GPS Watch",      "Garmin", "https://www.garmin.com",  "gadgets",
             "Pace, HR, VO2 max and recovery in one wrist tool.",                        429, ""),
            ("Chest Heart Rate Strap",    "Polar",  "https://www.polar.com",   "gadgets",
             "Lab-grade HR accuracy for serious training zones.",                          89, ""),
            ("Hydration Running Vest",    "Salomon","https://www.salomon.com", "nutrition",
             "2L bladder + 4 front pockets. Bounce-free fit for long runs.",             119, ""),
            ("Electrolyte Gel Pack x10",  "Maurten","https://www.maurten.com", "nutrition",
             "Hydrogel energy gel — easy on the stomach, used by elite marathoners.",     48, ""),
            ("Lightweight Run Shorts",    "Decathlon","https://www.decathlon.in","apparel",
             "Featherweight, breathable 2-in-1 shorts. Best budget pick.",                24, ""),
            ("Compression Run Tights",    "2XU",    "https://www.2xu.com",     "apparel",
             "Targeted compression for quads and calves. Reduces fatigue on long efforts.",89, ""),
        ]
        c.executemany(
            "INSERT INTO products (name,brand,affiliate_url,category,description,price,image_url) VALUES (?,?,?,?,?,?,?)",
            products
        )
        print("[DB] Sample products added.")

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
#  Page routes
# ─────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


# ─────────────────────────────────────────
#  API — Events
# ─────────────────────────────────────────

@app.route("/api/events", methods=["GET"])
def get_events():
    upcoming_only = request.args.get("upcoming", "false").lower() == "true"
    conn = get_db()
    if upcoming_only:
        today = datetime.today().strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT * FROM events WHERE date >= ? ORDER BY date", (today,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM events ORDER BY date").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/events/<int:eid>", methods=["GET"])
def get_event(eid):
    conn = get_db()
    row = conn.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
    conn.close()
    if not row:
        abort(404, "Event not found.")
    return jsonify(dict(row))


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.get_json()
    missing = [f for f in ("name","date","location") if not data.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing: {', '.join(missing)}"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO events (name,date,time,location,description,distance,difficulty,spots,image_url) VALUES (?,?,?,?,?,?,?,?,?)",
        (data["name"], data["date"], data.get("time",""), data["location"],
         data.get("description",""), data.get("distance",""),
         data.get("difficulty","moderate"), data.get("spots"), data.get("image_url",""))
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Event created."}), 201


@app.route("/api/events/<int:eid>", methods=["DELETE"])
def delete_event(eid):
    conn = get_db()
    conn.execute("DELETE FROM events WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ─────────────────────────────────────────
#  API — Applications
# ─────────────────────────────────────────

@app.route("/api/apply", methods=["POST"])
def submit_application():
    data = request.get_json()
    missing = [f for f in ("name","email","type") if not data.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing: {', '.join(missing)}"}), 400
    if data["type"] not in ("member","intern"):
        return jsonify({"success": False, "error": "type must be 'member' or 'intern'"}), 400
    if "@" not in data.get("email",""):
        return jsonify({"success": False, "error": "Invalid email address."}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO applications (name,email,type,message) VALUES (?,?,?,?)",
        (data["name"], data["email"], data["type"], data.get("message",""))
    )
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": f"Thanks {data['name']}! Your application is received. We'll be in touch soon."
    }), 201


@app.route("/api/applications", methods=["GET"])
def get_applications():
    filter_type = request.args.get("type")
    conn = get_db()
    if filter_type in ("member","intern"):
        rows = conn.execute(
            "SELECT * FROM applications WHERE type=? ORDER BY submitted_at DESC", (filter_type,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM applications ORDER BY submitted_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ─────────────────────────────────────────
#  API — Products
# ─────────────────────────────────────────

@app.route("/api/products", methods=["GET"])
def get_products():
    cat = request.args.get("category")
    conn = get_db()
    if cat:
        rows = conn.execute("SELECT * FROM products WHERE category=?", (cat,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()
    missing = [f for f in ("name","affiliate_url") if not data.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing: {', '.join(missing)}"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO products (name,brand,affiliate_url,category,description,price,image_url) VALUES (?,?,?,?,?,?,?)",
        (data["name"], data.get("brand",""), data["affiliate_url"],
         data.get("category",""), data.get("description",""),
         data.get("price"), data.get("image_url",""))
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Product added."}), 201


@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ─────────────────────────────────────────
#  API — Contact Messages
# ─────────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    missing = [f for f in ("name","email","message") if not data.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing: {', '.join(missing)}"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (name,email,message) VALUES (?,?,?)",
        (data["name"], data["email"], data["message"])
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Message received! We'll be in touch."}), 201


# ─────────────────────────────────────────
#  Error handlers
# ─────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e)}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e)}), 400


# ─────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    seed_db()
    print("\n✔  Elite Run running at http://localhost:5000\n")
    app.run(debug=True)
