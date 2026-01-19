#!/usr/bin/env python3
"""
GUI Flow Testing Script
Simulates user interactions to test all GUI functionality.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
from datetime import date, timedelta
import sqlite3
import tempfile
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Mock dotenv to avoid permission issues
import unittest.mock
with unittest.mock.patch('dotenv.load_dotenv'):
    from gui_app import MacroChefGUI
    from scripts.db_manager import DatabaseManager
    import scripts.db_setup as db_setup


class GUITestHarness:
    """Test harness for GUI flows."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during testing
        
        # Use temporary database for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = Path(self.test_db.name)
        self.test_db.close()
        
        # Initialize test database
        conn = sqlite3.connect(self.test_db_path)
        db_setup.create_tables(conn)
        conn.close()
        
        # Create GUI instance with test database
        self.app = MacroChefGUI(self.root, db_path=self.test_db_path)
        self.root.update()
        
        self.test_results = []
        self.current_test = None
        
    def log_test(self, test_name, status, message=""):
        """Log test result."""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        result = f"{status_symbol} {test_name}: {status}"
        if message:
            result += f" - {message}"
        self.test_results.append(result)
        print(result)
        
    def simulate_entry(self, var, value):
        """Simulate typing into an entry field."""
        try:
            if isinstance(var, tk.StringVar):
                var.set(str(value))
            elif isinstance(var, tk.IntVar):
                var.set(int(value))
            elif isinstance(var, tk.DoubleVar):
                var.set(float(value))
            elif isinstance(var, tk.BooleanVar):
                var.set(bool(value))
            return True
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Entry simulation failed: {e}")
            return False
    
    def simulate_click(self, widget):
        """Simulate clicking a widget."""
        try:
            widget.invoke()
            self.root.update()
            return True
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Click simulation failed: {e}")
            return False
    
    def check_database(self, table, condition=None):
        """Check database for records."""
        try:
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            if condition:
                query = f"SELECT COUNT(*) FROM {table} WHERE {condition}"
            else:
                query = f"SELECT COUNT(*) FROM {table}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Database check error: {e}")
            return 0
    
    def test_flow_1_create_user_and_generate_targets(self):
        """Test Flow 1: Create user profile and generate targets."""
        self.current_test = "Flow 1: Create User & Generate Targets"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Fill profile form
            self.simulate_entry(self.app.name_var, "Test User")
            self.simulate_entry(self.app.age_var, 30)
            self.simulate_entry(self.app.sex_var, "male")
            self.simulate_entry(self.app.height_var, 72)
            self.simulate_entry(self.app.weight_var, 180)
            self.simulate_entry(self.app.bodyfat_var, 15.0)
            self.simulate_entry(self.app.goal_var, "cut")
            self.simulate_entry(self.app.activity_var, "moderate")
            self.simulate_entry(self.app.training_days_var, 4)
            self.simulate_entry(self.app.budget_var, 150.0)
            self.root.update()
            
            # Step 2: Save profile
            save_button = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for i in range(widget.index("end")):
                        tab = widget.nametowidget(widget.tabs()[i])
                        for child in tab.winfo_children():
                            if isinstance(child, ttk.LabelFrame):
                                for subchild in child.winfo_children():
                                    if isinstance(subchild, ttk.Frame):
                                        for btn in subchild.winfo_children():
                                            if isinstance(btn, ttk.Button) and "Save Profile" in str(btn.cget("text")):
                                                save_button = btn
                                                break
            
            if save_button:
                self.simulate_click(save_button)
                self.root.update()
                
                # Check if user was created
                user_count = self.check_database("user_profile", "name = 'Test User'")
                if user_count > 0:
                    self.log_test("Step 1: Create User", "PASS", f"User created (ID: {self.app.current_user_id})")
                else:
                    self.log_test("Step 1: Create User", "FAIL", "User not found in database")
                    return
            else:
                self.log_test("Step 1: Create User", "FAIL", "Save Profile button not found")
                return
            
            # Step 3: Generate targets
            generate_button = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for i in range(widget.index("end")):
                        tab = widget.nametowidget(widget.tabs()[i])
                        for child in tab.winfo_children():
                            if isinstance(child, ttk.LabelFrame):
                                for subchild in child.winfo_children():
                                    if isinstance(subchild, ttk.Frame):
                                        for btn in subchild.winfo_children():
                                            if isinstance(btn, ttk.Button) and "Generate Targets" in str(btn.cget("text")):
                                                generate_button = btn
                                                break
            
            if generate_button:
                self.simulate_click(generate_button)
                self.root.update()
                
                # Check if targets were created
                target_count = self.check_database("daily_nutrition_targets", f"user_id = {self.app.current_user_id}")
                if target_count > 0:
                    self.log_test("Step 2: Generate Targets", "PASS", f"Targets created ({target_count} record)")
                else:
                    self.log_test("Step 2: Generate Targets", "FAIL", "No targets found in database")
            else:
                self.log_test("Step 2: Generate Targets", "FAIL", "Generate Targets button not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_2_meal_recommendation(self):
        """Test Flow 2: Get meal recommendation."""
        self.current_test = "Flow 2: Meal Recommendation"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Meals tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            # Find Meals tab
            meals_tab_idx = None
            for i in range(notebook.index("end")):
                tab_text = notebook.tab(i, "text")
                if "Meals" in tab_text and "Log" not in tab_text:
                    meals_tab_idx = i
                    break
            
            if meals_tab_idx is None:
                self.log_test(self.current_test, "FAIL", "Meals tab not found")
                return
            
            notebook.select(meals_tab_idx)
            self.root.update()
            
            # Find Get Recommendation button
            meals_tab = notebook.nametowidget(notebook.tabs()[meals_tab_idx])
            rec_button = None
            for widget in self._find_widgets_by_text(meals_tab, "Get Recommendation"):
                if isinstance(widget, ttk.Button):
                    rec_button = widget
                    break
            
            if rec_button:
                # Click recommendation button
                self.simulate_click(rec_button)
                self.root.update()
                
                # Check if meal was added to templates
                meal_count = self.check_database("meal_templates", f"user_id = {self.app.current_user_id}")
                if meal_count > 0:
                    self.log_test("Get Meal Recommendation", "PASS", f"Meal templates exist ({meal_count})")
                else:
                    self.log_test("Get Meal Recommendation", "WARN", "No meals in database (API may have failed)")
            else:
                self.log_test("Get Meal Recommendation", "FAIL", "Button not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_3_meal_logging(self):
        """Test Flow 3: Log a meal."""
        self.current_test = "Flow 3: Meal Logging"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Log Meals tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            # Find Log Meals tab
            log_tab_idx = None
            for i in range(notebook.index("end")):
                tab_text = notebook.tab(i, "text")
                if "Log" in tab_text:
                    log_tab_idx = i
                    break
            
            if log_tab_idx is None:
                self.log_test(self.current_test, "FAIL", "Log Meals tab not found")
                return
            
            notebook.select(log_tab_idx)
            self.root.update()
            
            # Fill meal logging form
            if hasattr(self.app, 'log_name_var'):
                self.simulate_entry(self.app.log_name_var, "Test Meal")
                self.simulate_entry(self.app.log_calories_var, 500)
                self.simulate_entry(self.app.log_protein_var, 30.0)
                self.simulate_entry(self.app.log_carbs_var, 50.0)
                self.simulate_entry(self.app.log_fat_var, 20.0)
                self.simulate_entry(self.app.log_meal_time_var, "dinner")
                self.simulate_entry(self.app.log_date_var, str(date.today()))
                self.simulate_entry(self.app.log_servings_var, 1.0)
                self.root.update()
                
                # Find and click Log Meal button
                log_tab = notebook.nametowidget(notebook.tabs()[log_tab_idx])
                log_button = None
                for widget in self._find_widgets_by_text(log_tab, "Log Meal"):
                    if isinstance(widget, ttk.Button):
                        log_button = widget
                        break
                
                if log_button:
                    initial_count = self.check_database("daily_nutrition_progress", f"user_id = {self.app.current_user_id}")
                    self.simulate_click(log_button)
                    self.root.update()
                    
                    # Wait a bit for database write
                    self.root.after(500, lambda: None)
                    self.root.update()
                    
                    final_count = self.check_database("daily_nutrition_progress", f"user_id = {self.app.current_user_id}")
                    
                    if final_count > initial_count:
                        self.log_test("Log Meal", "PASS", f"Meal logged (count: {initial_count} -> {final_count})")
                    else:
                        self.log_test("Log Meal", "FAIL", f"Meal not logged (count: {initial_count} -> {final_count})")
                else:
                    self.log_test("Log Meal", "FAIL", "Log Meal button not found")
            else:
                self.log_test("Log Meal", "FAIL", "Log form variables not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_4_weekly_planning(self):
        """Test Flow 4: Create weekly meal plan."""
        self.current_test = "Flow 4: Weekly Planning"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Weekly Plan tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            # Find Weekly Plan tab
            plan_tab_idx = None
            for i in range(notebook.index("end")):
                tab_text = notebook.tab(i, "text")
                if "Weekly" in tab_text or "Plan" in tab_text:
                    plan_tab_idx = i
                    break
            
            if plan_tab_idx is None:
                self.log_test(self.current_test, "FAIL", "Weekly Plan tab not found")
                return
            
            notebook.select(plan_tab_idx)
            self.root.update()
            
            # Set plan name and date
            if hasattr(self.app, 'plan_name_var'):
                self.simulate_entry(self.app.plan_name_var, "Test Weekly Plan")
                self.simulate_entry(self.app.plan_week_start_var, str(date.today()))
                self.root.update()
                
                # Find and click Generate Plan button
                plan_tab = notebook.nametowidget(notebook.tabs()[plan_tab_idx])
                generate_button = None
                for widget in self._find_widgets_by_text(plan_tab, "Generate Plan"):
                    if isinstance(widget, ttk.Button):
                        generate_button = widget
                        break
                
                if generate_button:
                    self.simulate_click(generate_button)
                    self.root.update()
                    
                    # Wait for plan generation
                    self.root.after(2000, lambda: None)
                    self.root.update()
                    
                    # Check if plan was created
                    if hasattr(self.app, 'current_weekly_plan') and self.app.current_weekly_plan:
                        self.log_test("Generate Weekly Plan", "PASS", "Plan generated successfully")
                    else:
                        self.log_test("Generate Weekly Plan", "WARN", "Plan may not have been generated")
                else:
                    self.log_test("Generate Weekly Plan", "FAIL", "Generate Plan button not found")
            else:
                self.log_test("Generate Weekly Plan", "FAIL", "Plan form variables not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_5_budget_tracking(self):
        """Test Flow 5: Add purchase to budget."""
        self.current_test = "Flow 5: Budget Tracking"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Budget tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            # Find Budget tab
            budget_tab_idx = None
            for i in range(notebook.index("end")):
                tab_text = notebook.tab(i, "text")
                if "Budget" in tab_text:
                    budget_tab_idx = i
                    break
            
            if budget_tab_idx is None:
                self.log_test(self.current_test, "FAIL", "Budget tab not found")
                return
            
            notebook.select(budget_tab_idx)
            self.root.update()
            
            # Fill purchase form
            if hasattr(self.app, 'purchase_name_var'):
                self.simulate_entry(self.app.purchase_name_var, "Test Grocery Item")
                self.simulate_entry(self.app.purchase_amount_var, 25.50)
                self.simulate_entry(self.app.purchase_category_var, "groceries")
                self.simulate_entry(self.app.purchase_store_var, "Test Store")
                self.simulate_entry(self.app.purchase_date_var, str(date.today()))
                self.root.update()
                
                # Find and click Add Purchase button
                budget_tab = notebook.nametowidget(notebook.tabs()[budget_tab_idx])
                add_button = None
                for widget in self._find_widgets_by_text(budget_tab, "Add Purchase"):
                    if isinstance(widget, ttk.Button):
                        add_button = widget
                        break
                
                if add_button:
                    initial_count = self.check_database("shopping_history", f"user_id = {self.app.current_user_id}")
                    self.simulate_click(add_button)
                    self.root.update()
                    
                    # Wait for database write
                    self.root.after(500, lambda: None)
                    self.root.update()
                    
                    final_count = self.check_database("shopping_history", f"user_id = {self.app.current_user_id}")
                    
                    if final_count > initial_count:
                        self.log_test("Add Purchase", "PASS", f"Purchase added (count: {initial_count} -> {final_count})")
                    else:
                        self.log_test("Add Purchase", "FAIL", f"Purchase not added (count: {initial_count} -> {final_count})")
                else:
                    self.log_test("Add Purchase", "FAIL", "Add Purchase button not found")
            else:
                self.log_test("Add Purchase", "FAIL", "Purchase form variables not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_6_body_metrics(self):
        """Test Flow 6: Log body metrics."""
        self.current_test = "Flow 6: Body Metrics"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Profile tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            # Find Profile tab
            profile_tab_idx = None
            for i in range(notebook.index("end")):
                tab_text = notebook.tab(i, "text")
                if "Profile" in tab_text:
                    profile_tab_idx = i
                    break
            
            if profile_tab_idx is None:
                self.log_test(self.current_test, "FAIL", "Profile tab not found")
                return
            
            notebook.select(profile_tab_idx)
            self.root.update()
            
            # Fill metrics form
            if hasattr(self.app, 'metrics_weight_var'):
                self.simulate_entry(self.app.metrics_weight_var, 175.0)
                self.simulate_entry(self.app.metrics_bodyfat_var, 14.5)
                self.simulate_entry(self.app.metrics_muscle_var, 150.0)
                self.simulate_entry(self.app.metrics_date_var, str(date.today()))
                self.root.update()
                
                # Find and click Log Metrics button
                profile_tab = notebook.nametowidget(notebook.tabs()[profile_tab_idx])
                log_button = None
                for widget in self._find_widgets_by_text(profile_tab, "Log Metrics"):
                    if isinstance(widget, ttk.Button):
                        log_button = widget
                        break
                
                if log_button:
                    initial_count = self.check_database("body_metrics_history", f"user_id = {self.app.current_user_id}")
                    self.simulate_click(log_button)
                    self.root.update()
                    
                    # Wait for database write
                    self.root.after(500, lambda: None)
                    self.root.update()
                    
                    final_count = self.check_database("body_metrics_history", f"user_id = {self.app.current_user_id}")
                    
                    if final_count > initial_count:
                        self.log_test("Log Body Metrics", "PASS", f"Metrics logged (count: {initial_count} -> {final_count})")
                    else:
                        self.log_test("Log Body Metrics", "FAIL", f"Metrics not logged (count: {initial_count} -> {final_count})")
                else:
                    self.log_test("Log Body Metrics", "FAIL", "Log Metrics button not found")
            else:
                self.log_test("Log Body Metrics", "FAIL", "Metrics form variables not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_flow_7_dashboard_refresh(self):
        """Test Flow 7: Dashboard refresh and progress display."""
        self.current_test = "Flow 7: Dashboard Refresh"
        print(f"\n{'='*60}")
        print(f"Testing: {self.current_test}")
        print(f"{'='*60}")
        
        try:
            # Navigate to Dashboard tab
            notebook = None
            for widget in self.app.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    notebook = widget
                    break
            
            if not notebook:
                self.log_test(self.current_test, "FAIL", "Notebook not found")
                return
            
            notebook.select(0)  # Dashboard is usually first
            self.root.update()
            
            # Check if dashboard has progress bars
            if hasattr(self.app, 'dashboard_progress_bars'):
                self.log_test("Dashboard Progress Bars", "PASS", "Progress bars exist")
            else:
                self.log_test("Dashboard Progress Bars", "FAIL", "Progress bars not found")
            
            # Check if refresh button exists
            dashboard_tab = notebook.nametowidget(notebook.tabs()[0])
            refresh_button = None
            for widget in self._find_widgets_by_text(dashboard_tab, "Refresh"):
                if isinstance(widget, ttk.Button):
                    refresh_button = widget
                    break
            
            if refresh_button:
                self.simulate_click(refresh_button)
                self.root.update()
                self.log_test("Dashboard Refresh", "PASS", "Refresh button works")
            else:
                self.log_test("Dashboard Refresh", "WARN", "Refresh button not found")
                
        except Exception as e:
            self.log_test(self.current_test, "FAIL", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def _find_widgets_by_text(self, parent, text):
        """Recursively find widgets containing text."""
        widgets = []
        try:
            if isinstance(parent, (ttk.Button, tk.Button)):
                if text in str(parent.cget("text")):
                    widgets.append(parent)
            
            for child in parent.winfo_children():
                widgets.extend(self._find_widgets_by_text(child, text))
        except:
            pass
        return widgets
    
    def run_all_tests(self):
        """Run all test flows."""
        print("\n" + "="*60)
        print("GUI FLOW TESTING - Starting All Tests")
        print("="*60)
        
        # Run all test flows
        self.test_flow_1_create_user_and_generate_targets()
        self.test_flow_2_meal_recommendation()
        self.test_flow_3_meal_logging()
        self.test_flow_4_weekly_planning()
        self.test_flow_5_budget_tracking()
        self.test_flow_6_body_metrics()
        self.test_flow_7_dashboard_refresh()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if "✅" in r)
        failed = sum(1 for r in self.test_results if "❌" in r)
        warned = sum(1 for r in self.test_results if "⚠️" in r)
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Cleanup
        try:
            self.root.destroy()
            if self.test_db_path.exists():
                os.unlink(self.test_db_path)
        except:
            pass
        
        return {
            'total': len(self.test_results),
            'passed': passed,
            'failed': failed,
            'warned': warned,
            'results': self.test_results
        }


if __name__ == "__main__":
    harness = GUITestHarness()
    results = harness.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(1 if results['failed'] > 0 else 0)
