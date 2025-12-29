# Macro Chef - AI-Powered Meal Planning System

An intelligent meal planning system that helps you maintain nutrition goals, minimize food waste, support athletic performance, and manage grocery budgets.

## Features

- **Smart Nutrition Tracking**: Automatically calculate daily macro and micronutrient targets based on your body metrics and goals
- **Meal Planning**: Get personalized meal recommendations based on your preferences, inventory, and budget
- **Inventory Management**: Track food on hand and get alerts before items expire
- **Budget Tracking**: Monitor grocery spending and stay within your weekly/monthly budget
- **Progress Monitoring**: Track body composition changes and nutrition adherence over time
- **Recipe Library**: Store and rate your favorite recipes with complete nutrition data

## Tech Stack

- **Database**: SQLite
- **Backend**: Python 3.8+
- **APIs**: Spoonacular (primary), USDA FoodData Central (backup)
- **Interface**: Claude AI (natural language)

## Project Structure

```
macro-chef/
├── database/           # SQLite database and backups
├── config/            # Configuration files
├── scripts/           # Python scripts for core functionality
├── data/              # JSON data files and caches
└── tests/             # Unit tests
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd macro-chef
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
# Get Spoonacular API key: https://spoonacular.com/food-api
```

### 5. Initialize the database

```bash
python scripts/db_setup.py
```

### 6. Create your user profile

```bash
python scripts/user_profile.py --create
```

## Usage

### Create User Profile

```bash
python scripts/user_profile.py --create
```

### View User Profile

```bash
python scripts/user_profile.py --view
```

### Log Body Metrics

```bash
python scripts/user_profile.py --log-metrics --weight 180 --body-fat 15
```

### Generate Daily Nutrition Targets

```bash
python scripts/nutrition_calculator.py --generate
```

### View Today's Targets

```bash
python scripts/nutrition_calculator.py --view
```

## Key Principles

- **Cheap**: Budget-conscious recommendations
- **Fast**: Quick meal suggestions and prep
- **Easy**: Simple recipes, minimal complexity
- **Nutritious**: Macro and micronutrient optimization

## Development Roadmap

### Phase 1: Foundation (MVP)
- [x] Project setup and database initialization
- [ ] User profile management
- [ ] Nutrition target calculation
- [ ] Meal tracking
- [ ] Basic inventory management

### Phase 2: Intelligence
- [ ] Meal recommendation engine
- [ ] API integration (Spoonacular, USDA)
- [ ] Shopping list generation
- [ ] Budget tracking

### Phase 3: Optimization
- [ ] Weekly meal planning
- [ ] Micronutrient deficiency alerts
- [ ] Analytics and insights
- [ ] Batch cooking optimization

## License

MIT

## Contributing

This is a personal project, but suggestions and feedback are welcome.
