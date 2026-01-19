# 🚀 Ready to Test!

## ✅ Servers Running
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## 🎯 Quick Start Testing

### Step 1: Open the Application
1. Open your browser and navigate to: **http://localhost:5173**
2. You should see the login/register page

### Step 2: Create a Test Account
1. Click "Register" or go to `/register`
2. Fill in:
   - **Email**: `test@macrochef.com`
   - **Password**: `testpass123` (min 8 chars)
   - **Name**: `Test User`
   - **Age**: `30`
   - **Height**: `70` inches
   - **Weight**: `180` lbs
   - **Goal**: `maintain`
   - **Activity Level**: `moderate`
3. Click "Register"
4. You should be redirected to login or dashboard

### Step 3: Login
1. If redirected to login, enter:
   - **Email**: `test@macrochef.com`
   - **Password**: `testpass123`
2. Click "Login"
3. You should see the Dashboard

### Step 4: Test Core Features (Follow QUICK_TEST_CHECKLIST.md)

## 📋 Testing Priority

### High Priority (Must Test)
1. ✅ **Authentication**: Register → Login → Logout
2. ✅ **Dashboard**: View macro progress, meals, weight chart
3. ✅ **Nutrition**: Generate targets, view charts
4. ✅ **Meal Tracker**: Log meal, search recipes, view history
5. ✅ **Settings**: Update profile, log metrics, change password

### Medium Priority
6. ✅ **Inventory**: Add items, view expiring items
7. ✅ **Weekly Planner**: Generate plan, view shopping list
8. ✅ **Budget**: View summaries, trends, categories

### Low Priority (Nice to Have)
9. ✅ **Export**: CSV downloads
10. ✅ **Charts**: All visualizations render correctly

## 🐛 Common Issues to Watch For

1. **CORS Errors**: Check browser console for CORS issues
2. **401 Unauthorized**: Token might be expired, try logging in again
3. **Empty Data**: Some features need data first (e.g., weight chart needs metrics)
4. **API Errors**: Check Network tab in DevTools for failed requests

## 📊 What to Verify

- [ ] All pages load without errors
- [ ] Forms validate input correctly
- [ ] Toast notifications appear for actions
- [ ] Charts render with data
- [ ] CSV exports work
- [ ] Navigation between pages works
- [ ] Responsive design on mobile/tablet

## 🔍 Debugging Tips

1. **Open Browser DevTools** (F12)
   - Console tab: Check for JavaScript errors
   - Network tab: Monitor API calls
   - Application tab: Check localStorage for token

2. **Check Backend Logs**
   - Look at the terminal where backend is running
   - Check for Python errors or exceptions

3. **Check Frontend Logs**
   - Look at the terminal where frontend is running
   - Check for build errors or warnings

## 📝 Test Results Template

```
Date: __________
Tester: __________

Authentication: [ ] Pass [ ] Fail - Notes: __________
Dashboard: [ ] Pass [ ] Fail - Notes: __________
Nutrition: [ ] Pass [ ] Fail - Notes: __________
Meal Tracker: [ ] Pass [ ] Fail - Notes: __________
Settings: [ ] Pass [ ] Fail - Notes: __________
Inventory: [ ] Pass [ ] Fail - Notes: __________
Weekly Planner: [ ] Pass [ ] Fail - Notes: __________
Budget: [ ] Pass [ ] Fail - Notes: __________
Export: [ ] Pass [ ] Fail - Notes: __________
Charts: [ ] Pass [ ] Fail - Notes: __________

Issues Found:
1. __________
2. __________
3. __________
```

## 🎉 Ready to Go!

Open http://localhost:5173 and start testing!

For detailed step-by-step instructions, see **TEST_WORKFLOW.md**
For quick checklist, see **QUICK_TEST_CHECKLIST.md**
