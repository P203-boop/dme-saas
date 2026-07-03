import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import authenticate_user
from app.database import Base
from app.routers.orders import create_order
from app.routers.patients import create_patient
from app.routers.process import process_order
from app.schemas import OrderCreate, PatientCreate
from app.services.eligibility import check_eligibility


class DmeSaasTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        self.engine = engine
        session_factory = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )
        self.db = session_factory()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_default_admin_login(self):
        self.assertIsNotNone(authenticate_user("admin", "admin123"))
        self.assertIsNone(authenticate_user("admin", "wrong-password"))

    def test_eligibility_rule(self):
        self.assertTrue(check_eligibility("INS-2468"))
        self.assertFalse(check_eligibility("INS-1357"))
        self.assertFalse(check_eligibility(""))

    def test_create_patient_and_order(self):
        patient = create_patient(
            PatientCreate(
                first_name="Ada",
                last_name="Lovelace",
                insurance_id="INS-2468",
            ),
            db=self.db,
        )

        order = create_order(
            OrderCreate(
                patient_id=patient.id,
                dme_code="WALKER",
                qty=1,
            ),
            db=self.db,
        )

        self.assertEqual(order.patient_id, patient.id)
        self.assertEqual(order.status, "NEW")

    def test_create_order_rejects_missing_patient(self):
        with self.assertRaises(HTTPException) as exc:
            create_order(
                OrderCreate(
                    patient_id="missing-patient",
                    dme_code="WALKER",
                    qty=1,
                ),
                db=self.db,
            )

        self.assertEqual(exc.exception.status_code, 404)
        self.assertEqual(exc.exception.detail, "Patient not found")

    def test_process_order_routes_eligible_patient(self):
        patient = create_patient(
            PatientCreate(
                first_name="Grace",
                last_name="Hopper",
                insurance_id="INS-2468",
            ),
            db=self.db,
        )
        order = create_order(
            OrderCreate(patient_id=patient.id, dme_code="CPAP", qty=1),
            db=self.db,
        )

        result = process_order(order.id, db=self.db)

        self.assertTrue(result["eligible"])
        self.assertEqual(result["status"], "ROUTED_TO_TRANSPORT")
        self.assertIsNone(result["flag_reason"])

    def test_process_order_flags_ineligible_patient(self):
        patient = create_patient(
            PatientCreate(
                first_name="Alan",
                last_name="Turing",
                insurance_id="INS-1357",
            ),
            db=self.db,
        )
        order = create_order(
            OrderCreate(patient_id=patient.id, dme_code="OXYGEN", qty=1),
            db=self.db,
        )

        result = process_order(order.id, db=self.db)

        self.assertFalse(result["eligible"])
        self.assertEqual(result["status"], "FLAGGED")
        self.assertEqual(result["flag_reason"], "INELIGIBLE")


if __name__ == "__main__":
    unittest.main()
