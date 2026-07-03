from pydantic import BaseModel
from pydantic import Field


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    insurance_id: str


class OrderCreate(BaseModel):
    patient_id: str
    dme_code: str
    qty: int = Field(gt=0)
