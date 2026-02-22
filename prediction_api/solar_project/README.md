# Solar Prediction & Intelligence API

A comprehensive REST API service for solar energy optimisation and intelligent data retrieval.

## Core Features

- **Solar Generation Forecast**: 10-day predictions based on location, panel condition, and real-time weather data.
- **Bill Optimization (Slab)**: Calculate required solar capacity to reduce monthly bills using Indian slab-based tariffs. No ML required.
- **Bill Prediction**: Bi-monthly electricity bill forecasting using dual-model routing (High Usage vs. General).
- **Intelligent Chatbot (RAG)**: Multi-tenant hybrid RAG system with fuzzy matching, synonym expansion, and query expansion.
- **PDF Ingestion**: Advanced document processing for extracting intelligence from PDF files.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6 + Django REST Framework |
| ML Models | scikit-learn (gradient boosting & regression) |
| Database | Supabase (PostgreSQL + pgvector) |
| AI / LLM | Groq (LLAMA 3.1 8B), Nomic Embedders |
| Data Sources | Open-Meteo, OpenStreetMap Nominatim |
| Documentation | Swagger UI (`drf-yasg`) |

---

## Quickstart

### 1. Prerequisites
- Python 3.10+
- pip + virtualenv

### 2. Installation
```bash
git clone <repo-url>
cd solar_project

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 3. Environment Setup
```bash
python setup_env.py   # creates .env from .env.example
# open .env and fill in your credentials
```

### 4. Run the Server
```bash
python manage.py runserver 5000
```

Swagger UI: `http://127.0.0.1:5000/solar_generation/swagger/`

---

## API Reference

All endpoints are prefixed with `/solar_generation/`.

### 1) Solar Generation Prediction
| | |
|--|--|
| **Path** | `GET /solar_generation/predict-production/` |
| **Params** | `pincode` (India), `sunlight_time` (hrs), `panels` (count), `panel_condition` (good/average/bad) |

---

### 2) Bill Optimization — Slab Tariff ✨ *New*
| | |
|--|--|
| **Path** | `POST /solar_generation/solar/bill-optimization-slab/` |
| **Tag** | Solar Optimisation |
| **Auth** | None |

**Request body:**
```json
{
  "current_bill": 2000,
  "target_bill": 500,
  "location": "Surat",
  "has_solar": false,
  "solar_capacity_kw": null
}
```

**Response `200`:**
```json
{
  "current_units": 368.43,
  "target_units": 135.4,
  "units_to_offset": 233.03,
  "recommended_solar_kw": 1.942,
  "recommended_panels": 4,
  "estimated_monthly_generation": 233.04
}
```

**Tariff slabs used (₹/unit):**

| Slab | Rate |
|------|------|
| 0 – 50 units | ₹ 3.00 |
| 51 – 100 units | ₹ 3.50 |
| 101 – 200 units | ₹ 5.00 |
| 201 + units | ₹ 7.00 |

> **Assumptions**: 1 kW solar → 120 units / month · Panel size = 540 W

**Logic:**
- `has_solar = false` → `required_kw = (current_units − target_units) / 120`
- `has_solar = true` → `required_kw = (current_units − existing_generation − target_units) / 120`

---

### 3) Electricity Bill Prediction (ML)
| | |
|--|--|
| **Path** | `GET /solar_generation/predict-bill/` |
| **Params** | `consumption_history` (list of 6 numbers), `cycle_index` (1–6) |

---

### 4) Intelligence Chatbot
| | |
|--|--|
| **Path** | `POST /solar_generation/chatbot/ask/` |
| **Body** | `{"question": "How efficient are the panels?", "tenant_id": "client_001"}` |

---

### 5) PDF Ingestion
| | |
|--|--|
| **Path** | `POST /solar_generation/chatbot/ingest-pdf/` |
| **Format** | Multipart form-data |
| **Fields** | `pdf_file` (File), `tenant_id` (String) |

---

### 6) Delete Knowledge Base
| | |
|--|--|
| **Path** | `POST /solar_generation/chatbot/delete-knowledge-base/` |
| **Body** | `{"tenant_id": "client_001"}` |

---

## Documentation
- **Swagger UI**: `http://127.0.0.1:5000/solar_generation/swagger/`
- **ReDoc**: `http://127.0.0.1:5000/solar_generation/redoc/`

## Deployment & Security
- All DB connections use `sslmode=require`.
- Default Django Admin and Auth tables removed to keep Supabase schema lean.
- Cross-origin isolation configured: `CORS_ALLOW_ALL_ORIGINS = True` (restrict in production).
- No authentication on endpoints by default — add token auth before exposing publicly.
