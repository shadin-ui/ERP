# Coworking ERP System

This repository provides a lightweight ERP backend for a coworking space with member management, space inventory, bookings, invoicing, and payments.

## Features
- Members: create, list, and fetch member profiles.
- Spaces: manage rooms/desks with capacity and pricing.
- Bookings: reserve spaces with availability checks.
- Invoices: issue invoices tied to bookings or ad-hoc charges.
- Payments: record payments and close invoices.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at `http://localhost:8000/docs`.

## Example Requests

```bash
curl -X POST http://localhost:8000/members \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alex Chen","email":"alex@example.com","company":"Studio"}'

curl -X POST http://localhost:8000/spaces \
  -H 'Content-Type: application/json' \
  -d '{"name":"Focus Room","space_type":"meeting","capacity":4,"hourly_rate":35}'
```

## Data Model

| Table | Purpose |
| --- | --- |
| members | Customer profiles |
| spaces | Inventory of rooms/desks |
| bookings | Scheduled reservations |
| invoices | Billing records |
| payments | Payments applied to invoices |

## Next Steps
- Add authentication and role-based access (admin vs. member).
- Integrate recurring membership billing.
- Export reports for occupancy and revenue.
