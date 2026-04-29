# Bakery Tracker PWA — Deployment Guide

## Project Structure
```
bakery_tracker/
├── run_server.py
├── requirements.txt
├── Procfile
└── server/
    ├── __init__.py
    ├── flask_app.py
    ├── config.py
    ├── models.py
    ├── routes/
    │   ├── __init__.py
    │   ├── auth_routes.py
    │   ├── dashboard_routes.py
    │   ├── production_routes.py
    │   ├── packaging_routes.py
    │   ├── giveaway_routes.py
    │   └── history_routes.py
    ├── templates/
    │   ├── base.html
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── production.html
    │   ├── packaging.html
    │   ├── giveaway.html
    │   └── history.html
    └── static/
        ├── manifest.json
        ├── js/
        │   └── sw.js
        └── icons/
            ├── icon-192.png   ← Add a 192x192 PNG icon
            └── icon-512.png   ← Add a 512x512 PNG icon
```

## Step 1 — Add your app icons
Create two PNG images of a bread/bakery logo:
- `server/static/icons/icon-192.png` (192×192 px)
- `server/static/icons/icon-512.png` (512×512 px)

You can use any free icon from https://icon.kitchen or https://favicon.io

## Step 2 — Deploy FREE on Render.com

1. Create account at https://render.com
2. Push your project to GitHub
3. Click "New Web Service" → connect your repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn "server.flask_app:create_app()" --worker-class eventlet -w 1`
5. Add environment variable:
   - `SECRET_KEY` = any random string e.g. `bakery-secret-2024`
6. Click Deploy → you get a URL like `https://bakery-tracker.onrender.com`

## Step 3 — Workers install it on their phones

Share the URL with workers. On their phone:
- **Android (Chrome)**: tap the 3-dot menu → "Add to Home Screen"
- **iPhone (Safari)**: tap Share button → "Add to Home Screen"

The app icon will appear on their home screen like a real app.

## Default Logins
| Username | Password    | Role    |
|----------|-------------|---------|
| manager  | manager123  | Manager |
| mandazi  | mandazi123  | Worker  |
| bread    | bread123    | Worker  |
| cakes    | cakes123    | Worker  |
| bagne    | bagne123    | Worker  |
