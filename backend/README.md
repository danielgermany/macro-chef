# Macro Chef Backend API

FastAPI backend for Macro Chef meal planning application.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

3. Visit API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & environment
│   ├── database.py          # Database connection
│   ├── routers/             # API route handlers
│   ├── schemas/             # Pydantic models
│   └── services/            # Business logic (links to scripts/)
└── tests/                   # API tests
```

## Environment Variables

Create a `.env` file in the project root:

```env
SPOONACULAR_API_KEY=your_key_here
USDA_API_KEY=your_key_here
DATABASE_URL=sqlite:///../database/meal_planner.db
```

## Development

The backend uses the existing `scripts/` directory for business logic, so no changes are needed to your existing code. The FastAPI layer simply wraps your existing managers with REST endpoints.
