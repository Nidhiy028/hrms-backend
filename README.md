# HRMS Lite – Backend API

A RESTful backend for the Human Resource Management System (Lite), built with **FastAPI** and **SQLAlchemy**.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Framework  | FastAPI 0.115                     |
| ORM        | SQLAlchemy 2.0                    |
| Database   | SQLite (dev) / PostgreSQL (prod)  |
| Validation | Pydantic v2                       |
| Server     | Uvicorn (ASGI)                    |
| Deployment | Render (recommended)              |

---

## Project Structure

```
hrms-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS, routers
│   ├── database.py      # DB engine & session
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── routers/
│       ├── employees.py # Employee CRUD endpoints
│       └── attendance.py# Attendance endpoints
├── requirements.txt
├── render.yaml          # Render deployment config
├── Procfile             # Railway/Heroku start command
├── run.py               # Local dev entry point
├── .env.example
└── README.md
```

---

## API Endpoints

### Employees
| Method | Endpoint                        | Description                      |
|--------|---------------------------------|----------------------------------|
| POST   | `/api/employees/`               | Add new employee                 |
| GET    | `/api/employees/`               | List all employees (with stats)  |
| GET    | `/api/employees/{id}`           | Get single employee              |
| DELETE | `/api/employees/{id}`           | Delete employee + their records  |
| GET    | `/api/employees/dashboard/stats`| Dashboard summary                |

### Attendance
| Method | Endpoint                        | Description                            |
|--------|---------------------------------|----------------------------------------|
| POST   | `/api/attendance/`              | Mark/update attendance                 |
| GET    | `/api/attendance/`              | List all (filter by employee_id, date) |
| GET    | `/api/attendance/{id}`          | Get single record                      |
| DELETE | `/api/attendance/{id}`          | Delete record                          |

Interactive docs available at: `http://localhost:8000/docs`

---

## Run Locally

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/hrms-backend.git
cd hrms-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (optional for local - SQLite is default)
cp .env.example .env

# 5. Start the server
python run.py
# OR
uvicorn app.main:app --reload --port 8000
```

API will be live at: **http://localhost:8000**
Swagger docs at: **http://localhost:8000/docs**

---

## Deploy on Render (Recommended – Free Tier)

### Step-by-Step

#### 1. Push code to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/hrms-backend.git
git push -u origin main
```

#### 2. Create a Render account
- Go to https://render.com and sign up (free)

#### 3. Create a PostgreSQL Database
- Dashboard → **New** → **PostgreSQL**
- Name: `hrms-db`
- Plan: **Free**
- Click **Create Database**
- Copy the **Internal Database URL** (you'll need it)

#### 4. Create a Web Service
- Dashboard → **New** → **Web Service**
- Connect your GitHub repo
- Fill in:
  | Field         | Value                                              |
  |---------------|----------------------------------------------------|
  | Name          | `hrms-lite-api`                                    |
  | Runtime       | `Python 3`                                         |
  | Build Command | `pip install -r requirements.txt`                  |
  | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
  | Plan          | **Free**                                           |

#### 5. Add Environment Variable
- In the Web Service → **Environment** tab
- Add:
  ```
  Key:   DATABASE_URL
  Value: <paste the Internal Database URL from step 3>
  ```
  > Make sure the URL starts with `postgresql://` (the app auto-fixes `postgres://`)

#### 6. Deploy
- Click **Create Web Service**
- Render will build and deploy automatically (takes ~2 min)
- Your API URL will be: `https://hrms-lite-api.onrender.com`

#### 7. Verify
Visit: `https://hrms-lite-api.onrender.com/health`
Expected: `{"status": "ok"}`

---

## Deploy on Railway (Alternative)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add PostgreSQL plugin
railway add --plugin postgresql

# 5. Set env variable (Railway auto-sets DATABASE_URL for linked plugins)

# 6. Deploy
railway up
```

---

## Validations & Error Handling

| Scenario                        | HTTP Status | Message                                   |
|---------------------------------|-------------|-------------------------------------------|
| Missing required field          | 422         | Pydantic validation error detail          |
| Invalid email format            | 422         | `value is not a valid email address`      |
| Duplicate employee_id           | 409         | `Employee with ID '...' already exists.`  |
| Duplicate email                 | 409         | `Employee with email '...' already exists`|
| Employee not found              | 404         | `Employee not found.`                     |
| Attendance record not found     | 404         | `Attendance record not found.`            |
| Mark attendance (same day)      | 200         | Updates existing record automatically     |

---

## Assumptions & Limitations

- Single admin user — no authentication/authorization
- SQLite used for local dev; PostgreSQL recommended for production
- Marking attendance for the same employee + date updates the existing record
- Free Render instances spin down after 15 min of inactivity (cold start ~30s)
- Leave management, payroll, and roles are out of scope

---

## License
MIT
