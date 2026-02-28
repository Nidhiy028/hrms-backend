from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List
from app.models import AttendanceStatus


# ── Employee Schemas ──────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

    @field_validator("employee_id", "full_name", "department")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty or whitespace")
        return v


class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeWithStats(EmployeeResponse):
    total_present: int = 0
    total_absent: int = 0
    total_records: int = 0


# ── Attendance Schemas ────────────────────────────────────────────────────────

class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: AttendanceStatus


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    status: AttendanceStatus
    created_at: datetime
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Dashboard Schema ──────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_employees: int
    total_attendance_records: int
    present_today: int
    absent_today: int
    departments: List[dict]
