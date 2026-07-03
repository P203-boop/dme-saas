# DME SaaS

FastAPI backend plus Streamlit dashboard for a simple DME operations workflow:
patients, orders, eligibility checks, and order routing.

## Project Structure

```text
app/
  main.py
  auth.py
  database.py
  models.py
  schemas.py
  routers/
    patients.py
    orders.py
    process.py
  services/
    eligibility.py
dashboard.py
tests/
  test_app.py
```

## Local Setup

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Run the Streamlit dashboard in another terminal:

```powershell
streamlit run dashboard.py
```

## Tests

Run the test suite:

```powershell
python -m unittest discover -s tests -v
```

## Environment Variables

Backend/API:

```text
SECRET_KEY=<long random secret>
DME_ADMIN_USERNAME=<admin username>
DME_ADMIN_PASSWORD=<admin password>
CORS_ORIGINS=<allowed frontend origin or * for testing>
```

Dashboard:

```text
DME_API_URL=https://dme-saas-r1ir.onrender.com
```

If admin variables are not set, local development falls back to:

```text
admin / admin123
```

## Render Deploy

FastAPI start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Health check URL:

```text
https://dme-saas-r1ir.onrender.com/
```

Expected response:

```json
{"message":"DME SaaS API Running"}
```

## Eligibility Rule

The current MVP eligibility check is intentionally simple:

```text
Insurance ID ending in 0, 2, 4, 6, 8 -> ROUTED_TO_TRANSPORT
Insurance ID ending in 1, 3, 5, 7, 9 -> FLAGGED
Blank or non-digit ending -> FLAGGED
```

Example routed test value:

```text
TEST-1002
```
