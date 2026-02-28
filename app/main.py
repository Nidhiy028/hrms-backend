from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import employees, attendance

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HRMS Lite API",
    description="Human Resource Management System - Lite Version",
    version="1.0.0"
)

# CORS - allow all origins for assignment purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])


@app.get("/", tags=["Health"])
def root():
    return {"message": "HRMS Lite API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
