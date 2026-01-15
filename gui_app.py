#!/usr/bin/env python3
"""
Macro Chef GUI Application
A user-friendly graphical interface for the Macro Chef meal planning system.

Usage: python gui_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
from datetime import date, timedelta
import sqlite3

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from scripts.user_profile import UserProfileManager
from scripts.nutrition_calculator import NutritionCalculator
from scripts.meal_recommender import MealRecommender
from scripts.inventory_manager import InventoryManager
from scripts.db_manager import DatabaseManager
from config.config import DATABASE_PATH
import scripts.db_setup as db_setup


class MacroChefGUI:
    """Main GUI application for Macro Chef."""

    def __init__(self, root, db_path=None):
        self.root = root
        self.root.title("Macro Chef - Meal Planning & Nutrition Tracker")
        self.root.geometry("1000x700")

        # Determine database path
        self.db_path = db_path if db_path else DATABASE_PATH
        
        # Initialize database if needed
        self.ensure_database_initialized()
        
        # Initialize managers with optional database path
        if db_path:
            self.user_manager = UserProfileManager(db_path=db_path)
            self.nutrition_calc = NutritionCalculator()  # Uses default path internally
            self.meal_recommender = MealRecommender()  # Uses default path internally
            self.inventory_manager = InventoryManager(db_path=db_path)
            self.db_manager = DatabaseManager(db_path=db_path)
        else:
            self.user_manager = UserProfileManager()
            self.nutrition_calc = NutritionCalculator()
            self.meal_recommender = MealRecommender()
            self.inventory_manager = InventoryManager()
            self.db_manager = DatabaseManager()

        # Current user
        self.current_user_id = None
        self.current_user_profile = None

        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_user()

    def ensure_database_initialized(self):
        """Check if database tables exist and create them if needed."""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if user_profile table exists
            db_manager = DatabaseManager(db_path=self.db_path)
            table_exists = False
            try:
                table_exists = db_manager.table_exists('user_profile')
            except Exception:
                # Table doesn't exist or database is empty, will initialize
                pass
            
            if not table_exists:
                # Database not initialized, create all tables
                conn = sqlite3.connect(self.db_path)
                try:
                    db_setup.create_tables(conn)
                    print(f"[INFO] Database initialized at: {self.db_path}")
                except Exception as e:
                    messagebox.showerror(
                        "Database Error",
                        f"Failed to initialize database: {e}\n\n"
                        "Please ensure you have write permissions to the database directory."
                    )
                    raise
                finally:
                    conn.close()
            db_manager.disconnect()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to check/initialize database: {e}\n\n"
                "The application may not work correctly."
            )

    def setup_styles(self):
        """Configure ttk styles for better appearance."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Helvetica', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Helvetica', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Helvetica', 10), foreground='#27ae60')
        style.configure('Warning.TLabel', font=('Helvetica', 10), foreground='#e74c3c')

        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))

    def create_widgets(self):
        """Create main UI components."""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill='x')

        ttk.Label(
            header_frame,
            text=" Macro Chef",
            style='Title.TLabel'
        ).pack(side='left')

        self.user_label = ttk.Label(
            header_frame,
            text="No user profile loaded",
            style='Info.TLabel'
        )
        self.user_label.pack(side='right')

        # Tab control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self.create_dashboard_tab()
        self.create_profile_tab()
        self.create_meals_tab()
        self.create_inventory_tab()
        self.create_search_tab()

        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief='sunken',
            anchor='w'
        )
        self.status_bar.pack(fill='x', side='bottom')

    def create_dashboard_tab(self):
        """Create dashboard overview tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Dashboard")

        # Daily targets section
        targets_frame = ttk.LabelFrame(tab, text="Today's Nutrition Targets", padding="10")
        targets_frame.pack(fill='x', pady=5)

        self.targets_text = scrolledtext.ScrolledText(
            targets_frame,
            height=8,
            width=80,
            font=('Courier', 10),
            state='disabled'
        )
        self.targets_text.pack(fill='both', expand=True)

        # Quick stats section
        stats_frame = ttk.LabelFrame(tab, text="Quick Stats", padding="10")
        stats_frame.pack(fill='both', expand=True, pady=5)

        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            height=10,
            width=80,
            font=('Courier', 10),
            state='disabled'
        )
        self.stats_text.pack(fill='both', expand=True)

        # Refresh button
        ttk.Button(
            tab,
            text=" Refresh Dashboard",
            style='Action.TButton',
            command=self.refresh_dashboard
        ).pack(pady=5)

    def create_profile_tab(self):
        """Create user profile management tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Profile")

        # Profile info section
        info_frame = ttk.LabelFrame(tab, text="User Profile", padding="10")
        info_frame.pack(fill='x', pady=5)

        # Form fields
        fields_frame = ttk.Frame(info_frame)
        fields_frame.pack(fill='x')

        # Name
        ttk.Label(fields_frame, text="Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=2)

        # Age
        ttk.Label(fields_frame, text="Age:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.age_var = tk.IntVar(value=30)
        ttk.Spinbox(fields_frame, from_=18, to=100, textvariable=self.age_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        # Sex
        ttk.Label(fields_frame, text="Sex:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.sex_var = tk.StringVar(value="male")
        ttk.Combobox(fields_frame, textvariable=self.sex_var, values=["male", "female"], width=27, state='readonly').grid(row=1, column=1, padx=5, pady=2)

        # Height
        ttk.Label(fields_frame, text="Height (inches):").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.height_var = tk.IntVar(value=70)
        ttk.Spinbox(fields_frame, from_=48, to=84, textvariable=self.height_var, width=10).grid(row=1, column=3, padx=5, pady=2)

        # Weight
        ttk.Label(fields_frame, text="Weight (lbs):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.weight_var = tk.IntVar(value=180)
        ttk.Spinbox(fields_frame, from_=80, to=400, textvariable=self.weight_var, width=27).grid(row=2, column=1, padx=5, pady=2)

        # Body fat %
        ttk.Label(fields_frame, text="Body Fat % (optional):").grid(row=2, column=2, sticky='w', padx=5, pady=2)
        self.bodyfat_var = tk.DoubleVar(value=15.0)
        ttk.Spinbox(fields_frame, from_=5, to=50, textvariable=self.bodyfat_var, width=10, increment=0.5).grid(row=2, column=3, padx=5, pady=2)

        # Goal type
        ttk.Label(fields_frame, text="Goal:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.goal_var = tk.StringVar(value="maintain")
        ttk.Combobox(fields_frame, textvariable=self.goal_var, values=["bulk", "cut", "maintain", "recomp"], width=27, state='readonly').grid(row=3, column=1, padx=5, pady=2)

        # Activity level
        ttk.Label(fields_frame, text="Activity Level:").grid(row=3, column=2, sticky='w', padx=5, pady=2)
        self.activity_var = tk.StringVar(value="moderate")
        ttk.Combobox(fields_frame, textvariable=self.activity_var, values=["sedentary", "light", "moderate", "very_active", "athlete"], width=10, state='readonly').grid(row=3, column=3, padx=5, pady=2)

        # Training days
        ttk.Label(fields_frame, text="Training Days/Week:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.training_days_var = tk.IntVar(value=3)
        ttk.Spinbox(fields_frame, from_=0, to=7, textvariable=self.training_days_var, width=27).grid(row=4, column=1, padx=5, pady=2)

        # Budget
        ttk.Label(fields_frame, text="Weekly Budget ($):").grid(row=4, column=2, sticky='w', padx=5, pady=2)
        self.budget_var = tk.DoubleVar(value=100.0)
        ttk.Spinbox(fields_frame, from_=20, to=500, textvariable=self.budget_var, width=10, increment=5).grid(row=4, column=3, padx=5, pady=2)

        # Buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(
            button_frame,
            text=" Save Profile",
            style='Action.TButton',
            command=self.save_profile
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text=" Load Profile",
            command=self.load_user
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text=" Generate Targets",
            command=self.generate_targets
        ).pack(side='left', padx=5)

    def create_meals_tab(self):
        """Create meal templates tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Meals")

        # Meal list section
        list_frame = ttk.LabelFrame(tab, text="Saved Meal Templates", padding="10")
        list_frame.pack(fill='both', expand=True, pady=5)

        # Treeview for meals
        columns = ('ID', 'Name', 'Type', 'Calories', 'Protein', 'Carbs', 'Fat')
        self.meals_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.meals_tree.heading(col, text=col)
            width = 80 if col == 'ID' else (200 if col == 'Name' else 100)
            self.meals_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.meals_tree.yview)
        self.meals_tree.configure(yscrollcommand=scrollbar.set)

        self.meals_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(
            button_frame,
            text=" Refresh Meals",
            command=self.refresh_meals
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text=" Get Recommendation",
            style='Action.TButton',
            command=self.get_meal_recommendation
        ).pack(side='left', padx=5)

    def create_inventory_tab(self):
        """Create inventory management tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Inventory")

        # Inventory list section
        list_frame = ttk.LabelFrame(tab, text="Current Inventory", padding="10")
        list_frame.pack(fill='both', expand=True, pady=5)

        # Treeview for inventory
        columns = ('ID', 'Item', 'Quantity', 'Unit', 'Category', 'Location', 'Expires')
        self.inventory_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.inventory_tree.heading(col, text=col)
            width = 60 if col == 'ID' else (150 if col == 'Item' else 100)
            self.inventory_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Add item section
        add_frame = ttk.LabelFrame(tab, text="Add Item", padding="10")
        add_frame.pack(fill='x', pady=5)

        # Form fields
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')

        ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.inv_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.inv_name_var, width=25).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Quantity:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.inv_qty_var = tk.DoubleVar(value=1.0)
        ttk.Entry(form_frame, textvariable=self.inv_qty_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form_frame, text="Unit:").grid(row=0, column=4, sticky='w', padx=5, pady=2)
        self.inv_unit_var = tk.StringVar(value="lbs")
        ttk.Combobox(form_frame, textvariable=self.inv_unit_var, values=["lbs", "oz", "g", "kg", "count", "cups"], width=8, state='readonly').grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.inv_cat_var = tk.StringVar(value="protein")
        ttk.Combobox(form_frame, textvariable=self.inv_cat_var, values=["protein", "carbs", "vegetable", "fruit", "dairy", "grain", "fat", "snack", "other"], width=22, state='readonly').grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Location:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.inv_loc_var = tk.StringVar(value="fridge")
        ttk.Combobox(form_frame, textvariable=self.inv_loc_var, values=["fridge", "freezer", "pantry", "counter"], width=8, state='readonly').grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(form_frame, text="Days Until Expiry:").grid(row=1, column=4, sticky='w', padx=5, pady=2)
        self.inv_days_var = tk.IntVar(value=7)
        ttk.Spinbox(form_frame, from_=1, to=365, textvariable=self.inv_days_var, width=8).grid(row=1, column=5, padx=5, pady=2)

        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(
            button_frame,
            text=" Add Item",
            style='Action.TButton',
            command=self.add_inventory_item
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text=" Refresh List",
            command=self.refresh_inventory
        ).pack(side='left', padx=5)

    def create_search_tab(self):
        """Create online recipe search tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Search Recipes")

        # Search section
        search_frame = ttk.LabelFrame(tab, text="Search Online Recipes", padding="10")
        search_frame.pack(fill='x', pady=5)

        # Search bar
        search_bar_frame = ttk.Frame(search_frame)
        search_bar_frame.pack(fill='x', pady=5)

        ttk.Label(search_bar_frame, text="Search Query:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_bar_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', padx=5)

        ttk.Button(
            search_bar_frame,
            text=" Search",
            style='Action.TButton',
            command=self.search_recipes
        ).pack(side='left', padx=5)

        # Filters
        filters_frame = ttk.Frame(search_frame)
        filters_frame.pack(fill='x', pady=5)

        ttk.Label(filters_frame, text="Max Calories:").grid(row=0, column=0, sticky='w', padx=5)
        self.search_cal_var = tk.IntVar(value=800)
        ttk.Spinbox(filters_frame, from_=100, to=2000, textvariable=self.search_cal_var, width=10, increment=50).grid(row=0, column=1, padx=5)

        ttk.Label(filters_frame, text="Min Protein (g):").grid(row=0, column=2, sticky='w', padx=5)
        self.search_protein_var = tk.IntVar(value=20)
        ttk.Spinbox(filters_frame, from_=0, to=100, textvariable=self.search_protein_var, width=10, increment=5).grid(row=0, column=3, padx=5)

        ttk.Label(filters_frame, text="Max Time (min):").grid(row=0, column=4, sticky='w', padx=5)
        self.search_time_var = tk.IntVar(value=45)
        ttk.Spinbox(filters_frame, from_=5, to=180, textvariable=self.search_time_var, width=10, increment=5).grid(row=0, column=5, padx=5)

        # Results section
        results_frame = ttk.LabelFrame(tab, text="Search Results", padding="10")
        results_frame.pack(fill='both', expand=True, pady=5)

        self.search_results_text = scrolledtext.ScrolledText(
            results_frame,
            height=20,
            width=90,
            font=('Courier', 9)
        )
        self.search_results_text.pack(fill='both', expand=True)

    def load_user(self):
        """Load the default user profile."""
        try:
            # Try to get current user or default to user ID 1
            user_id_to_load = self.current_user_id if self.current_user_id else 1
            profile = self.user_manager.get_user(user_id_to_load)

            if profile:
                self.current_user_id = user_id_to_load
                self.current_user_profile = profile

                # Update form fields
                self.name_var.set(profile.get('name', ''))
                self.age_var.set(profile.get('age', 30))
                self.sex_var.set(profile.get('sex', 'male'))
                self.height_var.set(profile.get('height_inches', 70))
                self.weight_var.set(profile.get('weight_lbs', 180))
                self.bodyfat_var.set(profile.get('body_fat_pct', 15.0) or 15.0)
                self.goal_var.set(profile.get('goal_type', 'maintain'))
                self.activity_var.set(profile.get('activity_level', 'moderate'))
                self.training_days_var.set(profile.get('training_days_per_week', 3) or 3)
                self.budget_var.set(profile.get('weekly_budget_usd', 100.0) or 100.0)

                self.user_label.config(text=f"User: {profile['name']}")
                self.status_bar.config(text=f"Loaded profile: {profile['name']}")
                self.root.update_idletasks()  # Ensure status bar updates immediately
                self.refresh_dashboard()
            else:
                self.user_label.config(text="No user profile found")
                self.status_bar.config(text="No user profile found - please create one")
                self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user profile: {e}")

    def save_profile(self):
        """Save or update user profile."""
        try:
            name = self.name_var.get()
            if not name:
                messagebox.showwarning("Warning", "Please enter a name")
                return

            if self.current_user_id:
                # Update existing profile
                self.user_manager.update_user(
                    user_id=self.current_user_id,
                    name=name,
                    age=self.age_var.get(),
                    sex=self.sex_var.get(),
                    height_inches=self.height_var.get(),
                    weight_lbs=self.weight_var.get(),
                    body_fat_pct=self.bodyfat_var.get(),
                    goal_type=self.goal_var.get(),
                    activity_level=self.activity_var.get(),
                    training_days_per_week=self.training_days_var.get(),
                    weekly_budget_usd=self.budget_var.get()
                )
                messagebox.showinfo("Success", "Profile updated successfully!")
            else:
                # Create new profile
                user_id = self.user_manager.create_user(
                    name=name,
                    age=self.age_var.get(),
                    sex=self.sex_var.get(),
                    height_inches=self.height_var.get(),
                    weight_lbs=self.weight_var.get(),
                    body_fat_pct=self.bodyfat_var.get(),
                    goal_type=self.goal_var.get(),
                    activity_level=self.activity_var.get(),
                    training_days_per_week=self.training_days_var.get(),
                    weekly_budget_usd=self.budget_var.get()
                )
                self.current_user_id = user_id
                messagebox.showinfo("Success", f"Profile created successfully! User ID: {user_id}")

            self.load_user()
            self.status_bar.config(text="Profile saved successfully")
            self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    def generate_targets(self):
        """Generate daily nutrition targets."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return

        try:
            # Generate targets (returns dict with user_id, date, and all target values)
            targets = self.nutrition_calc.generate_daily_targets(
                user_id=self.current_user_id,
                target_date=date.today(),
                is_training_day=False
            )

            # Save targets to database
            target_id = self.nutrition_calc.save_daily_targets(targets, self.current_user_id)

            if target_id:
                messagebox.showinfo("Success", "Daily targets generated successfully!")
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", "Failed to save targets")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate targets: {e}")

    def refresh_dashboard(self):
        """Refresh dashboard with current data."""
        if not self.current_user_id:
            return

        try:
            # Get today's targets
            targets = self.nutrition_calc.get_daily_targets(self.current_user_id, date.today())

            self.targets_text.config(state='normal')
            self.targets_text.delete('1.0', tk.END)

            if targets:
                output = "═" * 70 + "\n"
                output += "  TODAY'S NUTRITION TARGETS\n"
                output += "═" * 70 + "\n\n"
                output += f"   Calories:      {targets.get('calories_target', 0):,} kcal\n\n"
                output += "  MACRONUTRIENTS:\n"
                output += f"    • Protein:      {targets.get('protein_target_g', 0)}g\n"
                output += f"    • Carbs:        {targets.get('carbs_target_g', 0)}g\n"
                output += f"    • Fat:          {targets.get('fat_target_g', 0)}g\n"
                output += f"    • Fiber:        {targets.get('fiber_target_g', 0)}g\n\n"
            else:
                output = "\n  No targets generated for today.\n"
                output += "  Click 'Generate Targets' in the Profile tab to create them.\n\n"

            self.targets_text.insert('1.0', output)
            self.targets_text.config(state='disabled')

            # Get stats
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', tk.END)

            stats_output = "═" * 70 + "\n"
            stats_output += "  QUICK STATS\n"
            stats_output += "═" * 70 + "\n\n"

            # Get meal count
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM meal_templates WHERE user_id = ?", (self.current_user_id,))
            meal_count = cursor.fetchone()[0]

            # Get inventory count (filter by user_id)
            user_id = self.current_user_id if self.current_user_id else 1
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE user_id = ?", (user_id,))
            inv_count = cursor.fetchone()[0]
            conn.close()

            stats_output += f"   Saved Meals:       {meal_count}\n"
            stats_output += f"   Inventory Items:   {inv_count}\n"
            stats_output += f"   Goal:              {self.goal_var.get().upper()}\n"
            stats_output += f"   Activity Level:    {self.activity_var.get()}\n\n"

            self.stats_text.insert('1.0', stats_output)
            self.stats_text.config(state='disabled')

            self.status_bar.config(text="Dashboard refreshed")
            self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dashboard: {e}")

    def refresh_meals(self):
        """Refresh meals list."""
        try:
            # Clear existing items
            for item in self.meals_tree.get_children():
                self.meals_tree.delete(item)

            # Get meals from database (filter by user_id if available)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_id = self.current_user_id if self.current_user_id else None
            if user_id:
                cursor.execute("""
                    SELECT id, name, meal_type, calories, protein_g, carbs_g, fat_g
                    FROM meal_templates
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 100
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT id, name, meal_type, calories, protein_g, carbs_g, fat_g
                    FROM meal_templates
                    ORDER BY id DESC
                    LIMIT 100
                """)

            meals = cursor.fetchall()
            conn.close()

            for meal in meals:
                self.meals_tree.insert('', 'end', values=meal)

            self.status_bar.config(text=f"Loaded {len(meals)} meals")
            self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            self.status_bar.config(text=f"Error loading meals: {e}")
            self.root.update_idletasks()  # Ensure status bar updates immediately
            messagebox.showerror("Error", f"Failed to load meals: {e}")

    def get_meal_recommendation(self):
        """Get meal recommendation based on targets."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return

        try:
            # Get today's targets (to verify they exist)
            targets = self.nutrition_calc.get_daily_targets(self.current_user_id, date.today())

            if not targets:
                messagebox.showwarning("Warning", "Please generate targets first (Profile tab)")
                return

            # Get recommendations (returns list of recommendations)
            recommendations = self.meal_recommender.recommend_meal(
                meal_time='dinner',
                user_id=self.current_user_id,
                target_date=date.today()
            )

            if recommendations:
                # Get top recommendation
                meal = recommendations[0]
                
                # Save recommended meal to database if it's an online recipe
                try:
                    saved_id = self.meal_recommender.save_recommended_meal(meal, self.current_user_id)
                    if saved_id:
                        self.status_bar.config(text=f"Saved meal '{meal['name']}' to database")
                        self.root.update_idletasks()
                except Exception as save_error:
                    print(f"[WARNING] Failed to save recommended meal: {save_error}")
                    # Continue even if save fails
                
                msg = f"Recommended Meal:\n\n"
                msg += f"Name: {meal['name']}\n"
                msg += f"Type: {meal.get('meal_type', 'dinner')}\n\n"
                msg += f"Calories: {meal['calories']} kcal\n"
                msg += f"Protein: {meal['protein_g']}g\n"
                msg += f"Carbs: {meal['carbs_g']}g\n"
                msg += f"Fat: {meal['fat_g']}g\n"
                
                # Add optional fields if available
                if meal.get('total_time_minutes'):
                    msg += f"\nTime: {meal['total_time_minutes']} minutes"
                if meal.get('cost_estimate_usd'):
                    msg += f"\nCost: ${meal['cost_estimate_usd']:.2f}"
                if meal.get('recommendation_score'):
                    msg += f"\nScore: {meal['recommendation_score']}/100"
                
                messagebox.showinfo("Meal Recommendation", msg)
            else:
                messagebox.showinfo("No Results", "No suitable meals found. Try searching online recipes!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get recommendation: {e}")

    def refresh_inventory(self):
        """Refresh inventory list."""
        try:
            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            # Get inventory items (use current user if available)
            user_id = self.current_user_id if self.current_user_id else 1
            items = self.inventory_manager.get_all_items(user_id=user_id)

            for item in items:
                self.inventory_tree.insert('', 'end', values=(
                    item['id'],
                    item['item_name'],
                    f"{item['quantity']:.1f}",
                    item['unit'],
                    item.get('category', 'N/A'),
                    item.get('location', 'N/A'),
                    item.get('expiration_date', 'N/A')
                ))

            self.status_bar.config(text=f"Loaded {len(items)} inventory items")
            self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            self.status_bar.config(text=f"Error loading inventory: {e}")
            self.root.update_idletasks()  # Ensure status bar updates immediately
            messagebox.showerror("Error", f"Failed to load inventory: {e}")

    def add_inventory_item(self):
        """Add item to inventory."""
        try:
            item_name = self.inv_name_var.get()
            if not item_name:
                messagebox.showwarning("Warning", "Please enter an item name")
                return

            expiration_date = date.today() + timedelta(days=self.inv_days_var.get())

            # Use current user if available, otherwise default to 1
            user_id = self.current_user_id if self.current_user_id else 1

            item_id = self.inventory_manager.add_item(
                item_name=item_name,
                quantity=self.inv_qty_var.get(),
                unit=self.inv_unit_var.get(),
                category=self.inv_cat_var.get(),
                location=self.inv_loc_var.get(),
                expiration_date=expiration_date,
                user_id=user_id
            )

            if item_id:
                messagebox.showinfo("Success", f"Added {item_name} to inventory!")
                self.inv_name_var.set("")
                self.refresh_inventory()
            else:
                messagebox.showerror("Error", "Failed to add item")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add inventory item: {e}")

    def search_recipes(self):
        """Search online recipes using Spoonacular API."""
        query = self.search_var.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return

        try:
            self.status_bar.config(text="Searching recipes...")
            self.root.update()

            results = self.meal_recommender.search_online_recipes(
                query=query,
                max_results=5,
                max_calories=self.search_cal_var.get(),
                min_protein=self.search_protein_var.get(),
                max_ready_time=self.search_time_var.get()
            )

            self.search_results_text.delete('1.0', tk.END)

            if results:
                output = f"Found {len(results)} recipes for '{query}':\n\n"
                output += "═" * 80 + "\n\n"

                for i, recipe in enumerate(results, 1):
                    output += f"{i}. {recipe['title']}\n"
                    output += f"   ID: {recipe['id']}\n"
                    output += f"   Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes\n"

                    if 'nutrition' in recipe:
                        nut = recipe['nutrition']
                        output += f"   Nutrition: {nut.get('calories', 0):.0f} cal | "
                        output += f"{nut.get('protein', 0):.0f}g protein | "
                        output += f"{nut.get('carbs', 0):.0f}g carbs | "
                        output += f"{nut.get('fat', 0):.0f}g fat\n"

                    if recipe.get('is_validated'):
                        output += f"    Nutrition validated with USDA\n"

                    output += "\n" + "─" * 80 + "\n\n"

                self.search_results_text.insert('1.0', output)
                self.status_bar.config(text=f"Found {len(results)} recipes")
                self.root.update_idletasks()  # Ensure status bar updates immediately
            else:
                self.search_results_text.insert('1.0', f"No recipes found for '{query}'")
                self.status_bar.config(text="No results found")
                self.root.update_idletasks()  # Ensure status bar updates immediately

        except Exception as e:
            self.status_bar.config(text="Search failed")
            self.root.update_idletasks()  # Ensure status bar updates immediately
            messagebox.showerror("Error", f"Search failed: {e}")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = MacroChefGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
