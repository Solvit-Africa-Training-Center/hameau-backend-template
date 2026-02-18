# Backend API — Local Development Setup

This repository contains the **Django REST API backend** for the project "Hameau des Jeunes".

This backendAPI is already hosted on https://tricky-cyb-matabar-576778bf.koyeb.app/ .
This means that the project that when we are working, we will only be pushing on our personal branches inheriting from the main branch. Never push directly to main.
Don't forget to write tests when working and before pushing.

The project is designed to be:

- Production-ready
- Easy to set up locally
- Safe to work on in a team

This README focuses **only on local backend setup** for developers.

---

We have (5) django-apps : accounts, ifashe, internships, public_modules, residentials.
Settings are split into modules for better lisibility.

---

## Tech Stack

- **Python 3.11+**
- **Django**
- **Django REST Framework**
- **PostgreSQL (Supabase)**
- **JWT Authentication**
- **django-allauth + dj-rest-auth**
- **Cloudinary (media storage)**
- **pytest (testing)**
- **GitHub Actions (CI)**

---

## Project Structure

```
hameauBackend/
├── accounts
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests
│   │   ├── __init__.py
│   ├── urls.py
│   └── views.py
|
|
├── config
│   ├── asgi.py
│   ├── celery.py
│   ├── __init__.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── base.py
│   │   ├── celery.py
│   │   ├── cors.py
│   │   ├── database.py
│   │   ├── dev.py
│   │   ├── email.py
│   │   ├── logging.py
│   │   ├── prod.py
│   │   ├── rest.py
│   │   ├── static.py
│   │   └── third_party.py
│   ├── urls.py
│   └── wsgi.py
|
|
├── programs
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── ifashe_models.py
│   │   ├── internships_models.py
│   │   └── residentials_models.py
│   ├── serializers
│   │   ├── __init__.py
│   │   ├── ifashe_serializers.py
│   │   ├── internships_serializers.py
│   │   └── residentials_serializers.py
|   |
│   ├── tasks.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── tests_ifashe_models.py
│   │   │   ├── tests_internships_models.py
│   │   │   └── tests_residentials_models.py
│   │   └── views
│   │       └── tests_internship_views.py
|   |
│   ├── urls.py
│   └── views
│       ├── __init__.py
│       ├── ifashe_views
│       │   ├── __init__.py
│       │   ├── all_reports_views.py
│       │   ├── child_views.py
│       │   ├── family_views.py
│       │   ├── parent_views.py
│       │   ├── school_views.py
│       │   └── sponsorship_views.py
│       ├── internships_views
│       │   ├── application_views.py
│       │   ├── __init__.py
│       │   └── internship_views.py
│       └── residentials_views
│           ├── __init__.py
│           ├── caretaker_views.py
│           ├── child_views.py
│           ├── health_record_views.py
│           └── residential_finance_views.py
|
|
├── public_modules
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests
│   │   ├── __init__.py
│   │   └── tests_models.py
│   └── views.py
|
|
├── templates
│   ├── emails
│   │   ├── email_reset_password.html
│   │   ├── email_temporary_credentials.html
│   │   └── internship_status.html
│   ├── home1.html
│   └── rapidoc.html
|
├── utils
│   ├── emails.py
│   ├── filters
│   │   ├── child_filters.py
│   │   └── health_records_filters.py
│   ├── general_codes.py
│   ├── paginators.py
│   ├── reports
│   │   ├── general_reports.py
│   │   ├── ifashe
│   │   │   ├── base.py
│   │   │   ├── family_reports.py
│   │   │   ├── helpers.py
│   │   │   ├── __init__.py
│   │   │   ├── parents_work_reports.py
│   │   │   ├── summary_reports.py
│   │   │   └── supports_reports.py
│   │   └── residentials
│   │       ├── base.py
│   │       ├── helpers.py
│   │       ├── __init__.py
│   │       └── spending_summary.py
│   ├── search.py
│   └── validators.py
|
├── logs
│   └── hameau.log
|
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── .env
├── .env.example
├── .gitignore
├── manage.py
├── Procfile
├── pytest.ini
├── README.md
├── requirements.txt
├── runtime.txt

```

---

## Prerequisites

Make sure you have the following installed:

- Python **3.12 or higher**
- Git
- pip
- A Supabase project (PostgreSQL) - or store your DB locally
- A Cloudinary account (to store media files online)
- A Gmail account (SMTP – app password)

## Steps

1. Clone the repository

> git clone https://github.com/Solvit-Africa-Training-Center/hameau-backend

> cd hameau-backend

2. Create Virtual Environment

> python -m venv venv

Activate it

> source venv/bin/activate on mac/linux or venv\Scripts\activate on windows

3. Install dependancies

> pip install -r requirements.txt

4. Create a .env file at the project root : follow .env.example

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=your-project.supabase.co
DB_PORT=5432

CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password


```

5. Database Setup (Supabase)

You can either user local DB or free online hosted one

- Create a Supabase project
- Copy PostgreSQL credentials
- Paste them into .env
- SSL is required (already configured in settings)

6. Run Migrations

```
python manage.py makemigrations
python manage.py migrate
```

7. Create Superuser

   > python manage.py createsuperuser

8. Git Workflow (Backend Team)

Recommended workflow:

```
git checkout -b feature/your-feature-name
git commit -m "Add feature"
git push origin feature/your-feature-name
```

9. Celery and Redis installation

- Installation of redis on Linux and Mac

> sudo apt-get install redis

On windows, use these commands in your PowerSehell as Administrator

> wsl --install # Then restart your computer

Then open the Ubuntu terminal and run,

```
sudo apt update
sudo apt install redis-server
```

- Start Redis ( All computer, windows, mac and linux)

  > sudo service redis-server start

- Now we go back to the project and install redis driver and celery

  > pip install redis celery

- Add these two lines in your .env

```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

- Comment out these code in settings/celery.py in developpement but uncomment them when you push

```
CELERY_BROKER_USE_SSL = {
    'ssl_cert_reqs': 'none'
}
CELERY_REDIS_BACKEND_USE_SSL = {
    'ssl_cert_reqs': 'none'
}
```

10. Run Development Server

    > python manage.py runserver

11. Run this in a new terminal
    > celery -A config worker --loglevel=info

Server will be available at: http://127.0.0.1:8000/ and you can then try out API endpoints available
