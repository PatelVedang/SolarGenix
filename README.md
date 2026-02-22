# Authentication API

A Django-based Authentication API featuring secure user registration, login, and password management, utilizing **Supabase** (PostgreSQL) for the database and **Twilio** for SMS-based OTP verification.

## Features
- **User Authentication**: Register, Login, Logout.
- **OTP Verification**: Secure SMS-based One-Time Passwords via Twilio.
- **Database**: Managed PostgreSQL via Supabase.
- **Local Dev**: Docker-free local development environment.

## Prerequisites
- **Python 3.12**+
- **Supabase Account**: A project with a PostgreSQL database.
- **Twilio Account**: For sending SMS OTPs.

## Installation

### Unix (Linux / macOS)
1. **Run the installation script**:
   ```bash
   ./scripts/install.sh
   ```
   This script will:
   - Install system dependencies (JQ, Ruff).
   - Set up a Python 3.12 virtual environment.
   - Install Python dependencies.
   - Optionally create your `.env` file.

### Windows
1. **Install Python 3.12**: Ensure Python is added to your PATH.
2. **Create a Virtual Environment**:
   ```powershell
   python -m venv env
   ```
3. **Activate the Environment**:
   ```powershell
   .\env\Scripts\activate
   ```
4. **Install Dependencies**:
   ```powershell
   pip install -r app\requirements.txt
   ```
5. **Setup Environment Variables**:
   ```powershell
   copy app\.env_example app\.env
   ```

## Configuration

1. Open `app/.env` (created during installation).
2. **Supabase Database**:
   Fill in your Supabase connection details. It is recommended to use the **Session Pooler (port 6543)**.
   ```ini
   SQL_DATABASE=<your_db_name>
   SQL_USER=postgres
   SQL_PASSWORD=<your_db_password>
   SQL_DATABASE_HOST=<your_supabase_host>
   SQL_DATABASE_PORT=6543
   ```
3. **Twilio Credentials**:
   Add your Twilio API keys for OTP functionality.
   ```ini
   TWILIO_ACCOUNT_SID=<your_sid>
   TWILIO_AUTH_TOKEN=<your_token>
   TWILIO_PHONE_NUMBER=<your_twilio_number>
   ```

## Running the Application

1. **Apply Migrations**:
   Run the migration script to set up your database schema.
   ```bash
   ./scripts/apply_migrations.sh
   ```
   *Note: This script supports both Windows (Git Bash/PowerShell) and Unix environments.*

2. **Start the Server**:
   ```bash
   python app/manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

## API Documentation
Once the server is running, you can access the Swagger documentation at:
- `http://127.0.0.1:8000/api/schema/swagger-ui/`

---

## Appendix: Utilities

### Filter Model
The `filter_model` function is a utility designed to filter a Django `QuerySet` based on dynamic query parameters provided through a `QueryDict`.

#### Function Signature
```python
def filter_model(
    query_params: QueryDict, queryset: QuerySet[Model], model: Type[Model]
) -> QuerySet[Model]:
    """
    Filter the given queryset based on the provided query parameters.
    """
```

#### Supported Query Parameters
- **`search_fields`**: Comma-separated list of fields to search against.
- **`search`**: Case-insensitive search string.
- **`sort`**: Comma-separated fields to sort by (prefix with `-` for descending).
- **`select`**: Comma-separated list of fields to return.

#### Django Lookups
Supports standard lookups like `__exact`, `__icontains`, `__gt`, `__lte`, `__in`, and custom `__not_in`.
