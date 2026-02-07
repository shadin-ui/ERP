import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "erp.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_cursor():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    finally:
        connection.close()


def init_db():
    with db_cursor() as cursor:
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                company TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS spaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                space_type TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                hourly_rate REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                space_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(member_id) REFERENCES members(id),
                FOREIGN KEY(space_id) REFERENCES spaces(id)
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                booking_id INTEGER,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                due_date TEXT NOT NULL,
                FOREIGN KEY(member_id) REFERENCES members(id),
                FOREIGN KEY(booking_id) REFERENCES bookings(id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                paid_at TEXT NOT NULL,
                method TEXT NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            );
            """
        )
