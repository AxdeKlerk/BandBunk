# 🎸 BandBunk

> **Sleep After The Gig.**  
> AirBnB for emerging UK rock and metal artists. Fans host. Bands sleep. £10 a night.

---

## What is BandBunk?

BandBunk connects touring UK rock and metal artists with fans who have a spare sofa, room, or floor. A band plays a gig away from home, needs somewhere to crash, and a local fan opens their door for £10 a night — which gets the band a safe bed, a mug of tea, and a slice of toast as a minimum.

Both sides leave honest reviews. The community polices itself.

---

## Tech Stack

- **Backend:** Django 4.2 (Python 3.12+)
- **Database:** SQLite (dev) — swap to PostgreSQL for production
- **Payments:** Stripe
- **Maps:** Leaflet.js + OpenStreetMap/CartoDB Dark tiles
- **Frontend:** Vanilla HTML, CSS (custom design system), Vanilla JS
- **Email:** Django console backend (dev) / any SMTP in production

---

## Local Setup

### 1. Clone & create a virtual environment

```bash
git clone https://github.com/yourname/bandbunk.git
cd bandbunk
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (admin access)

```bash
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**  
Admin: **http://127.0.0.1:8000/admin**

---

## Environment Variables

For production, set these as environment variables (never commit secrets):

| Variable | Description |
|----------|-------------|
| `STRIPE_PUBLIC_KEY` | Stripe publishable key |
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `SECRET_KEY` | Django secret key — change before deploying |

For local dev, the app runs without real Stripe keys — payment UI is present but transactions won't process.

---

## App Structure

```
bandbunk/
├── bandbunk/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/           # Custom user model, auth, profiles
│   ├── listings/           # Listing CRUD, browse, map
│   ├── bookings/           # Booking flow, host responses, Stripe
│   ├── reviews/            # Two-way review system
│   └── core/               # Homepage, static pages
├── static/
│   ├── css/main.css        # Full design system
│   └── js/main.js          # Nav, map init, UI helpers
├── templates/              # All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── listings/
│   ├── bookings/
│   ├── reviews/
│   └── core/
├── media/                  # User uploads (auto-created)
├── manage.py
└── requirements.txt
```

---

## Key Features

### For Artists
- Register with social proof (Facebook, Instagram, YouTube, Bandcamp, Spotify)
- Browse listings by town/city, listing type, max price
- Map view of all available bunks
- Multi-night booking requests with gig verification
- Real-time price calculator in booking form
- Two-way review system

### For Hosts / Fans
- Post sofas, spare rooms, floor space, or garages
- £10 minimum price per night
- Receive email notifications for booking requests
- Verify artist gig via their supplied event link
- Confirm or decline with optional message
- Mark stays complete → trigger review flow

### Reviews
- Star rating (1–5) overall
- Category ratings: cleanliness, noise/respect, hospitality
- Written review body
- Public and permanent
- Both artist → host and host → artist

### Admin Dashboard
- Full Django admin at `/admin/`
- Verify artist accounts
- Manage listings, bookings, reviews
- Bulk actions: verify artists, mark bookings complete/cancelled

---

## Design System

Defined in `static/css/main.css`:

| Token | Value |
|-------|-------|
| `--black` | `#000000` |
| `--purple` | `#9b1dfa` |
| `--purple-bright` | `#b44dff` |
| `--white` | `#f5f5f5` |
| `--font-display` | Bebas Neue |
| `--font-body` | Barlow |

---

## Adding Stripe (Payments)

1. Create a [Stripe account](https://stripe.com)
2. Add your keys to environment variables
3. In `apps/bookings/views.py`, implement `stripe.PaymentIntent.create()` in `host_respond_view` after confirmation
4. Add a Stripe webhook endpoint to handle `payment_intent.succeeded`

The `Booking` model already has `stripe_payment_intent_id`, `stripe_charge_id`, and `payment_status` fields ready.

---

## Adding Coordinates to Listings (for Map)

The map view only shows listings that have `latitude` and `longitude` set. To enable geocoding:

1. Install `geopy`: `pip install geopy`
2. In `create_listing_view`, after saving the listing, geocode the postcode using `Nominatim`
3. Store the result in `listing.latitude` / `listing.longitude`

Example:
```python
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="bandbunk")
location = geolocator.geocode(listing.postcode + ", UK")
if location:
    listing.latitude  = location.latitude
    listing.longitude = location.longitude
    listing.save()
```

---

## Deploying to Production

1. Set `DEBUG = False` in settings
2. Set a strong `SECRET_KEY`
3. Switch to PostgreSQL database
4. Set `ALLOWED_HOSTS` to your domain
5. Run `python manage.py collectstatic`
6. Switch email backend to SMTP (SendGrid, Mailgun, etc.)
7. Add `whitenoise` middleware for static files (already in requirements)
8. Set up Stripe webhook

Recommended: [Railway](https://railway.app), [Render](https://render.com), or a basic VPS.

---

## Keep The Scene On The Road. 🤘
