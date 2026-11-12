<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1F6FEB,100:0D1117&height=170&section=header&text=TIP%20MDS%20EMR&fontSize=38&fontColor=FFFFFF&fontAlignY=36&desc=Electronic%20medical%20records%20for%20TIP%20Medical-Dental%20Services&descSize=15&descAlignY=58" width="100%" alt="TIP MDS EMR" />

![Python](https://img.shields.io/badge/Python%203.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django%204.2-092E20?style=flat-square&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-A30000?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

**A Django-based Electronic Medical Records (EMR) system for the Technological Institute of the Philippines Medical-Dental Services.**

[Overview](#overview) · [Modules](#modules) · [Tech Stack](#tech-stack) · [Getting Started](#getting-started) · [Deployment](#deployment)

</div>

---

## Overview

TIP MDS EMR digitizes the records and workflows of the TIP Medical-Dental Services clinic: student medical records, doctor profiles, appointments, notifications, issued documents, and clinic analytics.

## Modules

| App | Responsibility | Main models |
|---|---|---|
| `accounts` | Users, profiles, and authentication | `User`, `UserProfile` |
| `students` | Student profiles and medical records, with update requests | `StudentProfile`, `MedicalRecord`, `RecordUpdateRequest` |
| `doctors` | Doctor profiles | `DoctorProfile` |
| `appointments` | Scheduling and appointment notes | `Appointment`, `AppointmentNote` |
| `notifications` | In-app notifications, email logs, and preferences | `Notification`, `EmailLog`, `NotificationPreference` |
| `templates_docs` | Document templates, issued certificates, and prescriptions | `Template`, `IssuedCertificate`, `Prescription` |
| `analytics` | Morbidity and consultation statistics, generated reports, and exports | `MorbidityStatistic`, `ConsultationStatistic`, `GeneratedReport` |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 4.2, Django REST Framework |
| Database | PostgreSQL (production) or SQLite (local) |
| Documents | WeasyPrint (PDF), Pillow |
| Configuration | django-environ, django-cors-headers |
| Production | Gunicorn, WhiteNoise |
| Quality | pytest, pytest-django, flake8, black |

## Project Structure

```text
TIP_MDS/
├── tip_mds_emr/       # Django project settings and WSGI
├── accounts/          # Users and authentication
├── students/          # Student profiles and medical records
├── doctors/           # Doctor profiles
├── appointments/      # Scheduling
├── notifications/     # Notifications and email
├── templates_docs/    # Certificates and prescriptions
├── analytics/         # Statistics, reports, exports
├── templates/         # HTML templates
├── static/            # Static assets
├── diagrams/          # Project diagrams
├── manage.py
└── requirements.txt
```

## Getting Started

**Prerequisites:** Python 3.10+, pip, and a virtual environment. PostgreSQL for production, or SQLite for local testing.

1. **Clone and enter the project**
   ```bash
   git clone https://github.com/nixxinix/TIP_MDS.git
   cd TIP_MDS
   ```
2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Linux / macOS
   ```
3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configure the environment.** Copy `.env.example` to `.env` and set:
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   EMAIL_HOST_USER=your-email@tip.edu.ph
   EMAIL_HOST_PASSWORD=your-app-password
   ```
5. **Initialize the database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_demo_data    # optional demo data
   ```
6. **Run the server**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/), or the admin at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Deployment

```bash
pip install gunicorn
python manage.py collectstatic
gunicorn tip_mds_emr.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

**Tips:** always activate the virtual environment before running commands. Logs are written to `logs/django.log`.

---

<div align="center">
<sub>Part of the <a href="https://github.com/nixxinix">nixxinix</a> project portfolio</sub>
</div>
