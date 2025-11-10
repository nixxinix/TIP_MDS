# TIP MDS EMR - Backend Documentation

Electronic Medical Records System for Technological Institute of the Philippines Medical-Dental Services.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Backend Components](#backend-components)
- [API Structure](#api-structure)
- [Database Schema](#database-schema)
- [Management Commands](#management-commands)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

The TIP MDS EMR backend is a Django-based REST API that provides comprehensive electronic medical record management for students at the Technological Institute of the Philippines. The system handles student health records, appointments, medical certificates, and analytics with role-based access control.

### Key Features

- **Student Management**: Complete medical and dental records with document attachments
- **Appointment System**: Scheduling, approval, and management workflows
- **Certificate Generation**: Automated PDF generation for medical certificates and prescriptions
- **Analytics Dashboard**: Morbidity statistics and health trends reporting
- **Notification System**: Email notifications for appointments and updates
- **Update Workflow**: Student information update requests with approval process

---

## System Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 4.2+ |
| Database | PostgreSQL / SQLite | 12+ / 3.x |
| API | Django REST Framework | 3.14+ |
| PDF Generation | WeasyPrint | 59+ |
| Authentication | Django Auth | Built-in |
| Task Queue | Django Management Commands | - |

### Application Structure

The backend follows Django's MVT (Model-View-Template) architecture with the following core applications:

- **accounts**: User authentication and authorization
- **students**: Student profiles and medical records
- **doctors**: Healthcare provider profiles and management
- **appointments**: Appointment scheduling and tracking
- **templates_docs**: Medical certificates and prescriptions
- **analytics**: Statistics and reporting
- **notifications**: Email and in-app notifications

---

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **pip**: Latest version
- **PostgreSQL**: 12+ (production) or SQLite (development)
- **Virtual Environment**: venv or virtualenv

### Platform-Specific Dependencies

**Ubuntu/Debian** (for PDF generation):
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

**macOS**:
```bash
brew install pango
```

**Windows**:
No additional system dependencies required.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd tip_mds_emr_backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 5. Load Initial Data (Optional)

```bash
# Seed demo data for testing
python manage.py seed_demo_data
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Development (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Production (PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/tip_mds_emr

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@tip.edu.ph
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@tip.edu.ph

# Security
INSTITUTIONAL_EMAIL_DOMAIN=tip.edu.ph
```

### Email Setup

For Gmail:
1. Enable 2-Factor Authentication
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the app password in `EMAIL_HOST_PASSWORD`

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

---

## Running the Application

### Development Server

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000
```

### Access Points

- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Student Portal**: http://localhost:8000/student/dashboard/
- **Doctor Portal**: http://localhost:8000/doctor/dashboard/
- **API Endpoints**: http://localhost:8000/api/

### Production Server

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn tip_mds_emr.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## Backend Components

### 1. Accounts Application

**Purpose**: User authentication and role-based access control

**Key Components**:
- `models.py`: Custom User model with email-based authentication
- `backends.py`: Email authentication backend
- `decorators.py`: Role-based permission decorators (`@student_required`, `@doctor_required`)
- `forms.py`: Registration and login forms with institutional email validation

**User Roles**:
- **Student**: Access to personal records and appointment booking
- **Doctor**: Medical record creation and management
- **Admin**: Full system access and user management

### 2. Students Application

**Purpose**: Student profile and medical record management

**Key Models**:
- `StudentProfile`: Demographics, emergency contacts, medical history
- `MedicalRecord`: Medical and dental visit records with diagnoses
- `DentalRecord`: Specialized dental treatment records
- `UpdateRequest`: Student information update workflow with approval

**Features**:
- Complete medical history tracking
- File attachment support for medical documents
- Update request approval workflow (7-day expiration)
- Blood type and allergy tracking

### 3. Doctors Application

**Purpose**: Healthcare provider management

**Key Models**:
- `DoctorProfile`: Doctor credentials, specialization, and schedule

**Features**:
- Provider search and filtering
- Schedule management
- Patient record access control

### 4. Appointments Application

**Purpose**: Appointment scheduling and management

**Key Models**:
- `Appointment`: Scheduled visits with status tracking
- `AppointmentNote`: Clinical notes for completed appointments

**Workflow**:
1. Student creates appointment request
2. Doctor/Admin approves or declines
3. Appointment can be rescheduled
4. Doctor marks as completed with notes

**Status Types**:
- Pending, Approved, Declined, Completed, Cancelled, No Show

### 5. Templates & Documents Application

**Purpose**: Medical certificate and prescription generation

**Key Models**:
- `Template`: Certificate templates (Medical, Dental, Fit to Work)
- `IssuedCertificate`: Generated certificates with PDF
- `Prescription`: Medication prescriptions with dosage

**PDF Generation**:
- Uses WeasyPrint for HTML-to-PDF conversion
- Template-based rendering with Django templates
- Digital signature support
- Automatic email delivery

### 6. Analytics Application

**Purpose**: Health statistics and reporting

**Key Models**:
- `MorbidityStatistic`: Disease frequency tracking
- `AppointmentStatistic`: Appointment trends

**Features**:
- Morbidity rate calculations
- Top 10 diseases tracking
- Appointment analytics by service type
- Export to CSV and PDF
- Monthly statistics generation

### 7. Notifications Application

**Purpose**: User notifications and email delivery

**Key Models**:
- `Notification`: In-app notifications
- `EmailLog`: Email delivery tracking
- `NotificationPreferences`: User notification settings

**Notification Types**:
- Appointment confirmations and reminders
- Update request approvals
- Certificate issuance
- System announcements

---

## API Structure

### Authentication Endpoints

```
POST   /accounts/login/          # User login
POST   /accounts/register/       # Student registration
POST   /accounts/logout/         # User logout
GET    /accounts/profile/        # User profile
```

### Student Endpoints

```
GET    /student/dashboard/       # Student dashboard
GET    /student/records/         # Medical records list
POST   /student/update-request/  # Request information update
GET    /student/appointments/    # Appointment list
POST   /student/book-appointment/ # Book appointment
```

### Doctor Endpoints

```
GET    /doctor/dashboard/        # Doctor dashboard
GET    /doctor/search/           # Search students
GET    /doctor/pending-requests/ # Pending update requests
POST   /doctor/create-record/    # Create medical record
POST   /doctor/approve-request/  # Approve update request
GET    /doctor/analytics/        # Analytics dashboard
```

### Document Endpoints

```
POST   /documents/certificate/   # Generate certificate
GET    /documents/certificates/  # List certificates
POST   /documents/prescription/  # Create prescription
GET    /documents/download/<id>/ # Download PDF
```

---

## Database Schema

### Core Tables

**users** (Custom User Model)
- id, email, password, role, is_active, is_staff, created_at

**student_profiles**
- user_id, student_number, program, year_level, blood_type, allergies, emergency_contact

**medical_records**
- student_id, record_type, chief_complaint, diagnosis, treatment, doctor_id, date

**appointments**
- student_id, doctor_id, service_type, appointment_date, status, reason

**issued_certificates**
- student_id, template_id, issued_by, purpose, valid_until, pdf_file

### Relationships

- User ↔ StudentProfile (1:1)
- User ↔ DoctorProfile (1:1)
- Student ↔ MedicalRecords (1:N)
- Student ↔ Appointments (1:N)
- Doctor ↔ MedicalRecords (1:N)
- Doctor ↔ IssuedCertificates (1:N)

---

## Management Commands

### Seed Demo Data

```bash
# Create sample data for testing
python manage.py seed_demo_data

# Clear existing data and reseed
python manage.py seed_demo_data --clear
```

Creates:
- 3 doctors/staff accounts
- 30 student accounts
- 100+ medical records
- 20+ appointments
- Sample certificate templates

### Generate Statistics

```bash
# Generate monthly statistics
python manage.py generate_statistics --period monthly

# Generate yearly statistics
python manage.py generate_statistics --period yearly
```

### Send Appointment Reminders

```bash
# Send email reminders for upcoming appointments
python manage.py send_reminders
```

### Database Management

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create database backup
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
```

---

## Deployment

### Production Configuration

1. **Update Settings**

```python
# tip_mds_emr/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# Use environment variables for sensitive data
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}
```

2. **Static Files**

```bash
python manage.py collectstatic --noinput
```

3. **Install Production Server**

```bash
pip install gunicorn psycopg2-binary
```

4. **Run with Gunicorn**

```bash
gunicorn tip_mds_emr.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

5. **Setup Nginx Reverse Proxy**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

6. **Setup Cron Jobs**

```cron
# Daily appointment reminders at 8 AM
0 8 * * * cd /path/to/project && /path/to/.venv/bin/python manage.py send_reminders

# Monthly statistics generation
0 0 1 * * cd /path/to/project && /path/to/.venv/bin/python manage.py generate_statistics --period monthly
```

7. **Setup Systemd Service**

```ini
# /etc/systemd/system/tip_emr.service
[Unit]
Description=TIP MDS EMR Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/gunicorn tip_mds_emr.wsgi:application --bind 0.0.0.0:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tip_emr
sudo systemctl start tip_emr
```

---

## Troubleshooting

### WeasyPrint Installation Errors

**Error**: `OSError: cannot load library 'gobject-2.0-0'`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# macOS
brew install pango
```

### Database Connection Failed

**Error**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check DATABASE_URL in `.env` file
3. Verify database credentials
4. Ensure database exists: `createdb tip_mds_emr`

### Email Not Sending

**Error**: `SMTPAuthenticationError`

**Solution**:
1. Use App Password instead of regular password (Gmail)
2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in `.env`
3. Check firewall allows port 587
4. Test email configuration:
```python
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@tip.edu.ph', ['to@tip.edu.ph'])
```

### Static Files Not Loading

**Solution**:
```bash
python manage.py collectstatic --clear --noinput
```

### Permission Denied on Media Files

**Solution**:
```bash
chmod -R 755 media/
chown -R www-data:www-data media/
```

---

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students
python manage.py test appointments

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## Support

For technical issues:
- Check application logs: `logs/django.log`
- Review Django debug toolbar in development
- Verify database migrations: `python manage.py showmigrations`

---

## License

Developed for Technological Institute of the Philippines Medical-Dental Services.

© 2025 TIP MDS EMR. All rights reserved.