# Test Failures Documentation

**Date:** January 19, 2026  
**Test Run:** Backend API Tests + Frontend Build

## Test Summary

- **Total Tests:** 17
- **Passed:** 8 (47%)
- **Failed:** 8 (47%)
- **Errors:** 1 (6%)
- **Warnings:** 29

## Backend Test Failures

### 1. Authentication Tests (4 failures, 1 error)

#### Failure: `test_register_user`
**Error:** `ValueError: password cannot be longer than 72 bytes, truncate manually if necessary`

**Root Cause:** 
- Bcrypt library has a 72-byte limit for passwords
- The error occurs during bcrypt initialization when detecting a wrap bug
- The test password "testpassword123" is fine, but bcrypt's internal detection mechanism is failing
- This is a known issue with passlib/bcrypt on some systems

**Location:** `app/auth/jwt.py:24` in `get_password_hash()`

**Fix Required:**
- Update `get_password_hash()` to handle bcrypt initialization properly
- Consider using `passlib` with `argon2` instead of `bcrypt` for better compatibility
- Or add error handling for bcrypt initialization

#### Failure: `test_register_duplicate_email`
**Error:** Same as above - bcrypt initialization issue

#### Failure: `test_login_success`
**Error:** Same as above - bcrypt initialization issue

#### Error: `test_get_current_user`
**Error:** Same bcrypt issue during fixture setup (`auth_token` fixture)

#### Passed: `test_login_invalid_credentials`
✓ Works correctly - returns 401 for invalid credentials

#### Passed: `test_get_current_user_no_token`
✓ Works correctly - returns 401 without token

#### Passed: `test_get_current_user_invalid_token`
✓ Works correctly - returns 401 for invalid token

---

### 2. Meal Tests (4 failures)

#### Failure: `test_log_meal`
**Error:** `assert 400 == 201` - Bad Request instead of Created

**Root Cause:**
- The meal logging endpoint is returning 400 Bad Request
- Need to check actual error response to see what validation is failing
- Likely missing required fields or enum value mismatch

**Location:** `app/routers/meals.py` in `log_meal()` endpoint

**Fix Required:**
- Check the actual error response in test
- Verify all required fields are being sent
- Check `meal_time` enum validation (should be "lunch" not "Lunch")

#### Failure: `test_get_daily_progress`
**Error:** `TypeError: expected str, bytes or os.PathLike object, not NoneType`

**Root Cause:**
- `db_path` is `None` when `MealTracker` is instantiated
- The service layer isn't properly passing database path to managers
- Managers default to `DATABASE_PATH` from `config.config`, but test sets `DATABASE_URL` env var
- The managers don't read from `DATABASE_URL` environment variable

**Location:** `scripts/db_manager.py:26` in `connect()`

**Fix Required:**
- Update managers to read `DATABASE_URL` from environment if `db_path` not provided
- Or update router dependencies to extract db_path from `DATABASE_URL` and pass to managers
- Fix `get_meal_tracker()` to pass db_path from config

#### Failure: `test_get_meal_history`
**Error:** Same as above - `db_path` is None

**Root Cause:** Same database path issue

#### Failure: `test_delete_meal`
**Error:** `KeyError: 'id'` - Response doesn't contain 'id' field

**Root Cause:**
- Meal logging endpoint doesn't return the meal with 'id' field
- The response structure doesn't match what the test expects
- Looking at code: `log_meal()` tries to get meal from history but may return None

**Location:** `app/routers/meals.py` in `log_meal()` endpoint

**Fix Required:**
- Update `log_meal()` to return the created meal with ID
- Or update test to get meal ID from history instead
- Check that `tracker.get_meal_history()` returns the meal

---

### 3. User Tests (1 failure, 4 passed)

#### Failure: `test_create_user`
**Error:** `assert 422 == 201` - Unprocessable Entity instead of Created

**Root Cause:**
- Request validation is failing (422 = validation error)
- Need to check what validation error is returned
- Likely enum value mismatch or missing required field

**Location:** `app/routers/users.py` in `create_user()` endpoint

**Fix Required:**
- Check Pydantic schema validation
- Verify enum values match (goal_type, activity_level should be lowercase)
- Check if all required fields are present in test

#### Passed Tests:
- ✓ `test_get_user` - Works correctly
- ✓ `test_get_nonexistent_user` - Returns 404 correctly
- ✓ `test_update_user` - Update works correctly
- ✓ `test_log_body_metrics` - Metrics logging works
- ✓ `test_get_metrics_history` - History retrieval works

---

## Frontend Build Failures

### TypeScript Compilation Errors (6 errors)

#### Error 1: `AuthContext.tsx(1,58)`
**Error:** `'ReactNode' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.`

**Current:**
```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
```

**Fix:**
```typescript
import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
```

#### Error 2: `AuthContext.tsx(75,11)`
**Error:** `'response' is declared but its value is never read.`

**Current:**
```typescript
const response = await api.post('/auth/register', data);
```

**Fix:**
```typescript
await api.post('/auth/register', data);
// Or use the response if needed
```

#### Error 3: `Inventory.tsx(5,39)`
**Error:** `'Edit2' is declared but its value is never read.`

**Fix:**
```typescript
// Remove Edit2 from imports
import { Plus, AlertTriangle, Trash2 } from 'lucide-react';
```

#### Error 4: `MealTracker.tsx(5,16)`
**Error:** `'Search' is declared but its value is never read.`

**Fix:**
```typescript
// Remove Search from imports
import { Plus } from 'lucide-react';
```

#### Error 5: `MealTracker.tsx(12,9)`
**Error:** `'user' is declared but its value is never read.`

**Fix:**
```typescript
// Remove unused variable
// const { data: user } = useUser(userId); // Remove this line
```

#### Error 6: `Nutrition.tsx(1,1)`
**Error:** `'useState' is declared but its value is never read.`

**Fix:**
```typescript
// Remove useState from imports
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
```

---

## Warnings (Non-Critical)

### Pydantic Deprecation Warnings
- Multiple files using deprecated `class Config` instead of `ConfigDict`
- Files affected:
  - `app/config.py` - Line 34
  - `app/schemas/user.py` - Lines 57, 91
  - `app/schemas/meal.py` - Lines 35, 101
  - `app/schemas/nutrition.py` - Line 13
  - `app/schemas/inventory.py` - Line 27

**Fix:** Update to use `model_config = ConfigDict(...)` instead of `class Config:`

**Example:**
```python
# Old:
class UserResponse(BaseModel):
    class Config:
        from_attributes = True

# New:
from pydantic import ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### SQLAlchemy Deprecation Warning
- `app/database.py:33` - Using deprecated `declarative_base()`
- Should use `sqlalchemy.orm.declarative_base()`

**Fix:**
```python
# Old:
from sqlalchemy.ext.declarative import declarative_base

# New:
from sqlalchemy.orm import declarative_base
```

### SQLite Deprecation Warnings
- Python 3.12+ deprecation warnings for datetime/date adapters
- Files affected: `scripts/db_manager.py:55`

**Fix:** Use proper type converters for datetime/date in SQLite

### Resource Warnings
- Multiple unclosed database connections
- Database connections not being properly closed in test fixtures
- Need to ensure `disconnect()` is called or use context managers

**Fix:** Update `DatabaseManager` to use context managers or ensure cleanup in tests

---

## Critical Issues Summary

### High Priority (Blocking Tests)

1. **Bcrypt Password Hashing Issue** 🔴
   - All auth tests failing due to bcrypt initialization
   - **Impact:** Authentication completely broken
   - **Files:** `app/auth/jwt.py`
   - **Fix:** Update password hashing or switch to argon2

2. **Database Path Not Propagated** 🔴
   - Services not receiving database path from environment
   - All meal tracking tests failing
   - **Impact:** Meal tracking endpoints broken
   - **Files:** `app/routers/meals.py`, `scripts/db_manager.py`
   - **Fix:** Extract db_path from DATABASE_URL and pass to managers

3. **Frontend TypeScript Errors** 🔴
   - Build fails due to type import issues and unused variables
   - **Impact:** Frontend cannot be built for production
   - **Files:** Multiple frontend files
   - **Fix:** Fix type imports and remove unused variables

### Medium Priority (Test Data Issues)

4. **Meal Logging Response Format** 🟡
   - Endpoint doesn't return expected format
   - Missing 'id' field in response
   - **Impact:** Tests fail, but functionality may work
   - **Files:** `app/routers/meals.py`

5. **User Creation Validation** 🟡
   - Request validation failing (422 error)
   - Need to check required fields
   - **Impact:** User creation may not work
   - **Files:** `app/routers/users.py`, `app/schemas/user.py`

### Low Priority (Warnings)

6. **Deprecation Warnings** 🟢
   - Pydantic v2 migration needed
   - SQLAlchemy v2 migration needed
   - **Impact:** Future compatibility issues

7. **Resource Leaks** 🟢
   - Database connections not closed
   - **Impact:** Memory leaks in long-running tests

---

## Recommended Fix Order

### Phase 1: Critical Fixes (Do First)

1. **Fix Database Path Propagation** (30 min)
   - Update `get_meal_tracker()` and other dependencies to extract db_path from DATABASE_URL
   - Update managers to read from environment if db_path not provided
   - **Files:** `backend/app/routers/*.py`, `scripts/db_manager.py`

2. **Fix Bcrypt Password Hashing** (1 hour)
   - Update `get_password_hash()` to handle bcrypt properly
   - Or switch to argon2 for better compatibility
   - **Files:** `backend/app/auth/jwt.py`

3. **Fix Frontend TypeScript Errors** (15 min)
   - Fix type imports
   - Remove unused variables
   - **Files:** `frontend/src/**/*.tsx`

### Phase 2: Medium Priority (Do Next)

4. **Fix Meal Logging Response** (30 min)
   - Update endpoint to return proper response format
   - **Files:** `backend/app/routers/meals.py`

5. **Fix User Creation Validation** (30 min)
   - Check and fix validation requirements
   - **Files:** `backend/app/routers/users.py`

### Phase 3: Cleanup (Do Last)

6. **Fix Deprecation Warnings** (1 hour)
   - Update to Pydantic v2 ConfigDict
   - Update SQLAlchemy imports
   - Fix SQLite adapters

7. **Fix Resource Leaks** (30 min)
   - Ensure database connections are closed
   - Use context managers where appropriate

---

## Test Coverage

**Overall Coverage:** 79%

**Well Covered:**
- Schemas: 100% coverage
- Config: 100% coverage
- Users router: 82% coverage

**Needs Improvement:**
- Auth router: 57% coverage (blocked by bcrypt issue)
- Meals router: 60% coverage (blocked by db_path issue)
- Inventory router: 42% coverage
- Budget router: 42% coverage
- Nutrition router: 45% coverage
- Plans router: 45% coverage
- Recipes router: 45% coverage

---

## Detailed Error Analysis

### Bcrypt Error Details

The error occurs in `passlib.handlers.bcrypt.py:655` during `_calc_checksum()`:
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

This happens during bcrypt's internal bug detection, not with the actual password. The test password "testpassword123" is only 16 characters, well under 72 bytes.

**Possible Solutions:**
1. Use `bcrypt` directly instead of through `passlib`
2. Switch to `argon2` hashing (recommended)
3. Add error handling for bcrypt initialization
4. Update bcrypt library version

### Database Path Issue Details

The problem is that:
1. Tests set `DATABASE_URL` environment variable: `sqlite:///path/to/temp.db`
2. Managers default to `DATABASE_PATH` from `config.config` (which is a Path object)
3. Managers don't read from `DATABASE_URL` environment variable
4. When `db_path` is None, SQLite connection fails

**Solution:**
Update `DatabaseManager.__init__()` to:
1. Check for `DATABASE_URL` environment variable first
2. Extract path from `sqlite:///` URL format
3. Fall back to `DATABASE_PATH` from config if not set

---

## Next Steps

1. ✅ Document all failures (this file)
2. Fix critical issues (database path, bcrypt, TypeScript)
3. Re-run tests to verify fixes
4. Address medium priority issues
5. Clean up warnings
6. Improve test coverage for low-coverage areas

---

## Test Execution Commands

```bash
# Run all backend tests
cd backend
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Build frontend
cd frontend
npm run build
```
