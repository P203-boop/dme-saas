from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Order
from schemas import OrderCreate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/orders")
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):

    order = Order(
        patient_id=payload.patient_id,
        dme_code=payload.dme_code,
        qty=payload.qty
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
