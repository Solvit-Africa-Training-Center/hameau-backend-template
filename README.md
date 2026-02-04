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
├── config/
│ ├── settings/
│ │ ├── auth.py
│ │ ├── base.py
│ │ ├── cors.py
│ │ ├── database.py
│ │ ├── dev.py
│ │ ├── email.py
│ │ ├── prod.py
│ │ ├── rest.py
│ │ ├── static.py
│ │ ├── template.py    
│ │ └── third_party.py
│ ├── urls.py
│ ├── asgi.py
│ └── wsgi.py
├── accounts/
│ ├── adapters.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── serializers.py
│ ├── urls.py
│ ├── views.py
│ └── tests.py
├── blogs/
├── ifashe/
├── internships/
├── residentials/
├── public_modules/
├── static/
├── templates/
├── .gitignore.py
├── Dockerfile
├── Procfile
├── manage.py
├── runtime.txt
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
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

STRIPE_PUBLISHABLE_KEY= xxx
STRIPE_SECRET_KEY= xxx
STRIPE_WEBHOOK_SECRET= xxx


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

8. Run Development Server
> python manage.py runserver

Server will be available at: http://127.0.0.1:8000/ and you can then try out API endpoints available

9. Git Workflow (Backend Team)

Recommended workflow:
```
git checkout -b feature/your-feature-name
git commit -m "Add feature"
git push origin feature/your-feature-name
```

