# Full Workflow Testing Guide

## Prerequisites
1. Backend server running on http://localhost:8000
2. Frontend server running on http://localhost:5173 (or check terminal output)
3. Database initialized (should happen automatically on first run)

## Test Workflow

### 1. User Registration
- Navigate to http://localhost:5173/register
- Fill in registration form:
  - Email: test@example.com
  - Password: testpassword123 (min 8 characters)
  - Name: Test User
  - Optional: Age, Height, Weight, Goal Type, Activity Level
- Click "Register"
- **Expected**: Success message, redirect to login or dashboard

### 2. User Login
- Navigate to http://localhost:5173/login
- Enter credentials:
  - Email: test@example.com
  - Password: testpassword123
- Click "Login"
- **Expected**: Redirect to Dashboard, user name displayed in header

### 3. Dashboard Overview
- **Expected**: 
  - Welcome message with user name
  - Macro progress cards (Calories, Protein, Carbs, Fat)
  - Today's meals list (empty initially)
  - Quick actions panel
  - Weight progress chart (empty if no metrics logged)

### 4. Generate Nutrition Targets
- Navigate to Nutrition page
- Click "Generate Targets" button
- **Expected**: 
  - Targets generated based on user profile
  - Display shows: Calories, Protein, Carbs, Fat targets
  - User profile info displayed
  - Macro distribution chart (shows today's consumed macros)
  - Nutrition trend chart (last 7 days)

### 5. Log a Meal
- Navigate to Meal Tracker page
- Click "Log Meal" button
- Fill in meal form:
  - Meal Name: Grilled Chicken Breast
  - Meal Time: Dinner
  - Calories: 250
  - Protein: 50g
  - Carbs: 0g
  - Fat: 5g
- Click "Log Meal"
- **Expected**: 
  - Success toast notification
  - Meal appears in "Today's Meals" list
  - Dashboard macro progress updates

### 6. Search and Add Online Recipe
- In Meal Tracker, click "Search Recipes"
- Enter search query: "chicken pasta"
- Optionally set filters (max calories, min protein, max time)
- Click "Search"
- **Expected**: 
  - Recipe cards displayed with nutrition info
  - Click "Add to Log" to populate form
  - Click "View Details" to see full recipe information

### 7. View Meal History
- In Meal Tracker, click "History" button
- **Expected**: 
  - Meal history displayed grouped by date
  - Filter options available:
    - Search by meal name
    - Filter by last N days (7, 14, 30, 60, 90)
    - Filter by custom date range
  - Click "Export to CSV" to download meal logs

### 8. Add Inventory Item
- Navigate to Inventory page
- Click "Add Item" button
- Fill in form:
  - Item Name: Chicken Breast
  - Quantity: 2
  - Unit: lbs
  - Category: Protein
  - Location: Fridge
  - Expiration Date: (optional)
- Click "Add Item"
- **Expected**: 
  - Success toast notification
  - Item appears in inventory list
  - Expiring items alert if expiration date is soon

### 9. Generate Weekly Meal Plan
- Navigate to Weekly Planner page
- Click "Generate New Plan"
- Enter plan name (optional): "Test Week 1"
- Click "Generate Plan"
- **Expected**: 
  - Weekly plan generated with meals for each day
  - Daily plans show breakfast, lunch, dinner, snacks
  - Nutrition totals and cost estimates displayed
  - Click "Save Plan" to save
  - Click "Shopping List" to view generated shopping list

### 10. View Budget Summary
- Navigate to Budget page
- **Expected**: 
  - Weekly/Monthly summary toggle
  - Total spent, remaining budget, percentage used
  - Spending trends chart
  - Category breakdown (pie chart and table)
  - Navigation to previous/next periods

### 11. Log Body Metrics
- Navigate to Settings page
- Click "Body Metrics" tab
- Click "Log Metrics" button
- Fill in form:
  - Weight: 180 lbs
  - Body Fat %: 15
  - Optional: Waist, Chest, Arms, Legs measurements
  - Notes: "Morning measurement"
- Click "Log Metrics"
- **Expected**: 
  - Success toast notification
  - Metrics appear in history
  - Progress summary updates
  - Weight chart on Dashboard updates

### 12. Update Profile
- In Settings, "Profile" tab
- Update any fields (name, age, height, weight, goal, activity level, budget)
- Click "Save Changes"
- **Expected**: 
  - Success toast notification
  - Changes reflected immediately
  - Nutrition targets may need regeneration

### 13. Change Password
- In Settings, click "Security" tab
- Fill in "Change Password" form:
  - Current Password: testpassword123
  - New Password: newpassword123
  - Confirm New Password: newpassword123
- Click "Change Password"
- **Expected**: 
  - Success toast notification
  - Form clears
  - Can login with new password

### 14. Change Email
- In Settings, "Security" tab
- Fill in "Change Email" form:
  - New Email: newemail@example.com
  - Confirm Password: newpassword123
- Click "Change Email"
- **Expected**: 
  - Success toast notification
  - Email updated
  - Can login with new email

### 15. Export Data
- **Meal Logs**: Meal Tracker > History > Export to CSV
- **Nutrition Summary**: Nutrition page > Export Summary (CSV)
- **Body Metrics**: Settings > Body Metrics > Export CSV
- **Inventory**: Inventory page > Export CSV
- **Expected**: CSV files download with proper formatting

### 16. Data Visualizations
- Navigate to Nutrition page
- **Expected**: 
  - Macro Distribution Chart: Pie chart showing protein/carbs/fat percentages
  - Nutrition Trend Chart: Line chart showing 7-day trends with actual vs targets
- Navigate to Dashboard
- **Expected**: 
  - Weight Progress Chart: Line chart showing weight over time

## Error Scenarios to Test

1. **Invalid Login**: Wrong password → Error toast
2. **Duplicate Email**: Register with existing email → Error message
3. **Form Validation**: Submit empty forms → Inline error messages
4. **Invalid Date Range**: End date before start date → Validation error
5. **Network Error**: Stop backend → Error handling and user feedback

## Performance Checks

1. **Loading States**: All pages show skeleton loaders while loading
2. **Toast Notifications**: All actions show success/error toasts
3. **Responsive Design**: Test on different screen sizes
4. **Chart Rendering**: Charts load smoothly with data

## Notes

- All API calls require authentication (JWT token)
- Token stored in localStorage
- Auto-logout on 401 errors
- Protected routes redirect to login if not authenticated
