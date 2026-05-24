# FitTrack — Full Stack Fitness Tracker

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)

A full-stack web application for logging, tracking, and analysing gym workouts. FitTrack provides a clean, dark-themed interface for recording exercise sessions, building workout history, visualising progress over time, and managing personal records.

## Table of Contents

- [Project Overview](#project-overview)
- [Purpose & Value](#purpose--value)
  - [Target Audiences & Their Needs](#target-audiences--their-needs)
  - [Value to the User](#value-to-the-user)
- [User Experience (UX)](#user-experience-ux)
  - [Strategy](#strategy)
  - [Design Rationale](#design-rationale)
  - [Accessibility Considerations](#accessibility-considerations)
- [User Stories](#user-stories)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Data Schema](#data-schema)
- [Security Features](#security-features)
- [Testing Documentation](#testing-documentation)
  - [Manual Testing](#manual-testing)
  - [Automated Testing](#automated-testing)
  - [Test Results](#test-results)
- [Validation](#validation)
- [Known Bugs & Resolutions](#known-bugs--resolutions)
- [Future Improvements](#future-improvements)
- [Project Structure](#project-structure)
- [Sources](#sources)

---

## Project Overview

FitTrack is a full-stack web application that empowers users to systematically log, track, and review their gym workouts. Unlike mobile-only solutions or complex spreadsheet alternatives, FitTrack provides a dedicated web-based interface optimised for both desktop and mobile use, requiring no app installation or subscription fees.

**Key focal points:**
- Streamlined workout logging with inline exercise entry (no separate page per exercise)
- Progress charts: workout frequency, bodyweight trend, and per-exercise estimated 1RM
- Personal records board with automatic PR detection on every save
- Workout templates for quickly starting a session from a saved routine
- Bodyweight tracker with 7-day moving average chart
- Daily notes with mood tracking
- CSV export of full workout history
- Password reset via email
- Arctic Blue dark theme with full responsive design
- Secure user authentication and per-user data isolation

---

## Purpose & Value

FitTrack addresses a critical pain point for fitness enthusiasts: the need for a simple, fast, and reliable way to track workout progress without relying on expensive mobile apps or generic spreadsheets. The application combines the structure of a proper database with the accessibility of a web browser, enabling users to focus on their fitness goals rather than struggling with complex interfaces.

### Target Audiences & Their Needs

1. **Serious Gym Enthusiasts & Strength Athletes**: Users who prioritise detailed workout logging, progressive overload tracking, and data-driven fitness decisions. They need precise recording of sets, reps, weight, and the ability to see estimated 1RM trends over time.

2. **Casual Fitness Trackers & Beginners**: Individuals new to gym training who want a simple, no-frills tool to build a habit of logging workouts without intimidating complexity.

3. **Mobile-First Athletes & On-the-Go Trainers**: Users who train at multiple locations and need quick access to their workout history via any internet-connected device. They require fast load times and responsive layouts.

### Value to the User

- **Accountability Through History**: A persistent, searchable workout log creates accountability and reveals patterns (e.g., "I haven't trained legs in 3 weeks").

- **Progress Visualisation**: The progress page summarises key metrics — workout frequency, bodyweight trend, and per-exercise estimated 1RM — providing instant context about training performance.

- **Automatic PR Detection**: Personal records are detected and stored automatically whenever a workout is saved, with a live PR board showing best weight, reps, and est. 1RM per exercise.

- **Workout Templates**: Save and reuse workout structures (e.g., "Push Day", "Leg Day") to start a logged session in seconds.

- **Data Privacy & Ownership**: Users control their own data; workouts are never shared or sold.

- **Zero Cost, No App Installation**: Running entirely in a web browser with no mobile app download, no subscription, and no third-party account linking.

---

## User Experience (UX)

### Strategy

FitTrack is designed for users who:
- Train regularly and want to build an objective training record
- Prefer simplicity and speed over feature bloat
- May train at different locations and access their data from multiple devices
- Value data privacy and ownership

### Design Rationale

**Dashboard as Hub**: The dashboard serves as the central hub, displaying summary stats, recent workouts, quick-action buttons, today's note, and recent personal records — everything the user needs without digging through menus.

**Inline Exercise Entry**: Exercises are logged directly within the new workout form (using an inline formset), removing the need to navigate to a separate page per exercise. "+ Add Exercise" appends a new row without a page reload.

**Progress Charts**: Three distinct chart types are used for different data shapes:
- Frequency: area chart (shows volume of training over time)
- Bodyweight: line with 7-day moving average dashed overlay
- Exercise progress: mixed bar (sets) + line (estimated 1RM) with shared tooltip and reps shown on hover

**Arctic Blue Dark Theme**: Custom CSS using CSS variables for consistent dark backgrounds (`#0d1117`), blue accent (`#58a6ff`), and off-white text (`#e6edf3`). No third-party CSS framework — all styles are hand-written.

**Grouped Exercise Dropdowns**: Exercises are grouped by muscle group using `<optgroup>`, making selection faster across a large library.

### Accessibility Considerations

- Semantic HTML (`<nav>`, `<main>`, `<header>`, `<footer>`, `<form>`, `<label>`) for assistive technologies
- All form inputs have associated `<label>` elements with proper `for` attributes
- ARIA labels on charts and interactive elements
- `sr-only` descriptions on all Chart.js canvas elements
- `role="group"` and `aria-label` on date range filter buttons
- Keyboard navigation works throughout
- Error messages are descriptive and contextual

---

## User Stories

1. **As a strength athlete**, I want to log my workout with exercise name, sets, reps, and weight so that I can track progressive overload and see my estimated 1RM trend over time.

2. **As a casual gym user**, I want to create workouts quickly with all exercises on one page so that I can log a full session without friction.

3. **As a returning user**, I want to start from a saved template so I don't have to re-enter the same exercises every session.

4. **As a user tracking body composition**, I want to log my bodyweight daily and see a smoothed trend line so I can see progress through daily fluctuations.

5. **As a mobile user**, I want to access my workout history from my phone so I can verify what weight I used last time and stay accountable.

6. **As a privacy-conscious user**, I want my data stored securely in my personal account so it is not shared with third parties.

7. **As a forgetful user**, I want to be able to reset my password via email so I'm not permanently locked out.

---

## Features

### Workout Logging
- **Inline Exercise Entry** — Add all exercises to a new workout on a single page using a formset; "+ Add Exercise" appends rows without a page reload
- **Full CRUD for Workouts** — Create, read, update, and delete workouts with name, date, and notes
- **Full CRUD for Exercise Entries** — Log sets, reps, weight (optional for bodyweight exercises), and notes per entry
- **CSV Export** — Download full workout history as a CSV file

### Progress & Analytics
- **Progress Page** — Four summary stat cards: Total Workouts, Day Streak, Avg Workouts/Week, Personal Records
- **Date Range Filter** — Filter all charts simultaneously by 30d / 90d / 6m / 1y / All time
- **Workout Frequency Chart** — Area chart showing workouts per week or month with human-readable labels
- **Bodyweight Chart** — Line chart with 7-day moving average overlay
- **Exercise Progress Chart** — Mixed bar (sets) + line (estimated 1RM via Epley formula) with shared tooltip
- **Personal Records Board** — Lifetime PR table per exercise showing best weight, reps, est. 1RM, and date
- **Automatic PR Detection** — PRs detected and updated whenever a workout is saved

### Workout Templates
- **Template Library** — Create and manage named workout templates (e.g., "Push Day")
- **Template Detail** — View all exercises in a template with sets, reps, and notes
- **Launch from Template** — Start a new workout pre-filled from a template in one click

### Body & Wellbeing
- **Bodyweight Tracker** — Log daily weigh-ins; chart with 7-day moving average
- **Daily Notes** — Add daily notes with mood tracking (Great / Good / OK / Tired / Bad)
- **Today's Note** — Displayed on the dashboard

### Exercise Library
- **Shared Library** — Browse exercises by name and muscle group
- **Grouped Dropdowns** — Exercise selectors use `<optgroup>` labels by muscle group
- **Custom Exercises** — Add exercises with category, muscle group, and description
- **PROTECT constraint** — Exercises used in workouts cannot be deleted

### User Account
- **Registration & Login** — Secure registration and login with password hashing (PBKDF2)
- **Password Reset** — Email-based forgot-password flow (4-step: request → sent → confirm → complete)
- **Profile Page** — View account details and delete account
- **Access Control** — All data scoped to the logged-in user; direct URL access to another user's data returns 404

---

## Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.12 | Backend programming language |
| **Django** | 4.2 | Web framework — routing, ORM, authentication, templates |
| **PostgreSQL** | 16 | Relational database |
| **psycopg2** | Latest | PostgreSQL adapter for Python |
| **dj-database-url** | Latest | Parse `DATABASE_URL` environment variable |
| **gunicorn** | Latest | Production WSGI server |
| **whitenoise** | Latest | Serve static files in production |
| **python-dotenv** | Latest | Load `.env` file for local development |
| **Chart.js** | 4.4.0 | Interactive progress charts (CDN) |
| **HTML5** | — | Semantic markup and form structure |
| **CSS3** | — | Custom responsive styling (Arctic Blue dark theme, no framework) |
| **Google Fonts** | — | Typography (Bebas Neue, DM Sans) |
| **Heroku** | — | Cloud deployment and hosting |
| **Resend / SMTP** | — | Transactional email for password reset |

---

## Getting Started

### Prerequisites

- **Python 3.12** or higher
- **PostgreSQL** (v16 or higher) running locally
- **Git**

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/MHussainGit/Milestone-Project-3--fitness-tracker.git
cd fitness-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE fittrack;"

# 5. Create your .env file
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env

# 6. Edit .env — set SECRET_KEY and DATABASE_URL at minimum:
#    SECRET_KEY=<any-long-random-string>
#    DATABASE_URL=postgresql://postgres:<password>@localhost:5432/fittrack

# 7. Run migrations
python manage.py migrate

# 8. Seed the exercise library
python manage.py seed_exercises

# 9. (Optional) Create a superuser for /admin/
python manage.py createsuperuser

# 10. Start the dev server
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Running Tests

```bash
# Using pytest (recommended)
.venv\Scripts\python.exe -m pytest

# Or using Django's test runner
python manage.py test
```

---

## Deployment

FitTrack is deployed to **Heroku** with automatic migrations on every deploy.

### Step-by-Step

```bash
# 1. Create the app
heroku create your-app-name

# 2. Provision PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# 3. Set environment variables
heroku config:set SECRET_KEY="$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set CSRF_TRUSTED_ORIGINS=https://your-app-name.herokuapp.com

# 4. Deploy
git push heroku main

# 5. Verify
heroku open
heroku logs --tail
```

### Enabling Email (Password Reset)

Password reset emails print to the terminal locally (console backend). For production, configure an SMTP provider:

```bash
# Example using Resend (free tier: 3,000 emails/month)
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
heroku config:set EMAIL_HOST=smtp.resend.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_HOST_USER=resend
heroku config:set EMAIL_HOST_PASSWORD=your_api_key
heroku config:set DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

See `.env.example` for full documentation of all email options.

### Deployment Notes

- `Procfile` runs `python manage.py migrate` and `python manage.py seed_exercises` automatically on every deploy
- Static files are served via WhiteNoise — no separate CDN required
- Python version is pinned via `.python-version` (contains `3.12`)
- `DATABASE_URL` is set automatically by the Heroku PostgreSQL addon

---

## Data Schema

### Entity-Relationship Diagram

```
User (Django auth_user)
 ├─ Workout            [user FK → User, CASCADE]
 │   └─ WorkoutEntry   [workout FK → Workout, CASCADE]
 │                      [exercise FK → Exercise, PROTECT]
 ├─ PersonalRecord     [user FK → User, CASCADE]
 │                      [exercise FK → Exercise, PROTECT]
 ├─ BodyWeightEntry    [user FK → User, CASCADE]
 ├─ DailyNote          [user FK → User, CASCADE]
 └─ WorkoutTemplate    [user FK → User, CASCADE]
     └─ WorkoutTemplateItem [template FK → WorkoutTemplate, CASCADE]
                             [exercise FK → Exercise, PROTECT]

Exercise (shared library — no user FK)
```

### Table Descriptions

| Table | Key Fields | Notes |
|---|---|---|
| `auth_user` | id, username, email, password_hash | Django built-in; PBKDF2 hashing |
| `tracker_exercise` | id, name, category, muscle_group, description | Shared across all users; name UNIQUE |
| `tracker_workout` | id, user_id, name, date, notes | Per-user; CASCADE on user delete |
| `tracker_workoutentry` | id, workout_id, exercise_id, sets, reps, weight, notes | weight nullable for bodyweight exercises |
| `tracker_personalrecord` | id, user_id, exercise_id, best_weight, best_reps, est_1rm, achieved_date | One record per user+exercise; upserted on save |
| `tracker_bodyweightentry` | id, user_id, date, weight | Daily weigh-ins |
| `tracker_dailynote` | id, user_id, date, content, mood | One note per user per date |
| `tracker_workouttemplate` | id, user_id, name, notes | Named template per user |
| `tracker_workouttemplatem item` | id, template_id, exercise_id, sets, reps, notes | Exercises within a template |

---

## Security Features

| Feature | Implementation |
|---|---|
| **Secret Key** | Environment variable — never in source code |
| **Debug Mode** | Env var; defaults `False` in production |
| **CSRF Protection** | Django `CsrfViewMiddleware` on all POST requests |
| **Password Hashing** | PBKDF2 with salt; plaintext never stored |
| **Password Reset** | Django's built-in token-based flow via email |
| **Login Required** | `@login_required` on all authenticated views |
| **Object-Level Auth** | All queries filtered by `user=request.user`; other users' data returns 404 |
| **SQL Injection** | Django ORM parameterised queries throughout |
| **`.env` in `.gitignore`** | Secrets never committed |
| **ALLOWED_HOSTS** | Prevents Host header attacks |
| **CSRF Trusted Origins** | Restricts cross-origin POST to trusted domains |

---

## Testing Documentation

### Manual Testing

#### Authentication Tests

| ID | Feature | Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| AT-01 | Registration | Register with valid data | Account created; redirect to dashboard | ✅ Pass |
| AT-02 | Registration | Duplicate username | Error: "Username already exists" | ✅ Pass |
| AT-03 | Registration | Weak password | Validation error shown | ✅ Pass |
| AT-04 | Login | Correct credentials | Redirect to dashboard | ✅ Pass |
| AT-05 | Login | Wrong password | Error message shown | ✅ Pass |
| AT-06 | Access Control | Access `/dashboard/` logged out | Redirect to `/login/` | ✅ Pass |
| AT-07 | Logout | Click Logout | Session cleared; redirect to login | ✅ Pass |
| AT-08 | Password Reset | Submit registered email | Redirect to done page; email sent | ✅ Pass |
| AT-09 | Password Reset | Submit unknown email | Same redirect (no enumeration) | ✅ Pass |
| AT-10 | Password Reset | Follow token link | Set new password form shown | ✅ Pass |

#### Workout Tests

| ID | Feature | Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| WT-01 | Create | Submit workout with inline exercises | Workout + entries saved; redirect to detail | ✅ Pass |
| WT-02 | Create | Submit with empty name | Validation error | ✅ Pass |
| WT-03 | Read | Click workout from list | Detail page shows all entries | ✅ Pass |
| WT-04 | Read | Access another user's workout URL | 404 returned | ✅ Pass |
| WT-05 | Update | Edit workout name | Name updated; flash message shown | ✅ Pass |
| WT-06 | Delete | Delete workout | Workout removed; redirect to list | ✅ Pass |

#### Progress Page Tests

| ID | Feature | Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| PP-01 | Stat cards | Load progress page | 4 stat cards visible with correct values | ✅ Pass |
| PP-02 | Date filter | Click "30d" | All charts update to last 30 days | ✅ Pass |
| PP-03 | Freq chart | Toggle Weekly/Monthly | Chart re-renders with correct grouping | ✅ Pass |
| PP-04 | Exercise chart | Select an exercise | Est. 1RM line + sets bar chart renders | ✅ Pass |
| PP-05 | Bodyweight chart | Log 7+ weights | Moving average dashed line appears | ✅ Pass |

#### Responsiveness Tests

| ID | Viewport | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| RES-01 | 375px (mobile) | Single-column layout; no overflow | ✅ Pass |
| RES-02 | 768px (tablet) | 2-column grid; charts readable | ✅ Pass |
| RES-03 | 1200px+ (desktop) | Full layout; stat cards in row | ✅ Pass |

### Automated Testing

```bash
# Run with pytest (recommended)
.venv\Scripts\python.exe -m pytest

# Run with Django test runner
python manage.py test

# Specific class
python manage.py test tests.test_fittrack.WorkoutCRUDTests

# Verbose
python manage.py test --verbosity=2
```

**Test Suite Coverage:**
- Exercise model: `__str__`, ordering, unique constraint
- Workout model: `__str__`, volume calculation, entry count
- WorkoutEntry model: volume with/without weight
- Form validation: WorkoutForm, ExerciseForm, RegisterForm
- Authentication views: register, login, logout, redirect
- Workout CRUD views: create (with formset), list, detail, edit, delete, access control
- WorkoutEntry CRUD: add, edit, delete
- Exercise library: create, list, filter, edit, delete (used/unused)
- Dashboard: load, stats, username display

### Test Results

#### Automated Tests

| Area | Tests | Pass | Fail |
| :--- | :---: | :---: | :---: |
| Authentication (views + forms) | 9 | 9 | 0 |
| Workouts (models + forms + CRUD) | 14 | 14 | 0 |
| Exercise Entries (models + CRUD) | 5 | 5 | 0 |
| Exercise Library (models + forms + CRUD) | 11 | 11 | 0 |
| Dashboard | 3 | 3 | 0 |
| **Total** | **42** | **42** | **0** |

---

## Validation

### Python / Django

- All `ModelForm` subclasses validate required fields, unique constraints, and custom logic
- All database queries use Django ORM parameterised queries (no raw SQL)
- All views protected by `@login_required` or `LoginRequiredMixin`

### HTML5

- Proper use of semantic elements (`<nav>`, `<main>`, `<form>`, `<label>`)
- All inputs have associated `<label>` elements
- Correct heading hierarchy throughout

### CSS3

- Custom CSS with CSS variables; no third-party framework
- CSS Grid and Flexbox for layouts
- Media queries at 768px, 900px, 1100px, 1300px breakpoints
- All CSS variables defined in `:root`

### Accessibility (WCAG 2.1 AA)

| Criterion | Status |
| :--- | :---: |
| Semantic HTML structure | ✅ |
| Keyboard navigation | ✅ |
| Form labels on all inputs | ✅ |
| `sr-only` descriptions on charts | ✅ |
| ARIA labels on interactive controls | ✅ |
| Colour contrast ≥ 4.5:1 | ✅ |
| Focus indicators visible | ✅ |
| Responsive design (mobile/tablet/desktop) | ✅ |

---

## Known Bugs & Resolutions

#### Bug 1 — No Pagination on Workout List

| Field | Detail |
| :--- | :--- |
| **ID** | BUG-01 |
| **Issue** | Users with hundreds of workouts see all of them on one page, causing slow load times. |
| **Resolution** | Implement Django pagination with 20 workouts per page |
| **Status** | ⏳ Planned |

#### Bug 2 — Exercise Library is Shared Across All Users

| Field | Detail |
| :--- | :--- |
| **ID** | BUG-02 |
| **Issue** | All users share one exercise library; custom exercises added by one user are visible to all. |
| **Resolution** | Add optional `user` FK to Exercise; scope queries per user with global fallback |
| **Status** | ⏳ Planned |

---

## Future Improvements

1. **Workout Pagination** — Handle large workout histories efficiently
2. **User-Scoped Exercise Library** — Personal exercises alongside a global shared library
3. **Workout Cloning** — Duplicate a past workout as a new session
4. **Mobile App** — Native or React Native app with offline sync
5. **Social Features** — Optionally share workout summaries or join challenges
6. **REST API** — Expose endpoints for third-party integrations

---

## Project Structure

```
fitness-tracker/
├── fittrack/                          # Django project config
│   ├── settings.py                    # All settings (DB, auth, email, middleware)
│   ├── urls.py                        # Root URL dispatcher
│   └── wsgi.py                        # WSGI entry point
│
├── tracker/                           # Main application
│   ├── models.py                      # All models + WorkoutManager (streak)
│   ├── views.py                       # All views (FBV + CBV)
│   ├── forms.py                       # Forms + WorkoutEntryFormSet
│   ├── urls.py                        # App URL patterns (incl. password reset)
│   ├── admin.py                       # Admin registrations
│   └── templates/tracker/
│       ├── dashboard.html
│       ├── login.html
│       ├── register.html
│       ├── workout_list.html
│       ├── workout_detail.html
│       ├── workout_form.html          # Create (inline formset) + edit
│       ├── entry_form.html
│       ├── exercise_list.html
│       ├── exercise_form.html
│       ├── progress.html              # Charts + stat cards
│       ├── bodyweight.html
│       ├── notes.html
│       ├── profile.html
│       ├── template_list.html
│       ├── template_form.html
│       ├── template_detail.html
│       └── confirm_delete.html
│
├── templates/
│   ├── base.html                      # Shared base (nav, footer)
│   └── registration/                  # Django auth password reset templates
│       ├── password_reset_form.html
│       ├── password_reset_done.html
│       ├── password_reset_confirm.html
│       └── password_reset_complete.html
│
├── static/
│   └── css/
│       └── styles.css                 # Arctic Blue dark theme (CSS variables)
│
├── tests/
│   └── test_fittrack.py               # 42 automated tests
│
├── .env.example                       # Environment variable template
├── .gitignore
├── .python-version                    # Python 3.12 (Heroku)
├── conftest.py                        # pytest-django config
├── manage.py
├── Procfile                           # Heroku release + web commands
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Sources

### Libraries & Frameworks

**Django 4.2** — Web framework (routing, ORM, auth, templates, password reset)
https://www.djangoproject.com/

**PostgreSQL** — Relational database providing ACID compliance, foreign key constraints, and scalability
https://www.postgresql.org/

**Bootstrap 5.3** — Responsive grid, components (buttons, modals, forms), and utility classes
https://getbootstrap.com/

**Chart.js 4.4.0** — Interactive canvas charts (frequency, bodyweight, exercise progress)
https://www.chartjs.org/

**psycopg2** — PostgreSQL adapter for Python
https://www.psycopg.org/

**gunicorn** — Production WSGI server
https://gunicorn.org/

**WhiteNoise** — Static file serving in production without a separate CDN
https://whitenoise.readthedocs.io/

**python-dotenv** — `.env` loading for local development
https://github.com/theskumar/python-dotenv

**dj-database-url** — `DATABASE_URL` parsing
https://github.com/jazzband/dj-database-url

**Google Fonts** — Roboto (body and display typography)
https://fonts.google.com/

### Deployment

**Heroku** — Cloud hosting + PostgreSQL
https://www.heroku.com/

**Resend** — Transactional email for password reset
https://resend.com/

### References

**Django Documentation** — https://docs.djangoproject.com/

**MDN Web Docs** — HTML5, CSS3, JavaScript
https://developer.mozilla.org/

---

**FitTrack © 2026 — Built with Django, PostgreSQL, and Chart.js**
