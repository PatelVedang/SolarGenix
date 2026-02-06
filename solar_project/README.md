# Solar Prediction & Intelligence API

A comprehensive REST API service for solar energy optimization and intelligent data retrieval.

## Core Features
- **Solar Generation Forecast**: 10-day predictions based on location, panel condition, and real-time weather data.
- **Bill Prediction**: Bi-monthly electricity bill forecasting using dual-model routing (High Usage vs. General).
- **Intelligent Chatbot (RAG)**: Multi-tenant hybrid RAG system with fuzzy matching, synonym expansion, and query expansion.
- **Web Crawler**: Selenium-based automated ingestion for JavaScript-heavy websites.
- **PDF Ingestion**: Advanced document processing for extracting intelligence from PDF files.

## Tech Stack
- **Framework**: Django + Django REST Framework
- **Models**: scikit-learn (gradient boosting & regression)
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI/LLM**: Groq (LLAMA 3.1 8B), Nomic Embedders
- **Data Sources**: Open-Meteo, OpenStreetMap Nominatim
- **Documentation**: Swagger UI (drf-yasg)

## Quickstart

### 1. Prerequisites
- Python 3.10+
- Pip and virtualenv

### 2. Installation
```bash
# Clone the repository
git clone <repo-url>
cd solar_project

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Run the setup script to initialize your `.env` file:
```bash
python setup_env.py
```
This will create a `.env` file from `.env.example`. Open it and fill in your actual credentials.

### 4. Running the Server
```bash
python manage.py runserver 5000
```
Documentation available at: `http://127.0.0.1:5000/solar_generation/swagger/`

---

## API Reference

### 1) Solar Generation Prediction
- **Path**: `/solar_generation/predict-production/`
- **Method**: GET
- **Params**: `pincode` (India), `sunlight_time` (hrs), `panels` (count), `panel_condition` (good/average/bad).

### 2) Electricity Bill Prediction
- **Path**: `/solar_generation/predict-bill/`
- **Method**: GET
- **Params**: `consumption_history` (list of 6 numbers), `cycle_index` (1-6).

### 3) Intelligence Chatbot
- **Path**: `/solar_generation/chatbot/ask/`
- **Method**: POST
- **Body**: `{"question": "How efficient are the solar panels?", "tenant_id": "client_001"}`
- **Features**: Hybrid retrieval combining vector similarity and fuzzy keyword search.

### 4) Website Crawler
- **Path**: `/solar_generation/chatbot/crawl/`
- **Method**: POST
- **Body**: `{"website_url": "https://example-solar.com", "tenant_id": "client_001"}`
- **Features**: Headless Selenium processing for deep indexing.

### 5) PDF Ingestion
- **Path**: `/solar_generation/chatbot/ingest-pdf/`
- **Method**: POST
- **Format**: Multipart Form-data
- **Fields**: `pdf_file` (File), `tenant_id` (String)

---

## Documentation
- **Swagger UI**: `/solar_generation/swagger/`
- **ReDoc**: `/solar_generation/redoc/`

## Deployment & Security
- Default Django Admin and Auth tables are removed to optimize Supabase schema.
- All connections use `sslmode=require`.
- Cross-origin isolation configured for safe API access.
