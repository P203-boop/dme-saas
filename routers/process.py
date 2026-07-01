from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Order, Patient
from services.eligibility import check_eligibility

router = APIRouter()


@router.post("/process/{order_id}")
def process_order(order_id: str, db: Session = Depends(get_db)):

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    patient = db.query(Patient).filter(Patient.id == order.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    eligible = check_eligibility(patient.insurance_id)

    if eligible:
        order.status = "ROUTED_TO_TRANSPORT"
        order.flag_reason = None
    else:
        order.status = "FLAGGED"
        order.flag_reason = "INELIGIBLE"

    db.commit()

    return {
        "order_id": order.id,
        "status": order.status,
        "eligible": eligible,
        "flag_reason": order.flag_reason
    }
