# RxLabel Web App

Flask product website with license request form, SQLite storage, and protected admin panel.

## Structure

```
rxlabel-app/
├── run.py                       # Entry point
├── requirements.txt
├── rxlabel/                     # App package
│   ├── __init__.py              # create_app factory
│   ├── extensions.py            # SQLite db helper
│   └── blueprints/
│       ├── main.py              # GET  /
│       ├── license.py           # POST /request-license
│       └── admin.py             # /admin/* (login-protected)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── partials/
│   │   ├── nav.html
│   │   ├── footer.html
│   │   └── license_modal.html
│   └── admin/
│       ├── base_admin.html
│       ├── login.html
│       └── requests.html
└── static/
    ├── css/
    │   ├── base.css             # Variables, reset, keyframes
    │   ├── nav.css
    │   ├── hero.css             # Hero + carousel
    │   ├── sections.css         # Features, 5R, products, pricing, footer
    │   ├── modal.css            # License modal + toast
    │   └── admin.css            # Admin + login
    ├── js/
    │   ├── carousel.js
    │   ├── modal.js
    │   └── admin.js
    └── img/
```

## Run

```bash
pip install -r requirements.txt
python run.py
# Visit http://localhost:5000
# Admin: http://localhost:5000/admin/login
```

## Admin Credentials (override via env vars)

| Variable         | Default           |
|------------------|-------------------|
| ADMIN_USERNAME   | admin             |
| ADMIN_PASSWORD   | rxlabel2026       |
| SECRET_KEY       | change-me-in-prod |

```bash
export SECRET_KEY="your-secret"
export ADMIN_USERNAME="your-user"
export ADMIN_PASSWORD="your-password"
```
