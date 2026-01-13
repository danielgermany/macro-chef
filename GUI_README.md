# Macro Chef GUI Application

A user-friendly graphical interface for the Macro Chef meal planning and nutrition tracking system.

## Features

### Dashboard
- View daily nutrition targets (calories, protein, carbs, fat, fiber)
- Quick stats overview (meal count, inventory, goals)
- One-click refresh

### User Profile
- Create and edit user profiles
- Set personal metrics (age, sex, height, weight, body fat %)
- Configure fitness goals (bulk, cut, maintain, recomp)
- Set activity level and training frequency
- Weekly budget tracking
- Generate daily nutrition targets

### Meals
- Browse saved meal templates
- View nutrition information (calories, macros)
- Get AI-powered meal recommendations based on your targets
- Filter by meal type

### Inventory
- Track food inventory
- Add items with quantity, category, and location
- Monitor expiration dates
- Search and filter items

### Search Recipes
- Search 570,000+ online recipes via Spoonacular API
- Filter by calories, protein, and prep time
- USDA nutrition validation
- See detailed nutrition breakdown
- Save recipes to your meal library

## Usage

### Quick Start

1. **Launch the application:**
   ```bash
   python3 gui_app.py
   ```

2. **Set up your profile:**
   - Go to the "Profile" tab
   - Fill in your personal information
   - Click "Save Profile"
   - Click "Generate Targets" to calculate your daily nutrition goals

3. **View your dashboard:**
   - Go to the "Dashboard" tab
   - See your daily nutrition targets
   - View quick stats about your meals and inventory

4. **Add inventory:**
   - Go to the "Inventory" tab
   - Fill in item details
   - Click "Add Item"

5. **Search recipes:**
   - Go to the "Search Recipes" tab
   - Enter a search query (e.g., "chicken breast")
   - Adjust filters (calories, protein, time)
   - Click "Search"

6. **Get meal recommendations:**
   - Go to the "Meals" tab
   - Click "Get Recommendation"
   - Receive personalized meal suggestions based on your targets

## Keyboard Shortcuts

- **Enter** in search box: Execute search
- **Tab**: Navigate between fields
- **Escape**: Close dialogs

## Requirements

- Python 3.8+
- tkinter (included with Python)
- All Macro Chef dependencies (see main README.md)
- API keys configured in `.env` file

## Tips

1. **First-time setup:**
   - Create your profile first before using other features
   - Generate targets to get personalized recommendations

2. **Meal planning:**
   - Use the search feature to discover new recipes
   - Check the "Nutrition validated" badge for accurate data
   - Add items to inventory before shopping

3. **Budget tracking:**
   - Set your weekly budget in the profile
   - The system will consider cost when recommending meals

4. **Training days:**
   - Set your training frequency in the profile
   - Targets automatically adjust for training vs. rest days

## Troubleshooting

### GUI won't launch
- Ensure tkinter is installed: `python3 -m tkinter`
- Try running with: `python3 -m gui_app`

### No results in search
- Check that API keys are set in `.env` file
- Verify internet connection
- Check API quota (Spoonacular free tier: 150 requests/day)

### Database errors
- Ensure database exists: `python3 scripts/db_setup.py`
- Check file permissions on `database/` directory

### Profile won't save
- Check that database is initialized
- Ensure all required fields are filled
- Check status bar for error messages

## Architecture

The GUI is built with:
- **tkinter**: Python's standard GUI library
- **ttk**: Themed widgets for modern appearance
- **Threading**: Background API calls (future enhancement)

It integrates with:
- User Profile Manager
- Nutrition Calculator
- Meal Recommender
- Inventory Manager
- Spoonacular API
- USDA API

## Future Enhancements

- [ ] Weekly meal plan generator with drag-and-drop
- [ ] Shopping list generator
- [ ] Progress charts and analytics
- [ ] Meal prep calendar view
- [ ] Recipe image display
- [ ] Barcode scanner for inventory
- [ ] Export meal plans to PDF
- [ ] Dark mode theme

## Support

For issues or questions:
1. Check the main README.md
2. Review the test suite in `tests/`
3. Open an issue on GitHub

## License

Same as main Macro Chef project
