# AMIN JOON Backend

Backend API for the AMIN JOON VPN Management System.

## Requirements

- Python 3.11 or newer
- pip

## Installation

Enter the backend directory:

```bash
cd backend
Create a virtual environment:
python -m venv .venv


Activate it on Linux:
source .venv/bin/activate


Install dependencies:
pip install -r requirements.txt


Environment Configuration
Create a .env file based on .env.example.

Generate a unique Fernet key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


Set the generated key as NODE_CREDENTIALS_KEY in .env.

Never commit .env or share its contents.
Database
Initialize or update the database schema:
alembic upgrade head


Run the API
uvicorn app.main:app --host 0.0.0.0 --port 8000


API documentation:

/docs

Health check:

/health
Development and Testing
Install development dependencies:
pip install -r requirements-dev.txt


Run all tests:
pytest


Security
- Keep .env private.
- Never expose agent tokens in API responses.
- Use HTTPS in production.
- Do not expose Node Agents directly over public HTTP.

پیام ثبت تغییرات:

`Update backend testing documentation`
