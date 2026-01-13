# Macro Chef GUI - Feature Overview

##  User Interface Design

The Macro Chef GUI provides an intuitive, tab-based interface built with Python's tkinter library, offering a modern and responsive user experience.

### Design Principles

- **Clean Layout**: Tab-based navigation for easy access to all features
- **Visual Hierarchy**: Clear section headers for quick recognition
- **Responsive Design**: Adapts to different screen sizes
- **Color-Coded Status**: Success (green), warnings (orange), errors (red)
- **Professional Typography**: Clean fonts with appropriate sizing

##  Tab 1: Dashboard

**Purpose**: Quick overview of your daily nutrition goals and system stats

### Features:
- **Daily Nutrition Targets Display**
  - Total calorie target
  - Macronutrient breakdown (protein, carbs, fat, fiber)
  - Formatted with clear visual separators

- **Quick Stats Panel**
  - Number of saved meals in database
  - Inventory item count
  - Current fitness goal
  - Activity level
  - Refresh button for real-time updates

### Use Cases:
- Morning check-in to see daily targets
- Quick reference throughout the day
- Verify system status

##  Tab 2: Profile

**Purpose**: Manage user profile and generate personalized nutrition targets

### Features:
- **Personal Information**
  - Name (text input)
  - Age (spinner: 18-100)
  - Sex (dropdown: male/female)
  - Height in inches (spinner: 48-84)
  - Weight in lbs (spinner: 80-400)
  - Body fat % (optional, spinner: 5-50%, 0.5% increments)

- **Fitness Configuration**
  - Goal type (dropdown: bulk/cut/maintain/recomp)
  - Activity level (dropdown: sedentary/light/moderate/very_active/athlete)
  - Training days per week (spinner: 0-7)
  - Weekly budget in USD (spinner: $20-$500)

- **Actions**
  - Save Profile: Create or update user data
  - Load Profile: Retrieve existing profile (auto-loads on startup)
  - Generate Targets: Calculate daily nutrition targets using BMR/TDEE formulas

### Calculations:
- **BMR**: Uses Katch-McArdle (with body fat %) or Mifflin-St Jeor formula
- **TDEE**: Applies activity multipliers (1.2x to 1.9x)
- **Macro Targets**: Goal-specific protein ratios:
  - Bulk: 1.0g/lb bodyweight
  - Cut: 1.2g/lb (muscle preservation)
  - Maintain: 0.8g/lb
  - Recomp: 1.1g/lb
- **Micronutrients**: RDA-based targets with athlete multipliers

##  Tab 3: Meals

**Purpose**: Browse saved meals and get AI-powered recommendations

### Features:
- **Meal Templates Table**
  - Columns: ID, Name, Type, Calories, Protein, Carbs, Fat
  - Sortable by clicking headers
  - Scrollable list (displays up to 100 recent meals)

- **Actions**
  - Refresh Meals: Reload from database
  - Get Recommendation: AI suggests meal based on:
    - Remaining daily macros
    - Target meal type (breakfast/lunch/dinner/snack)
    - Proportional allocation (e.g., dinner = 1/3 daily targets)
    - Personal preferences and history

### Recommendation Algorithm:
1. Fetch today's nutrition targets
2. Calculate meal-specific targets (e.g., dinner = 33% of daily)
3. Query database for matching meals
4. Score based on:
   - Macro proximity to targets
   - Variety (avoid recent repeats)
   - User ratings (if available)
5. Return top match with details

##  Tab 4: Inventory

**Purpose**: Track food items with quantities and expiration dates

### Features:
- **Inventory Table**
  - Columns: ID, Item, Quantity, Unit, Category, Location, Expires
  - Real-time display of all items
  - Sortable and scrollable

- **Add Item Form**
  - Item Name (text input)
  - Quantity (decimal input)
  - Unit (dropdown: lbs/oz/g/kg/count/cups)
  - Category (dropdown: protein/carbs/vegetable/fruit/dairy/grain/fat/snack/other)
  - Location (dropdown: fridge/freezer/pantry/counter)
  - Days Until Expiry (spinner: 1-365)

- **Actions**
  - Add Item: Insert new inventory item
  - Refresh List: Update display

### Benefits:
- Prevent food waste by tracking expiration
- Support meal recommendations based on available ingredients
- Organize by location for efficient kitchen management
- Track quantities for shopping list generation

##  Tab 5: Search Recipes

**Purpose**: Search 570,000+ online recipes with nutrition filtering

### Features:
- **Search Bar**
  - Free-text query (e.g., "chicken breast", "high protein pasta")
  - Real-time search via Spoonacular API

- **Filters**
  - Max Calories (spinner: 100-2000, 50 cal increments)
  - Min Protein (spinner: 0-100g, 5g increments)
  - Max Prep Time (spinner: 5-180 minutes, 5 min increments)

- **Results Display**
  - Recipe title and ID
  - Prep time
  - Complete nutrition breakdown (calories, protein, carbs, fat)
  - Validation status ( if cross-checked with USDA)
  - Formatted with visual separators

### Advanced Features:
- **Nutrition Validation**: Cross-references with USDA database
  - Compares ingredient-level nutrition data
  - Flags discrepancies >10%
  - Provides confidence rating

- **Price Estimation**: Hybrid model
  - 70% based on shopping history
  - 30% based on API estimates
  - Realistic cost projections

- **Smart Caching**: Auto-saves recipes rated ≥3 stars

### API Integration:
- **Spoonacular**: Recipe search, nutrition data, instructions
- **USDA FoodData Central**: Ingredient validation
- Automatic fallback if APIs unavailable
- Request throttling to respect quotas

##  Status Bar

**Purpose**: Real-time feedback and error messages

### Displays:
- Current operation status
- Success confirmations (green)
- Warning messages (orange)
- Error alerts (red)
- User feedback for all actions

##  Technical Implementation

### Architecture:
```
MacroChefGUI (Main Class)
├── User Profile Manager
├── Nutrition Calculator
├── Meal Recommender
├── Inventory Manager
└── Database Manager
```

### Key Methods:
- `load_user()`: Auto-load user ID 1 on startup
- `save_profile()`: Create/update user with validation
- `generate_targets()`: Calculate daily nutrition goals
- `refresh_dashboard()`: Update all dashboard stats
- `refresh_meals()`: Query and display meal templates
- `get_meal_recommendation()`: AI-powered meal suggestion
- `refresh_inventory()`: Load and display inventory
- `add_inventory_item()`: Insert with expiration calculation
- `search_recipes()`: Query Spoonacular with filters

### Error Handling:
- Try-catch blocks on all database operations
- User-friendly error dialogs
- Status bar feedback
- Graceful degradation if APIs unavailable

### Performance:
- Background thread support (future enhancement)
- Efficient SQL queries with indexes
- Caching to minimize API calls
- Lazy loading for large datasets

##  Future Enhancements

### Planned Features:
1. **Weekly Meal Plan View**
   - Drag-and-drop calendar interface
   - Visual meal assignment
   - Auto-generate shopping list

2. **Progress Charts**
   - Weight tracking graphs
   - Macro adherence trends
   - Budget spending analysis
   - Matplotlib/Plotly integration

3. **Shopping List Generator**
   - Smart ingredient aggregation
   - Check against inventory
   - Store location mapping
   - Export to mobile apps

4. **Recipe Details View**
   - Display recipe images
   - Step-by-step instructions
   - Ingredient substitutions
   - Nutrition breakdown per serving

5. **Meal Prep Calendar**
   - Batch cooking planner
   - Prep time optimizer
   - Storage container suggestions
   - Reheating instructions

6. **Barcode Scanner**
   - Quick inventory addition
   - Nutrition lookup
   - Price tracking
   - UPC database integration

7. **Export/Import**
   - PDF meal plans
   - CSV data export
   - Recipe sharing
   - Backup/restore

8. **Theming**
   - Dark mode
   - Color customization
   - Font size adjustment
   - Accessibility features

9. **Multi-User Support**
   - User switching dropdown
   - Household meal planning
   - Shared inventory
   - Budget splitting

10. **Smart Notifications**
    - Expiration alerts
    - Meal prep reminders
    - Target achievement notifications
    - Budget warnings

##  Usage Tips

### Getting Started:
1. Create your profile first (Profile tab)
2. Generate targets to enable recommendations
3. Add some inventory items
4. Search recipes to populate your database
5. Use recommendations for daily meal planning

### Best Practices:
- Update weight weekly for accurate targets
- Log meals immediately after eating
- Review inventory before shopping
- Rate saved recipes for better recommendations
- Check dashboard each morning

### Power User Features:
- Use keyboard shortcuts (Tab, Enter)
- Leverage filters in recipe search
- Track body fat % for precise BMR
- Adjust training days on rest weeks
- Set realistic budgets for adherence

##  Troubleshooting

### Common Issues:

**Profile won't save:**
- Check all required fields are filled
- Verify database file exists
- Check file permissions

**No meal recommendations:**
- Generate targets first (Profile tab)
- Add meals to database (search recipes)
- Check database has templates

**Search returns no results:**
- Verify .env has API keys
- Check internet connection
- Relax filter constraints
- Verify API quota not exceeded

**Inventory items disappear:**
- Check database wasn't reset
- Verify add operation succeeded
- Refresh the list

**GUI won't launch:**
- Verify Python 3.8+ installed
- Check tkinter available: `python3 -m tkinter`
- Review error messages
- Try: `python3 -m gui_app`

##  Related Documentation

- [GUI_README.md](GUI_README.md) - Setup and usage guide
- [README.md](README.md) - Main project documentation
- [SPECIFICATION.md](SPECIFICATION.md) - Complete system specification
- [ONLINE_RECIPE_FEATURE.md](ONLINE_RECIPE_FEATURE.md) - API integration details

##  Learning Resources

### For Developers:
- tkinter documentation: https://docs.python.org/3/library/tkinter.html
- ttk themed widgets: https://docs.python.org/3/library/tkinter.ttk.html
- Spoonacular API: https://spoonacular.com/food-api
- USDA FoodData Central: https://fdc.nal.usda.gov/api-guide.html

### For Users:
- Nutrition basics: Understanding BMR, TDEE, macros
- Meal planning strategies
- Food inventory management
- Budget-friendly eating
