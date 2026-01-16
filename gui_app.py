#!/usr/bin/env python3
"""
Macro Chef GUI Application
A user-friendly graphical interface for the Macro Chef meal planning system.

Usage: python gui_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
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


class DeveloperGUI:
    """Developer GUI for database management and inspection."""
    
    def __init__(self, root, db_path=None):
        self.root = root
        self.root.title("Macro Chef - Developer Mode")
        self.root.geometry("1200x800")
        
        # Determine database path
        self.db_path = db_path if db_path else DATABASE_PATH
        
        # Current state
        self.current_table = None
        self.read_only_mode = False
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_table_list()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """Create main UI components."""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill='x')
        
        ttk.Label(
            header_frame,
            text=" Developer Mode - Database Manager",
            font=('Helvetica', 14, 'bold')
        ).pack(side='left')
        
        # Read-only toggle
        self.read_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            header_frame,
            text="Read-Only Mode",
            variable=self.read_only_var,
            command=self.toggle_read_only
        ).pack(side='right', padx=10)
        
        # Status bar (create before tabs so methods can use it)
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief='sunken',
            anchor='w'
        )
        self.status_bar.pack(fill='x', side='bottom')
        
        # Tab control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_table_browser_tab()
        self.create_schema_tab()
        self.create_sql_tab()
    
    def toggle_read_only(self):
        """Toggle read-only mode."""
        self.read_only_mode = self.read_only_var.get()
        mode = "Read-Only" if self.read_only_mode else "Edit Mode"
        self.status_bar.config(text=f"Mode: {mode}")
        self.root.update_idletasks()
    
    def load_table_list(self):
        """Load list of all tables from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Populate table list
            self.table_listbox.delete(0, tk.END)
            for table in tables:
                self.table_listbox.insert(tk.END, table)
            
            self.status_bar.config(text=f"Loaded {len(tables)} tables")
            self.root.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table list: {e}")
    
    def create_table_browser_tab(self):
        """Create table browser tab with table list and data viewer."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Table Browser")
        
        # Main container with table list and data viewer
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        # Left panel: Table list
        left_frame = ttk.LabelFrame(main_frame, text="Tables", padding="5")
        left_frame.pack(side='left', fill='both', padx=(0, 5))
        left_frame.config(width=200)
        
        # Table listbox
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        scrollbar1 = ttk.Scrollbar(listbox_frame)
        scrollbar1.pack(side='right', fill='y')
        
        self.table_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar1.set)
        self.table_listbox.pack(side='left', fill='both', expand=True)
        scrollbar1.config(command=self.table_listbox.yview)
        
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Refresh button
        ttk.Button(
            left_frame,
            text=" Refresh Tables",
            command=self.load_table_list
        ).pack(pady=5)
        
        # Right panel: Data viewer
        right_frame = ttk.LabelFrame(main_frame, text="Table Data", padding="5")
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill='x', pady=(0, 5))
        
        ttk.Button(toolbar, text=" Refresh", command=self.refresh_table_data).pack(side='left', padx=2)
        ttk.Button(toolbar, text=" Add Row", command=self.add_table_row).pack(side='left', padx=2)
        ttk.Button(toolbar, text=" Edit Row", command=self.edit_table_row).pack(side='left', padx=2)
        ttk.Button(toolbar, text=" Delete Row", command=self.delete_table_row).pack(side='left', padx=2)
        ttk.Button(toolbar, text=" Export CSV", command=self.export_table_csv).pack(side='left', padx=2)
        
        # Row count label
        self.row_count_label = ttk.Label(toolbar, text="Rows: 0")
        self.row_count_label.pack(side='right', padx=5)
        
        # Data treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar2 = ttk.Scrollbar(tree_frame, orient='vertical')
        scrollbar3 = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        self.data_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar2.set, xscrollcommand=scrollbar3.set)
        scrollbar2.config(command=self.data_tree.yview)
        scrollbar3.config(command=self.data_tree.xview)
        
        self.data_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        scrollbar3.pack(side='bottom', fill='x')
        
        self.data_tree.bind('<Double-1>', lambda e: self.edit_table_row())
    
    def create_schema_tab(self):
        """Create schema viewer tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Schema")
        
        # Table selector
        selector_frame = ttk.Frame(tab)
        selector_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(selector_frame, text="Table:").pack(side='left', padx=5)
        self.schema_table_var = tk.StringVar()
        schema_combo = ttk.Combobox(selector_frame, textvariable=self.schema_table_var, width=30, state='readonly')
        schema_combo.pack(side='left', padx=5)
        schema_combo.bind('<<ComboboxSelected>>', lambda e: self.show_table_schema())
        
        ttk.Button(selector_frame, text=" Refresh", command=self.load_schema_tables).pack(side='left', padx=5)
        
        self.schema_combo = schema_combo
        
        # Schema display
        schema_frame = ttk.LabelFrame(tab, text="Table Schema", padding="10")
        schema_frame.pack(fill='both', expand=True)
        
        self.schema_text = scrolledtext.ScrolledText(
            schema_frame,
            font=('Courier', 10),
            wrap='none'
        )
        self.schema_text.pack(fill='both', expand=True)
        
        # Load tables into combo
        self.load_schema_tables()
    
    def create_sql_tab(self):
        """Create SQL query tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" SQL Query")
        
        # Query editor
        editor_frame = ttk.LabelFrame(tab, text="SQL Query", padding="5")
        editor_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.sql_text = scrolledtext.ScrolledText(
            editor_frame,
            font=('Courier', 11),
            height=8
        )
        self.sql_text.pack(fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(button_frame, text=" Execute", command=self.execute_sql_query).pack(side='left', padx=2)
        ttk.Button(button_frame, text=" Clear", command=lambda: self.sql_text.delete('1.0', tk.END)).pack(side='left', padx=2)
        
        # Results
        results_frame = ttk.LabelFrame(tab, text="Results", padding="5")
        results_frame.pack(fill='both', expand=True)
        
        # Results treeview
        results_tree_frame = ttk.Frame(results_frame)
        results_tree_frame.pack(fill='both', expand=True)
        
        scrollbar4 = ttk.Scrollbar(results_tree_frame, orient='vertical')
        scrollbar5 = ttk.Scrollbar(results_tree_frame, orient='horizontal')
        
        self.results_tree = ttk.Treeview(results_tree_frame, yscrollcommand=scrollbar4.set, xscrollcommand=scrollbar5.set)
        scrollbar4.config(command=self.results_tree.yview)
        scrollbar5.config(command=self.results_tree.xview)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar4.pack(side='right', fill='y')
        scrollbar5.pack(side='bottom', fill='x')
    
    def load_schema_tables(self):
        """Load table names into schema combo."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.schema_combo['values'] = tables
            if tables:
                self.schema_table_var.set(tables[0])
                self.show_table_schema()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables: {e}")
    
    def on_table_select(self, event):
        """Handle table selection from listbox."""
        selection = self.table_listbox.curselection()
        if selection:
            table_name = self.table_listbox.get(selection[0])
            self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        """Load and display table data."""
        self.current_table = table_name
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Clear existing tree
            self.data_tree.delete(*self.data_tree.get_children())
            self.data_tree['columns'] = columns
            self.data_tree['show'] = 'headings'
            
            # Configure columns
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, minwidth=50)
            
            # Fetch data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            rows = cursor.fetchall()
            conn.close()
            
            # Insert data
            for row in rows:
                self.data_tree.insert('', 'end', values=row)
            
            # Update row count
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.row_count_label.config(text=f"Rows: {count} (showing {len(rows)})")
            self.status_bar.config(text=f"Loaded {len(rows)} rows from {table_name}")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {e}")
    
    def refresh_table_data(self):
        """Refresh current table data."""
        if self.current_table:
            self.load_table_data(self.current_table)
    
    def show_table_schema(self):
        """Display table schema."""
        table_name = self.schema_table_var.get()
        if not table_name:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get CREATE TABLE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            create_sql = cursor.fetchone()
            
            if create_sql and create_sql[0]:
                self.schema_text.delete('1.0', tk.END)
                self.schema_text.insert('1.0', create_sql[0])
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Add column details
            self.schema_text.insert(tk.END, "\n\n" + "="*80 + "\n")
            self.schema_text.insert(tk.END, "COLUMN INFORMATION:\n")
            self.schema_text.insert(tk.END, "="*80 + "\n\n")
            
            for col in columns:
                cid, name, ctype, notnull, default_val, pk = col
                info = f"{name} ({ctype})"
                if pk:
                    info += " PRIMARY KEY"
                if notnull:
                    info += " NOT NULL"
                if default_val is not None:
                    info += f" DEFAULT {default_val}"
                self.schema_text.insert(tk.END, info + "\n")
            
            # Get indexes
            cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=?", (table_name,))
            indexes = cursor.fetchall()
            
            if indexes:
                self.schema_text.insert(tk.END, "\n" + "="*80 + "\n")
                self.schema_text.insert(tk.END, "INDEXES:\n")
                self.schema_text.insert(tk.END, "="*80 + "\n\n")
                for idx_name, idx_sql in indexes:
                    if idx_sql:
                        self.schema_text.insert(tk.END, idx_sql + "\n\n")
            
            conn.close()
            self.status_bar.config(text=f"Schema loaded for {table_name}")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load schema: {e}")
    
    def execute_sql_query(self):
        """Execute custom SQL query."""
        query = self.sql_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a SQL query")
            return
        
        # Safety check for destructive operations
        query_upper = query.upper()
        destructive_keywords = ['DROP', 'DELETE', 'UPDATE', 'ALTER', 'TRUNCATE']
        if any(keyword in query_upper for keyword in destructive_keywords):
            if not messagebox.askyesno("Warning", "This query may modify data. Continue?"):
                return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear results
            self.results_tree.delete(*self.results_tree.get_children())
            self.results_tree['columns'] = []
            
            # Execute query
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query_upper.strip().startswith('SELECT'):
                # Fetch results
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    columns = [description[0] for description in cursor.description]
                    self.results_tree['columns'] = columns
                    self.results_tree['show'] = 'headings'
                    
                    # Configure columns
                    for col in columns:
                        self.results_tree.heading(col, text=col)
                        self.results_tree.column(col, width=100, minwidth=50)
                    
                    # Insert data
                    for row in rows:
                        self.results_tree.insert('', 'end', values=row)
                    
                    self.status_bar.config(text=f"Query executed: {len(rows)} rows returned")
                else:
                    self.status_bar.config(text="Query executed: No rows returned")
            else:
                # Non-SELECT query
                conn.commit()
                self.status_bar.config(text=f"Query executed successfully. Rows affected: {cursor.rowcount}")
            
            conn.close()
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {e}")
            self.status_bar.config(text=f"Query failed: {e}")
    
    def add_table_row(self):
        """Add a new row to the current table."""
        if self.read_only_mode:
            messagebox.showwarning("Read-Only", "Read-only mode is enabled")
            return
        
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        self._show_row_editor(self.current_table, None)
    
    def edit_table_row(self):
        """Edit selected row."""
        if self.read_only_mode:
            messagebox.showwarning("Read-Only", "Read-only mode is enabled")
            return
        
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a row to edit")
            return
        
        item = self.data_tree.item(selection[0])
        row_values = item['values']
        self._show_row_editor(self.current_table, row_values)
    
    def delete_table_row(self):
        """Delete selected row."""
        if self.read_only_mode:
            messagebox.showwarning("Read-Only", "Read-only mode is enabled")
            return
        
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a row to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get primary key column
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            pk_column = None
            for col in columns:
                if col[5]:  # pk flag
                    pk_column = col[1]
                    break
            
            if not pk_column:
                messagebox.showerror("Error", "Cannot delete: table has no primary key")
                conn.close()
                return
            
            # Get the selected row's primary key value
            item = self.data_tree.item(selection[0])
            row_values = item['values']
            col_names = [col[1] for col in columns]
            pk_index = col_names.index(pk_column)
            pk_value = row_values[pk_index]
            
            # Delete row
            cursor.execute(f"DELETE FROM {self.current_table} WHERE {pk_column} = ?", (pk_value,))
            conn.commit()
            conn.close()
            
            self.status_bar.config(text="Row deleted successfully")
            self.root.update_idletasks()
            self.refresh_table_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete row: {e}")
    
    def _show_row_editor(self, table_name, row_values):
        """Show dialog for editing/adding table row."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Row - {table_name}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get table schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get column names in order (matching treeview order)
        column_names = [col[1] for col in columns]
        
        # Create mapping of row_values to column names if editing
        row_dict = {}
        if row_values and len(row_values) == len(column_names):
            row_dict = dict(zip(column_names, row_values))
        
        conn.close()
        
        # Create form fields
        entries = {}
        scroll_frame = ttk.Frame(dialog)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        for col in columns:
            cid, name, ctype, notnull, default_val, pk = col
            
            ttk.Label(scrollable_frame, text=f"{name}:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
            
            var = tk.StringVar()
            # Use row_dict if editing, otherwise use default
            if name in row_dict:
                value = row_dict[name]
                var.set(str(value) if value is not None else '')
            elif default_val is not None:
                var.set(str(default_val))
            
            entry = ttk.Entry(scrollable_frame, textvariable=var, width=40)
            entry.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
            
            entries[name] = (var, entry, ctype, notnull, pk)
            row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', pady=10)
        
        def save_row():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if row_values:
                    # Update existing row
                    pk_column = None
                    for col_name, (var, entry, ctype, notnull, pk) in entries.items():
                        if pk:
                            pk_column = col_name
                            break
                    
                    if not pk_column:
                        messagebox.showerror("Error", "Cannot update: no primary key")
                        dialog.destroy()
                        return
                    
                    set_clauses = []
                    values = []
                    pk_value = None
                    
                    for col_name, (var, entry, ctype, notnull, pk) in entries.items():
                        value = var.get().strip()
                        if pk:
                            pk_value = value
                            continue
                        
                        if value == '':
                            if notnull:
                                messagebox.showerror("Error", f"{col_name} cannot be empty")
                                return
                            set_clauses.append(f"{col_name} = ?")
                            values.append(None)
                        else:
                            set_clauses.append(f"{col_name} = ?")
                            values.append(self._convert_value(value, ctype))
                    
                    values.append(pk_value)
                    query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {pk_column} = ?"
                    cursor.execute(query, tuple(values))
                else:
                    # Insert new row
                    col_names = []
                    values = []
                    
                    for col_name, (var, entry, ctype, notnull, pk) in entries.items():
                        if pk and var.get().strip() == '':
                            continue  # Skip auto-increment primary keys
                        
                        value = var.get().strip()
                        if value == '':
                            if notnull:
                                messagebox.showerror("Error", f"{col_name} cannot be empty")
                                return
                            col_names.append(col_name)
                            values.append(None)
                        else:
                            col_names.append(col_name)
                            values.append(self._convert_value(value, ctype))
                    
                    placeholders = ', '.join(['?' for _ in values])
                    query = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"
                    cursor.execute(query, tuple(values))
                
                conn.commit()
                conn.close()
                
                dialog.destroy()
                self.status_bar.config(text="Row saved successfully")
                self.root.update_idletasks()
                self.refresh_table_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save row: {e}")
        
        ttk.Button(button_frame, text=" Save", command=save_row).pack(side='left', padx=5)
        ttk.Button(button_frame, text=" Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def _convert_value(self, value, ctype):
        """Convert string value to appropriate type based on column type."""
        ctype_lower = ctype.upper()
        
        if 'INT' in ctype_lower:
            try:
                return int(value)
            except ValueError:
                return 0
        elif 'REAL' in ctype_lower or 'FLOAT' in ctype_lower or 'DOUBLE' in ctype_lower:
            try:
                return float(value)
            except ValueError:
                return 0.0
        elif 'BOOLEAN' in ctype_lower:
            return 1 if value.lower() in ('1', 'true', 'yes', 'on') else 0
        else:
            return str(value)
    
    def export_table_csv(self):
        """Export current table to CSV."""
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            import csv
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {self.current_table}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            self.status_bar.config(text=f"Exported {len(rows)} rows to {filename}")
            self.root.update_idletasks()
            messagebox.showinfo("Success", f"Exported {len(rows)} rows to CSV")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")


def main():
    """Run the GUI application."""
    import argparse
    parser = argparse.ArgumentParser(description='Macro Chef GUI')
    parser.add_argument('--dev', action='store_true', help='Launch developer mode')
    args = parser.parse_args()
    
    root = tk.Tk()
    if args.dev:
        app = DeveloperGUI(root)
    else:
        app = MacroChefGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
