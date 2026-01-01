# Macro Chef - Quick Start Guide

Get up and running with Macro Chef in 5 minutes!

## First-Time Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python scripts/db_setup.py
```

### 3. Populate Meal Library (28 meals)
```bash
python scripts/populate_meal_templates.py
```

### 4. Create Your Profile
```bash
python scripts/user_profile.py --create
```

You'll be asked:
- Name, age, sex
- Height (inches) and weight (lbs)
- Body fat % (optional but recommended)
- Goal: `cut`, `bulk`, `maintain`, or `recomp`
- Activity level: `sedentary`, `light`, `moderate`, `active`, `very_active`
- Training days per week (0-7)
- Cooking skill: `beginner`, `intermediate`, `advanced`
- Weekly grocery budget (USD)

Example:
```
Name: John
Age: 28
Sex: M
Height: 72 inches (6'0")
Weight: 180 lbs
Body fat: 15%
Goal: cut
Activity: moderate
Training days: 5
Cooking skill: intermediate
Weekly budget: $100
```

## Daily Workflow

### Morning Check-in
```bash
python scripts/claude_interface.py daily
```

This shows:
- Today's nutrition targets
- Current progress
- Expiring inventory items
- Budget status
- Next meal recommendation

### Log Your Meals

**Quick log:**
```bash
python scripts/meal_tracker.py --log \
  --name "Protein Oatmeal" \
  --calories 380 \
  --protein 30 \
  --carbs 48 \
  --fat 8 \
  --meal-time breakfast
```

**Interactive log** (searches meal templates):
```bash
python scripts/claude_interface.py log-meal
```

### Get Meal Recommendations
```bash
# Auto-detect next meal
python scripts/claude_interface.py recommend

# Specific meal
python scripts/meal_recommender.py --recommend dinner --count 5

# With constraints
python scripts/meal_recommender.py --recommend lunch --max-time 20 --budget 4.00
```

### Check Progress
```bash
# Dashboard overview
python scripts/claude_interface.py dashboard

# Today's progress
python scripts/meal_tracker.py --progress

# Weekly summary
python scripts/meal_tracker.py --weekly --days 7
```

## Weekly Planning

### Plan Your Week
```bash
python scripts/claude_interface.py plan-week
```

This will:
1. Generate 7-day meal plan optimized for your goals
2. Show nutrition summary
3. Estimate weekly cost
4. Offer to save the plan
5. Generate shopping list

### View Saved Plans
```bash
# List recent plans
python scripts/weekly_planner.py --list

# View specific plan
python scripts/weekly_planner.py --view 1

# Generate shopping list from saved plan
python scripts/weekly_planner.py --shopping-list 1
```

## Inventory & Shopping

### Add to Inventory
```bash
python scripts/inventory_manager.py --add \
  --name "Chicken breast" \
  --quantity 2.5 \
  --unit lbs \
  --category protein \
  --location freezer \
  --days-until-expire 30
```

### Check Inventory
```bash
# List all items
python scripts/inventory_manager.py --list

# Check expiring soon (7 days)
python scripts/inventory_manager.py --expiring --days 7

# Search
python scripts/inventory_manager.py --search chicken
```

### Shopping Lists
```bash
# Generate from meals (by template ID)
python scripts/shopping_list.py --generate 1 2 3 --servings 1 2 1

# View shopping history
python scripts/shopping_list.py --history --days 30
```

## Budget Tracking

### Weekly Budget
```bash
python scripts/budget_tracker.py --weekly
```

Shows:
- This week's spending vs budget
- Number of shopping trips
- Category breakdown

### Monthly Budget
```bash
python scripts/budget_tracker.py --monthly
```

### Spending Trends
```bash
# Last 4 weeks
python scripts/budget_tracker.py --trends --weeks 4

# Category breakdown
python scripts/budget_tracker.py --categories --days 30

# Price history for item
python scripts/budget_tracker.py --price-history "chicken"
```

## Analytics & Insights

### Progress Report
```bash
python scripts/analytics.py --progress-report --days 30
```

Shows:
- Body composition changes
- Nutrition adherence (avg %)
- Macro consistency
- Calorie trends

### Micronutrient Analysis
```bash
# Check for deficiencies
python scripts/analytics.py --deficiencies --days 7 --save-alerts

# View active alerts
python scripts/analytics.py --alerts
```

Tracks 9 key micronutrients:
- Vitamin D, C, A
- Calcium, Iron, Magnesium, Potassium, Zinc
- Omega-3 fatty acids

## Tips & Best Practices

### 1. Start Simple
- Use the unified CLI (`claude_interface.py`) for common tasks
- Log meals consistently for accurate tracking
- Check inventory before shopping

### 2. Weekly Routine
- **Sunday**: Plan the week, generate shopping list
- **Monday**: Go shopping, update inventory
- **Daily**: Morning check-in, log meals, track progress
- **Weekly**: Review progress report, adjust goals

### 3. Meal Prep
- Filter for `batch-friendly` meals:
  ```bash
  # Search meal templates
  python scripts/meal_tracker.py --history --days 90
  ```
- Cook 2-3 days worth on Sunday
- Update inventory after prep

### 4. Budget Management
- Set realistic weekly budget ($75-150 for one person)
- Check trends monthly
- Look for budget-friendly meals (tagged `budget`)

### 5. Body Metrics
```bash
# Log weight weekly
python scripts/user_profile.py --log-metrics --weight 178 --body-fat 14.5

# View progress
python scripts/user_profile.py --progress --days 30
```

### 6. Adjust Goals
- Cutting too fast? Lower deficit (aim for 1-2 lbs/week)
- Not gaining? Increase calories by 200-300
- Update profile every 2-4 weeks

## Troubleshooting

### No meal recommendations?
- Check that meal templates exist: `python scripts/populate_meal_templates.py`
- Verify daily targets: `python scripts/nutrition_calculator.py --view`

### Database issues?
```bash
# Re-initialize (WARNING: deletes all data)
python scripts/db_setup.py

# Backup first
cp database/meal_planner.db database/backups/meal_planner_backup_$(date +%Y%m%d).db
```

### Inventory not updating?
```bash
# Use item after logging meal
python scripts/inventory_manager.py --use ITEM_ID --amount 0.5
```

## Available Meal Templates

The system includes 28 pre-loaded meals:

**Breakfasts** (7):
- Protein Oatmeal ($1.50)
- Scrambled Eggs & Toast ($1.20)
- Greek Yogurt Bowl ($2.00)
- Breakfast Burrito ($2.50)
- Protein Pancakes ($1.80)
- Egg White Omelet ($2.20)
- Peanut Butter Banana Smoothie ($1.60)

**Lunches** (7):
- Chicken & Rice Bowl ($3.50)
- Turkey Sandwich ($2.80)
- Tuna Salad ($2.50)
- Chicken Quesadilla ($3.00)
- Beef & Veggie Stir Fry ($4.00)
- Pasta Salad with Chicken ($3.20)
- Protein Bowl ($4.50)

**Dinners** (7):
- Grilled Salmon & Vegetables ($6.50)
- Spaghetti & Meatballs ($3.80)
- Chicken Fajitas ($4.20)
- Turkey Chili ($3.50)
- Pork Chop with Sweet Potato ($5.00)
- Shrimp Stir Fry ($5.50)
- Beef Tacos ($4.00)

**Snacks** (7):
- Protein Shake ($1.20)
- Apple with Peanut Butter ($0.80)
- Cottage Cheese & Berries ($1.50)
- Trail Mix ($1.00)
- Protein Bar ($2.00)
- Hummus & Veggies ($1.20)
- Hard Boiled Eggs ($0.60)

## Next Steps

1. **Add your own recipes:**
   - Study the meal templates in the database
   - Add custom meals via SQL or create helper script

2. **API Integration** (optional):
   - Get Spoonacular API key: https://spoonacular.com/food-api
   - Add to `.env` file
   - Search recipes: `python scripts/spoonacular_api.py --search "chicken"`

3. **Customize:**
   - Modify RDA values in `config/config.py`
   - Adjust recommendation scoring in `meal_recommender.py`
   - Add dietary restrictions to your profile

## Support

- Report issues: https://github.com/anthropics/claude-code/issues
- Full documentation: See README.md
- Technical spec: See SPECIFICATION.md

---

**Remember:** Consistency is key! Log meals daily, track your progress weekly, and adjust your approach monthly. The system gets smarter as you use it more.
