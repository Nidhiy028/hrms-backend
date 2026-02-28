from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check duplicate employee_id
    if db.query(models.Employee).filter(models.Employee.employee_id == payload.employee_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{payload.employee_id}' already exists."
        )
    # Check duplicate email
    if db.query(models.Employee).filter(models.Employee.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with email '{payload.email}' already exists."
        )

    employee = models.Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/", response_model=List[schemas.EmployeeWithStats])
def list_employees(db: Session = Depends(get_db)):
    employees = db.query(models.Employee).order_by(models.Employee.created_at.desc()).all()

    result = []
    for emp in employees:
        records = emp.attendance_records
        present = sum(1 for r in records if r.status == models.AttendanceStatus.present)
        absent = sum(1 for r in records if r.status == models.AttendanceStatus.absent)

        emp_dict = schemas.EmployeeWithStats(
            **{c.name: getattr(emp, c.name) for c in emp.__table__.columns},
            total_present=present,
            total_absent=absent,
            total_records=len(records)
        )
        result.append(emp_dict)

    return result


@router.get("/{employee_id}", response_model=schemas.EmployeeWithStats)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")

    records = emp.attendance_records
    present = sum(1 for r in records if r.status == models.AttendanceStatus.present)
    absent = sum(1 for r in records if r.status == models.AttendanceStatus.absent)

    return schemas.EmployeeWithStats(
        **{c.name: getattr(emp, c.name) for c in emp.__table__.columns},
        total_present=present,
        total_absent=absent,
        total_records=len(records)
    )


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")

    db.delete(emp)
    db.commit()
    return {"message": f"Employee '{emp.full_name}' deleted successfully."}


@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    from datetime import date

    total_employees = db.query(models.Employee).count()
    total_attendance = db.query(models.Attendance).count()
    today = date.today()

    present_today = db.query(models.Attendance).filter(
        models.Attendance.date == today,
        models.Attendance.status == models.AttendanceStatus.present
    ).count()

    absent_today = db.query(models.Attendance).filter(
        models.Attendance.date == today,
        models.Attendance.status == models.AttendanceStatus.absent
    ).count()

    dept_rows = db.query(
        models.Employee.department,
        func.count(models.Employee.id).label("count")
    ).group_by(models.Employee.department).all()

    departments = [{"department": row.department, "count": row.count} for row in dept_rows]

    return schemas.DashboardStats(
        total_employees=total_employees,
        total_attendance_records=total_attendance,
        present_today=present_today,
        absent_today=absent_today,
        departments=departments
    )
