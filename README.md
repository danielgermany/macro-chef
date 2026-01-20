# Macro Chef - AI-Powered Meal Planning System

An intelligent meal planning system that helps you maintain nutrition goals, minimize food waste, support athletic performance, and manage grocery budgets through smart recommendations and comprehensive tracking.

## Quick Links

- **[Complete Documentation](DOCUMENTATION.md)** - Full documentation with all guides, specs, and details
- **[Quick Start Guide](DOCUMENTATION.md#quick-start-guide)** - Get started in 5 minutes
- **[Web Migration Plan](MIGRATION_PLAN.md)** - FastAPI + React migration details
- **[Technical Specification](SPECIFICATION.md)** - Complete technical specs

## Features

### Core Functionality
- **Smart Nutrition Tracking**: Automatically calculate daily macro and micronutrient targets
- **Intelligent Meal Recommendations**: AI-powered suggestions based on remaining macros, inventory, budget, and preferences
- **Meal Logging & Progress**: Track meals throughout the day with real-time progress vs targets
- **Inventory Management**: Track food on hand with expiration alerts
- **Budget Tracking**: Monitor grocery spending with weekly/monthly summaries
- **Body Composition Tracking**: Log weight, body fat %, and measurements

### Advanced Features
- **Online Recipe Search**: Automatically searches Spoonacular when local database has <5 meals
- **Price Cross-Referencing**: Hybrid pricing using 70% shopping history + 30% API
- **Nutrition Validation**: Cross-validates online recipes with USDA database
- **Weekly Meal Planning**: Generate complete 7-day meal plans
- **Shopping List Generation**: Smart shopping lists that check inventory
- **Micronutrient Analysis**: Detect deficiencies in 9 key micronutrients

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/db_setup.py

# Start backend server
cd backend
uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 to access the web application.

For detailed setup instructions, see the [Quick Start Guide](DOCUMENTATION.md#quick-start-guide).

## Tech Stack

- **Database**: SQLite (13 tables)
- **Backend**: Python 3.8+
- **APIs**: Spoonacular (recipes/nutrition), USDA FoodData Central (nutrition)
- **Interface**: CLI + Web (FastAPI + React)

## Documentation

All documentation has been consolidated into a single file for easy access:

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete documentation including:
  - Project Overview
  - Quick Start Guide
  - Technical Specification
  - Web Migration Plan
  - Testing Guide
  - Implementation Details
  - Features & Integrations
  - Backend/Frontend Setup

For detailed technical information:
- **[MIGRATION_PLAN.md](MIGRATION_PLAN.md)** - Complete web migration plan with API specs
- **[SPECIFICATION.md](SPECIFICATION.md)** - Complete database schema and technical specs

## Project Status

### Completed
- Core functionality (nutrition tracking, meal recommendations, inventory)
- Online recipe integration
- Web backend (FastAPI) - Phase 1-2 complete
- Web frontend (React) - Phase 3-4 complete

### In Progress
- Web authentication & multi-user support
- Testing & deployment

## License

MIT

## Contributing

This is a personal project, but suggestions and feedback are welcome!
