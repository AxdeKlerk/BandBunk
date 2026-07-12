# BandBunk — Handover Notes for Simon

> Sleep After The Gig. AirBnB for UK rock & metal artists.

---

## Quick Start (local dev)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit: http://127.0.0.1:8000  
Admin: http://127.0.0.1:8000/admin

---

## What's built

| App | What it does |
|-----|-------------|
| `accounts` | Custom user model, artist vs host roles, social links, profile pages |
| `listings` | Create/browse/edit bunk listings, map view (Leaflet + OpenStreetMap) |
| `bookings` | Full booking flow — request, confirm/decline, mark complete, Stripe hooks ready |
| `reviews` | Two-way star ratings (artist → host, host → artist) after stay completes |
| `core` | Homepage, how it works, about, contact, terms, privacy, safety |

---

## Tech Stack

- Django 4.2 / Python 3.12+
- SQLite for dev → swap to PostgreSQL for production
- Stripe (keys via env vars — app runs without real keys in dev)
- Leaflet.js + OpenStreetMap for maps
- Whitenoise for static files in production

---

## Environment Variables (production)

```
SECRET_KEY=your-strong-secret-key
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Deploy (recommended: Railway or Render)

1. Set `DEBUG = False` in settings.py
2. Set all env vars above
3. Switch database to PostgreSQL
4. Set `ALLOWED_HOSTS = ['bandbunk.co.uk', 'www.bandbunk.co.uk']`
5. Run `python manage.py collectstatic`
6. Switch email backend to SMTP (SendGrid recommended)

---

## Things not yet wired up

- **Geocoding**: Map only shows listings with lat/lng set. README has the `geopy` snippet to auto-geocode on listing create.
- **Email**: Set to console backend for dev. Swap to SMTP for production.

## Stripe (now wired)

Stripe Checkout is live for artist → platform payment on confirmed bookings.

- Artist sees a "Pay Now" button on a confirmed booking → creates a Checkout Session (`bookings/pay/<pk>/`) → redirected to Stripe → back to `bookings/payment/success/`.
- Payment state is also confirmed server-side via webhook (`bookings/webhook/stripe/`), so it's not dependent on the browser making it back to the success page.
- `.env.example` has the three keys needed: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.
- For local testing, use the Stripe CLI: `stripe listen --forward-to localhost:8000/bookings/webhook/stripe/` — it prints a webhook signing secret to put in `.env`.
- This is a direct "artist pays platform" flow, not a split payout. If hosts need to be paid out automatically later, that's Stripe Connect (separate, bigger piece of work) — not needed for MVP.
- `.env` now holds `SECRET_KEY` and the Stripe keys — copy `.env.example` to `.env` and fill in real values (get test keys from your Stripe dashboard). DEBUG auto-detects based on hostname, no more manual toggling.

---

## Design System

Black `#000000` / Purple `#9b1dfa` / Off-white `#f5f5f5`  
Fonts: Bebas Neue (display) + Barlow (body)  
All in `static/css/main.css`

---

🤘 Keep the scene on the road.
