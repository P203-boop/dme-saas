from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
import uuid

from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    insurance_id = Column(String)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String)
    dme_code = Column(String)
    qty = Column(Integer)
    status = Column(String, default="NEW")
    flag_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)