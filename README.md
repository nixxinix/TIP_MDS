# TIP MDS EMR - Backend Quick Setup Guide

A **Django-based Electronic Medical Records (EMR)** system for the Technological Institute of the Philippines Medical-Dental Services.
This guide helps you quickly set up and run the backend locally.

---

## 📁 Required Files

Before starting, make sure you have these files:

* `requirements.txt` – Python dependencies
* `.env.example` → rename to `.env` and update configuration
* `manage.py` – Django management script
* `tip_mds/` – main Django project folder

(Optional: database backup or seed file for demo data)

---

## ⚙️ Prerequisites

* **Python** 3.10+
* **pip** (latest)
* **Virtual Environment** (`venv`)
* **PostgreSQL** (for production) or SQLite (for local testing)

---

## 🚀 Setup Procedure

### 1. Clone Repository

```bash
git clone <repository-url>
cd tip_mds
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST_USER=your-email@tip.edu.ph
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

(Optional: seed demo data)

```bash
python manage.py seed_demo_data
```

### 6. Run the Server

```bash
python manage.py runserver
```

Access the app at:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧩 Production (Optional)

```bash
pip install gunicorn
gunicorn tip_mds_emr.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🧠 Tips

* Always activate your virtual environment before running commands.
* Use `python manage.py collectstatic` before deployment.
* Logs can be found in `logs/django.log`.

---