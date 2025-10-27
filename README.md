#  Redlight Sports Events Platform

A web application to manage and organize sports events with user authentication, role management, calendar export, email notifications, and participant tracking.

---

##  Features

- User registration with profile picture
- Login/logout with session management
- Create, edit, delete, and view events
- Register and add participants to events
- Role-based access (admin/general)
- Email notifications (optional in dev)
- Export events to calendar
- Logging and soft deletion

---

##  Setup Instructions

### 1. Clone the repository

```bash
git clone https://gitlab.com/guilhermecruz760/red-light-challenge.git
cd redlight-platform
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `app_secrets.py`

This file contains sensitive keys and is ignored by Git.

```python
# app_secrets.py
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-password"
SECRET_KEY = "your-secret-key"
```

### 5. Initialize the database

In a Python shell or script:

```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

---

##  Running the App (Development)

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

The app will be running at: [http://localhost:5000](http://localhost:5000)

---

##  Project Structure

```
redlight-platform/
│
├── app/
│   ├── routes/                # Blueprints
│   ├── static/                # CSS, uploads
│   ├── templates/             # HTML files
│   ├── models.py              # Database models
│   └── __init__.py            # App factory
│
├── config.py                  # Configuration settings
├── app_secrets.py             # Secret values (ignored in Git)
├── run.py                     # App runner
├── requirements.txt           # Dependencies
├── logs/                      # Application logs
├── documentation.md           # Documentation File
└── README.md                  # This file

```

---

## Notes

- Email notifications only work if `MAIL_ENABLED = True` in `config.py`
- Uploaded user profile pictures go to `/static/uploads/`
- Logs are saved under `logs/app.log`
- The folder app/static/website/ must contain two subfolders: caroussel/ and logos/. These include event and logo images used in the platform.
    - A ZIP file containing these subfolders is provided by email. Extract its contents into app/static/website/ before running the app.


---

## Author

Carefully developed by Guilherme Cruz