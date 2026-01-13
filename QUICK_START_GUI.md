# Macro Chef GUI - Quick Start Guide

##  5-Minute Setup

### Step 1: Launch the GUI (30 seconds)

```bash
# macOS/Linux
./launch_gui.sh

# Windows
launch_gui.bat

# Or directly:
python3 gui_app.py
```

### Step 2: Create Your Profile (2 minutes)

1. Click the **" Profile"** tab
2. Fill in your information:
   - Name: Your name
   - Age: Your age
   - Sex: Male or Female
   - Height: In inches (5'10" = 70 inches)
   - Weight: In pounds
   - Body Fat %: Optional, for more accurate calculations
   - Goal: Choose bulk/cut/maintain/recomp
   - Activity: How active you are
   - Training Days: How many days per week you train
   - Budget: Weekly food budget

3. Click **" Save Profile"**
4. Click **" Generate Targets"**

 You now have personalized daily nutrition targets!

### Step 3: View Your Dashboard (30 seconds)

1. Click the **" Dashboard"** tab
2. See your daily targets:
   - Total calories
   - Protein, carbs, fat, fiber
   - Quick stats

### Step 4: Search Some Recipes (2 minutes)

1. Click the **" Search Recipes"** tab
2. Type what you want (e.g., "chicken breast")
3. Adjust filters if needed:
   - Max Calories
   - Min Protein
   - Max Prep Time
4. Click **" Search"**

 Browse results and save favorites!

##  Common Tasks

### Add Food to Inventory

1. Go to **" Inventory"** tab
2. Fill in the form:
   - Item Name (e.g., "Chicken Breast")
   - Quantity (e.g., 2.5)
   - Unit (lbs/oz/g/kg/count/cups)
   - Category (protein/carbs/etc.)
   - Location (fridge/freezer/pantry)
   - Days Until Expiry
3. Click **" Add Item"**

### Get Meal Recommendation

1. Make sure you have:
   - Profile created 
   - Targets generated 
   - Some meals in database 
2. Go to **" Meals"** tab
3. Click **" Get Recommendation"**
4. See personalized suggestion!

### Update Your Weight

1. Go to **" Profile"** tab
2. Update weight value
3. Click **" Save Profile"**
4. Click **" Generate Targets"** to recalculate

### Search with Filters

Perfect for finding:
- **High Protein Meals**: Min Protein = 40g
- **Quick Meals**: Max Time = 20 min
- **Low Calorie**: Max Calories = 400
- **Dinner Ideas**: Max Calories = 800, Min Protein = 40g

##  Tips & Tricks

### For Best Results:

1. **Generate targets daily or after profile changes**
   - Keeps calculations accurate
   - Reflects current goals

2. **Search and save recipes regularly**
   - Build your meal database
   - Better recommendations over time

3. **Keep inventory updated**
   - Prevents food waste
   - Enables smart recommendations

4. **Use realistic values**
   - Accurate targets require honest data
   - Update weight weekly

### Shortcuts:

- **Tab**: Navigate between fields
- **Enter**: Submit forms
- **Refresh buttons**: Update data without restarting

### Understanding Your Targets:

**Bulk** (Muscle gain):
- Calories: TDEE + 300
- Protein: 1.0g per lb bodyweight
- Focus: Gradual weight gain

**Cut** (Fat loss):
- Calories: TDEE - 500
- Protein: 1.2g per lb (preserve muscle)
- Focus: Sustainable deficit

**Maintain** (Maintenance):
- Calories: TDEE (no change)
- Protein: 0.8g per lb
- Focus: Consistency

**Recomp** (Body recomposition):
- Calories: TDEE (maintenance)
- Protein: 1.1g per lb (elevated)
- Focus: Build muscle, lose fat simultaneously

##  Troubleshooting

### "No user profile loaded"
→ Go to Profile tab, fill information, click Save

### "Please generate targets first"
→ Go to Profile tab, click " Generate Targets"

### "No suitable meals found"
→ Search recipes to add meals to database

### Search returns no results
→ Check:
- Internet connection
- API keys in .env file
- Filters aren't too restrictive
- API quota not exceeded (150 free/day)

### GUI looks weird
→ Update to latest tkinter or try different Python version

### Can't add inventory
→ Ensure database initialized: `python3 scripts/db_setup.py`

##  Understanding the Dashboard

### Daily Targets Section:
```
═══════════════════════════════════════
  TODAY'S NUTRITION TARGETS
═══════════════════════════════════════

   Calories:      2,800 kcal

  MACRONUTRIENTS:
    • Protein:      180g
    • Carbs:        350g
    • Fat:          78g
    • Fiber:        39g
```

This shows what you should eat today to reach your goal.

### Quick Stats:
- **Saved Meals**: Number of recipes in your database
- **Inventory Items**: Foods you currently have
- **Goal**: Your current fitness goal
- **Activity Level**: How active you are

##  Next Steps

### After Setup:

1. **Explore All Tabs**
   - Dashboard: Daily overview
   - Profile: Manage settings
   - Meals: Browse and recommend
   - Inventory: Track food
   - Search: Find recipes

2. **Build Your Database**
   - Search 10-20 recipes you like
   - Add current inventory
   - Save favorites

3. **Daily Routine**
   - Morning: Check dashboard
   - Before meals: Get recommendation
   - After shopping: Update inventory
   - Weekly: Update weight

4. **Advanced Features** (CLI)
   - Weekly meal planning
   - Shopping list generation
   - Progress analytics
   - Micronutrient analysis

See [GUI_FEATURES.md](GUI_FEATURES.md) for detailed documentation.

##  Need Help?

1. **Check Documentation**
   - [GUI_README.md](GUI_README.md) - Full GUI guide
   - [GUI_FEATURES.md](GUI_FEATURES.md) - Feature details
   - [README.md](README.md) - Main documentation

2. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

3. **Check Logs**
   - Status bar shows current operations
   - Error dialogs explain issues

4. **Verify Setup**
   ```bash
   # Database exists?
   ls database/meal_planner.db

   # API keys set?
   cat .env

   # Dependencies installed?
   pip list
   ```

##  You're Ready!

Start planning better meals, tracking nutrition, and achieving your fitness goals with Macro Chef!

**Pro tip**: Spend 5 minutes each morning checking your dashboard and planning your day's meals. Consistency is key!
