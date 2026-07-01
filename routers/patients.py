from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Patient
from schemas import PatientCreate

router = APIRouter()


@router.post("/patients")
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):

    patient = Patient(
        first_name=payload.first_name,
        last_name=payload.last_name,
        insurance_id=payload.insurance_id
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()
