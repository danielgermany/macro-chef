# Quick Test Checklist

## Server Status
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173 (check terminal for actual port)
- [ ] Backend API accessible: http://localhost:8000/api/
- [ ] API docs accessible: http://localhost:8000/docs

## Core User Flow (15 minutes)

### 1. Authentication (2 min)
- [ ] Register new user at /register
- [ ] Login with credentials
- [ ] Verify redirect to dashboard
- [ ] Check user name in header

### 2. Dashboard (1 min)
- [ ] View macro progress cards (should be 0/0 initially)
- [ ] View empty meals list
- [ ] View weight chart (empty if no metrics)

### 3. Nutrition Setup (2 min)
- [ ] Navigate to Nutrition page
- [ ] Generate targets
- [ ] Verify targets displayed
- [ ] Check macro distribution chart (empty initially)
- [ ] Check nutrition trend chart

### 4. Meal Logging (3 min)
- [ ] Navigate to Meal Tracker
- [ ] Log a manual meal (chicken, 250 cal, 50g protein)
- [ ] Verify meal appears in today's list
- [ ] Check dashboard updates
- [ ] Search for online recipe
- [ ] Add recipe to meal log
- [ ] View recipe details

### 5. Meal History (2 min)
- [ ] Click History button
- [ ] Verify meals displayed
- [ ] Test search filter
- [ ] Test date range filter
- [ ] Export to CSV

### 6. Inventory (2 min)
- [ ] Navigate to Inventory
- [ ] Add an item
- [ ] Verify item appears
- [ ] Check expiring items alert (if applicable)
- [ ] Export to CSV

### 7. Weekly Planner (2 min)
- [ ] Navigate to Weekly Planner
- [ ] Generate a weekly plan
- [ ] Verify plan displayed
- [ ] Check daily meals
- [ ] View shopping list
- [ ] Save plan

### 8. Budget (1 min)
- [ ] Navigate to Budget
- [ ] View weekly summary
- [ ] Toggle to monthly
- [ ] Check spending trends chart
- [ ] Check category breakdown

### 9. Settings (2 min)
- [ ] Navigate to Settings
- [ ] Update profile info
- [ ] Log body metrics
- [ ] View metrics history
- [ ] Change password (Security tab)
- [ ] Change email (Security tab)
- [ ] Export body metrics CSV

## Visual Checks
- [ ] Toast notifications appear for all actions
- [ ] Loading skeletons show during data fetch
- [ ] Charts render properly
- [ ] Forms show inline validation errors
- [ ] Responsive design works on different screen sizes

## Error Handling
- [ ] Invalid login shows error
- [ ] Form validation prevents invalid submissions
- [ ] Network errors handled gracefully
- [ ] 401 errors redirect to login

## Performance
- [ ] Pages load quickly
- [ ] Charts render smoothly
- [ ] No console errors
- [ ] No memory leaks (check browser dev tools)

## Notes
- Test with browser DevTools open (F12) to catch errors
- Check Network tab for failed API calls
- Verify localStorage has JWT token after login
- Test logout functionality
