from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from app.db import db_cursor, init_db
from app.schemas import (
    Booking,
    BookingCreate,
    Invoice,
    InvoiceCreate,
    Member,
    MemberCreate,
    Payment,
    PaymentCreate,
    Space,
    SpaceCreate,
)

app = FastAPI(title="Coworking ERP")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/members", response_model=Member)
def create_member(member: MemberCreate):
    with db_cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO members (name, email, phone, company, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    member.name,
                    member.email,
                    member.phone,
                    member.company,
                    utc_now(),
                ),
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Email already exists") from exc
        member_id = cursor.lastrowid
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
    return Member(**dict(row))


@app.get("/members", response_model=list[Member])
def list_members():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM members ORDER BY created_at DESC")
        rows = cursor.fetchall()
    return [Member(**dict(row)) for row in rows]


@app.get("/members/{member_id}", response_model=Member)
def get_member(member_id: int):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Member not found")
    return Member(**dict(row))


@app.post("/spaces", response_model=Space)
def create_space(space: SpaceCreate):
    with db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO spaces (name, space_type, capacity, hourly_rate, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                space.name,
                space.space_type,
                space.capacity,
                space.hourly_rate,
                1 if space.active else 0,
            ),
        )
        space_id = cursor.lastrowid
        cursor.execute("SELECT * FROM spaces WHERE id = ?", (space_id,))
        row = cursor.fetchone()
    return Space(**dict(row))


@app.get("/spaces", response_model=list[Space])
def list_spaces():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM spaces ORDER BY name")
        rows = cursor.fetchall()
    return [Space(**dict(row)) for row in rows]


@app.post("/bookings", response_model=Booking)
def create_booking(booking: BookingCreate):
    if booking.end_time <= booking.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    with db_cursor() as cursor:
        cursor.execute("SELECT id FROM members WHERE id = ?", (booking.member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Member not found")

        cursor.execute("SELECT id FROM spaces WHERE id = ? AND active = 1", (booking.space_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Space not available")

        cursor.execute(
            """
            SELECT 1 FROM bookings
            WHERE space_id = ?
              AND status = 'confirmed'
              AND NOT (end_time <= ? OR start_time >= ?)
            """,
            (
                booking.space_id,
                booking.start_time.isoformat(),
                booking.end_time.isoformat(),
            ),
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Space is already booked")

        cursor.execute(
            """
            INSERT INTO bookings (member_id, space_id, start_time, end_time, status)
            VALUES (?, ?, ?, ?, 'confirmed')
            """,
            (
                booking.member_id,
                booking.space_id,
                booking.start_time.isoformat(),
                booking.end_time.isoformat(),
            ),
        )
        booking_id = cursor.lastrowid
        cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
    return Booking(**dict(row))


@app.get("/bookings", response_model=list[Booking])
def list_bookings():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM bookings ORDER BY start_time DESC")
        rows = cursor.fetchall()
    return [Booking(**dict(row)) for row in rows]


@app.post("/invoices", response_model=Invoice)
def create_invoice(invoice: InvoiceCreate):
    with db_cursor() as cursor:
        cursor.execute("SELECT id FROM members WHERE id = ?", (invoice.member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Member not found")

        if invoice.booking_id is not None:
            cursor.execute("SELECT id FROM bookings WHERE id = ?", (invoice.booking_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Booking not found")

        cursor.execute(
            """
            INSERT INTO invoices (member_id, booking_id, amount, status, issued_at, due_date)
            VALUES (?, ?, ?, 'issued', ?, ?)
            """,
            (
                invoice.member_id,
                invoice.booking_id,
                invoice.amount,
                utc_now(),
                invoice.due_date.isoformat(),
            ),
        )
        invoice_id = cursor.lastrowid
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
    return Invoice(**dict(row))


@app.get("/invoices", response_model=list[Invoice])
def list_invoices():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM invoices ORDER BY issued_at DESC")
        rows = cursor.fetchall()
    return [Invoice(**dict(row)) for row in rows]


@app.post("/payments", response_model=Payment)
def create_payment(payment: PaymentCreate):
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (payment.invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        cursor.execute(
            """
            INSERT INTO payments (invoice_id, amount, paid_at, method)
            VALUES (?, ?, ?, ?)
            """,
            (
                payment.invoice_id,
                payment.amount,
                utc_now(),
                payment.method,
            ),
        )
        cursor.execute(
            """
            UPDATE invoices
            SET status = 'paid'
            WHERE id = ?
            """,
            (payment.invoice_id,),
        )
        payment_id = cursor.lastrowid
        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
    return Payment(**dict(row))


@app.get("/payments", response_model=list[Payment])
def list_payments():
    with db_cursor() as cursor:
        cursor.execute("SELECT * FROM payments ORDER BY paid_at DESC")
        rows = cursor.fetchall()
    return [Payment(**dict(row)) for row in rows]
