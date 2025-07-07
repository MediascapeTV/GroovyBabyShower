from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

db_path = Path("rsvps.db")

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rsvps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            attending TEXT,
            guests_count INTEGER,
            dietary_notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def rsvp_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/rsvp")
def submit_rsvp(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    attending: str = Form(...),
    guests_count: int = Form(...),
    dietary_notes: str = Form("")
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rsvps (name, email, attending, guests_count, dietary_notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, attending, guests_count, dietary_notes))
    conn.commit()
    conn.close()
    return templates.TemplateResponse("thank_you.html", {"request": request})

@app.get("/responses", response_class=HTMLResponse)
def view_responses(request: Request):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rsvps")
    rows = cursor.fetchall()
    conn.close()

    rsvps = [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "attending": row[3],
            "guests_count": row[4],
            "dietary_notes": row[5]
        }
        for row in rows
    ]
    return templates.TemplateResponse("responses.html", {"request": request, "rsvps": rsvps})

@app.get("/export")
def export_csv():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM rsvps", conn)
    conn.close()
    csv_path = "rsvps_export.csv"
    df.to_csv(csv_path, index=False)
    return {"message": f"CSV exported to {csv_path}"}
