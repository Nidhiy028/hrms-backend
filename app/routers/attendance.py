from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(payload: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    # Verify employee exists
    employee = db.query(models.Employee).filter(models.Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")

    # Prevent duplicate attendance for same day
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == payload.employee_id,
        models.Attendance.date == payload.date
    ).first()

    if existing:
        # Update existing record instead of error
        existing.status = payload.status
        db.commit()
        db.refresh(existing)
        record = existing
    else:
        record = models.Attendance(**payload.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)

    return schemas.AttendanceResponse(
        **{c.name: getattr(record, c.name) for c in record.__table__.columns},
        employee_name=employee.full_name,
        employee_code=employee.employee_id
    )


@router.get("/", response_model=List[schemas.AttendanceResponse])
def list_attendance(
    employee_id: Optional[int] = Query(None, description="Filter by employee DB id"),
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Attendance).join(models.Employee)

    if employee_id:
        query = query.filter(models.Attendance.employee_id == employee_id)
    if date_filter:
        query = query.filter(models.Attendance.date == date_filter)

    records = query.order_by(models.Attendance.date.desc()).all()

    result = []
    for rec in records:
        result.append(schemas.AttendanceResponse(
            **{c.name: getattr(rec, c.name) for c in rec.__table__.columns},
            employee_name=rec.employee.full_name,
            employee_code=rec.employee.employee_id
        ))
    return result


@router.get("/{attendance_id}", response_model=schemas.AttendanceResponse)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    return schemas.AttendanceResponse(
        **{c.name: getattr(rec, c.name) for c in rec.__table__.columns},
        employee_name=rec.employee.full_name,
        employee_code=rec.employee.employee_id
    )


@router.delete("/{attendance_id}", status_code=status.HTTP_200_OK)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    db.delete(rec)
    db.commit()
    return {"message": "Attendance record deleted successfully."}
