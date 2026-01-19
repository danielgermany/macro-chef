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
from scripts.meal_tracker import MealTracker
from scripts.weekly_planner import WeeklyPlanner
from scripts.budget_tracker import BudgetTracker
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
            self.nutrition_calc = NutritionCalculator(db_path=db_path)
            self.meal_recommender = MealRecommender(db_path=db_path)
            self.inventory_manager = InventoryManager(db_path=db_path)
            self.db_manager = DatabaseManager(db_path=db_path)
            self.meal_tracker = MealTracker(db_path=db_path)
            self.weekly_planner = WeeklyPlanner(db_path=db_path)
            self.budget_tracker = BudgetTracker(db_path=db_path)
        else:
            self.user_manager = UserProfileManager()
            self.nutrition_calc = NutritionCalculator()
            self.meal_recommender = MealRecommender()
            self.inventory_manager = InventoryManager()
            self.db_manager = DatabaseManager()
            self.meal_tracker = MealTracker()
            self.weekly_planner = WeeklyPlanner()
            self.budget_tracker = BudgetTracker()

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
        self.create_meal_logging_tab()
        self.create_weekly_planning_tab()
        self.create_shopping_list_tab()
        self.create_budget_tab()
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

        # Top section: Quick actions
        actions_frame = ttk.Frame(tab)
        actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            actions_frame,
            text=" Log Meal",
            style='Action.TButton',
            command=self.switch_to_log_meals_tab
        ).pack(side='left', padx=5)
        
        ttk.Button(
            actions_frame,
            text=" Get Recommendation",
            style='Action.TButton',
            command=self.get_meal_recommendation
        ).pack(side='left', padx=5)
        
        ttk.Button(
            actions_frame,
            text=" Refresh Dashboard",
            command=self.refresh_dashboard
        ).pack(side='right', padx=5)

        # Daily targets and progress section
        targets_frame = ttk.LabelFrame(tab, text="Today's Nutrition Targets & Progress", padding="10")
        targets_frame.pack(fill='x', pady=5)

        # Progress display
        progress_display_frame = ttk.Frame(targets_frame)
        progress_display_frame.pack(fill='x', pady=5)
        
        # Progress bars for dashboard
        self.dashboard_progress_bars = {}
        self.dashboard_progress_labels = {}
        
        macros = [
            ('Calories', 'calories', 'kcal'),
            ('Protein', 'protein_g', 'g'),
            ('Carbs', 'carbs_g', 'g'),
            ('Fat', 'fat_g', 'g')
        ]
        
        for i, (label, key, unit) in enumerate(macros):
            row_frame = ttk.Frame(progress_display_frame)
            row_frame.pack(fill='x', pady=2)
            
            ttk.Label(row_frame, text=f"{label}:", width=12, anchor='w').pack(side='left', padx=5)
            
            # Progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(row_frame, variable=progress_var, maximum=100, length=250)
            progress_bar.pack(side='left', padx=5)
            self.dashboard_progress_bars[key] = progress_var
            
            # Label showing consumed/target/remaining
            label_var = tk.StringVar(value="0 / 0 (0%) | Remaining: 0")
            label_widget = ttk.Label(row_frame, textvariable=label_var, width=35, anchor='w')
            label_widget.pack(side='left', padx=5)
            self.dashboard_progress_labels[key] = label_var
        
        # Meal count and adherence
        self.dashboard_meal_count_label = ttk.Label(targets_frame, text="Meals logged today: 0", font=('Helvetica', 10, 'bold'))
        self.dashboard_meal_count_label.pack(pady=5)

        # Targets text (for detailed view)
        self.targets_text = scrolledtext.ScrolledText(
            targets_frame,
            height=6,
            width=80,
            font=('Courier', 9),
            state='disabled'
        )
        self.targets_text.pack(fill='both', expand=True, pady=5)

        # Quick stats section
        stats_frame = ttk.LabelFrame(tab, text="Quick Stats", padding="10")
        stats_frame.pack(fill='both', expand=True, pady=5)

        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            height=8,
            width=80,
            font=('Courier', 10),
            state='disabled'
        )
        self.stats_text.pack(fill='both', expand=True)

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
        
        # Body metrics logging section
        metrics_frame = ttk.LabelFrame(tab, text="Log Body Metrics", padding="10")
        metrics_frame.pack(fill='x', pady=5)
        
        # Metrics form
        metrics_form_frame = ttk.Frame(metrics_frame)
        metrics_form_frame.pack(fill='x')
        
        ttk.Label(metrics_form_frame, text="Date:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.metrics_date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(metrics_form_frame, textvariable=self.metrics_date_var, width=12).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(metrics_form_frame, text="Weight (lbs):").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.metrics_weight_var = tk.DoubleVar()
        ttk.Entry(metrics_form_frame, textvariable=self.metrics_weight_var, width=12).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(metrics_form_frame, text="Body Fat %:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.metrics_bodyfat_var = tk.DoubleVar()
        ttk.Entry(metrics_form_frame, textvariable=self.metrics_bodyfat_var, width=12).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(metrics_form_frame, text="Muscle Mass (lbs):").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.metrics_muscle_var = tk.DoubleVar()
        ttk.Entry(metrics_form_frame, textvariable=self.metrics_muscle_var, width=12).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Button(metrics_form_frame, text=" Log Metrics", style='Action.TButton', command=self.log_body_metrics).grid(row=2, column=0, columnspan=4, pady=5)
        
        # Metrics history display
        metrics_history_frame = ttk.LabelFrame(tab, text="Metrics History (Last 30 Days)", padding="10")
        metrics_history_frame.pack(fill='both', expand=True, pady=5)
        
        metrics_columns = ('Date', 'Weight', 'Body Fat %', 'Muscle Mass')
        self.metrics_history_tree = ttk.Treeview(metrics_history_frame, columns=metrics_columns, show='headings', height=8)
        
        for col in metrics_columns:
            self.metrics_history_tree.heading(col, text=col)
            width = 120 if col == 'Date' else 100
            self.metrics_history_tree.column(col, width=width)
        
        metrics_scrollbar = ttk.Scrollbar(metrics_history_frame, orient='vertical', command=self.metrics_history_tree.yview)
        self.metrics_history_tree.configure(yscrollcommand=metrics_scrollbar.set)
        
        self.metrics_history_tree.pack(side='left', fill='both', expand=True)
        metrics_scrollbar.pack(side='right', fill='y')
        
        ttk.Button(metrics_history_frame, text=" Refresh History", command=self.refresh_metrics_history).pack(pady=5)

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

    def create_meal_logging_tab(self):
        """Create meal logging and progress tracking tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Log Meals")
        
        # Top section: Progress display
        progress_frame = ttk.LabelFrame(tab, text="Daily Progress", padding="10")
        progress_frame.pack(fill='x', pady=5)
        
        # Progress bars container
        progress_bars_frame = ttk.Frame(progress_frame)
        progress_bars_frame.pack(fill='x')
        
        # Date selector
        date_frame = ttk.Frame(progress_frame)
        date_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(date_frame, text="Date:").pack(side='left', padx=5)
        self.progress_date_var = tk.StringVar(value=str(date.today()))
        date_entry = ttk.Entry(date_frame, textvariable=self.progress_date_var, width=12)
        date_entry.pack(side='left', padx=5)
        ttk.Button(date_frame, text="Refresh", command=self.refresh_progress).pack(side='left', padx=5)
        
        # Progress bars for each macro
        macros = [
            ('Calories', 'calories', 'kcal'),
            ('Protein', 'protein_g', 'g'),
            ('Carbs', 'carbs_g', 'g'),
            ('Fat', 'fat_g', 'g')
        ]
        
        self.progress_bars = {}
        self.progress_labels = {}
        
        for i, (label, key, unit) in enumerate(macros):
            row_frame = ttk.Frame(progress_bars_frame)
            row_frame.pack(fill='x', pady=2)
            
            ttk.Label(row_frame, text=f"{label}:", width=12, anchor='w').pack(side='left', padx=5)
            
            # Progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(row_frame, variable=progress_var, maximum=100, length=300)
            progress_bar.pack(side='left', padx=5)
            self.progress_bars[key] = progress_var
            
            # Label showing consumed/target/remaining
            label_var = tk.StringVar(value="0 / 0 (0%) | Remaining: 0")
            label_widget = ttk.Label(row_frame, textvariable=label_var, width=40, anchor='w')
            label_widget.pack(side='left', padx=5)
            self.progress_labels[key] = label_var
        
        # Meal count label
        self.meal_count_label = ttk.Label(progress_frame, text="Meals logged today: 0", font=('Helvetica', 10, 'bold'))
        self.meal_count_label.pack(pady=5)
        
        # Middle section: Log meal
        log_frame = ttk.LabelFrame(tab, text="Log Meal", padding="10")
        log_frame.pack(fill='x', pady=5)
        
        # Form fields
        form_frame = ttk.Frame(log_frame)
        form_frame.pack(fill='x')
        
        # Row 1: Meal template or manual entry
        ttk.Label(form_frame, text="Meal Template:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.log_template_var = tk.StringVar()
        self.log_template_combo = ttk.Combobox(form_frame, textvariable=self.log_template_var, width=30, state='readonly')
        self.log_template_combo.grid(row=0, column=1, padx=5, pady=2)
        self.log_template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        ttk.Label(form_frame, text="OR Manual Entry:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        
        # Row 2: Meal name (manual)
        ttk.Label(form_frame, text="Meal Name:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.log_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.log_name_var, width=30).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Meal Time:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.log_meal_time_var = tk.StringVar(value="dinner")
        ttk.Combobox(form_frame, textvariable=self.log_meal_time_var, values=["breakfast", "lunch", "dinner", "snack"], width=12, state='readonly').grid(row=1, column=3, padx=5, pady=2)
        
        # Row 3: Nutrition
        ttk.Label(form_frame, text="Calories:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.log_calories_var = tk.IntVar()
        ttk.Entry(form_frame, textvariable=self.log_calories_var, width=12).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Protein (g):").grid(row=2, column=2, sticky='w', padx=5, pady=2)
        self.log_protein_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.log_protein_var, width=12).grid(row=2, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Carbs (g):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.log_carbs_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.log_carbs_var, width=12).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Fat (g):").grid(row=3, column=2, sticky='w', padx=5, pady=2)
        self.log_fat_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.log_fat_var, width=12).grid(row=3, column=3, padx=5, pady=2)
        
        # Row 4: Date and servings
        ttk.Label(form_frame, text="Date:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.log_date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(form_frame, textvariable=self.log_date_var, width=12).grid(row=4, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Servings:").grid(row=4, column=2, sticky='w', padx=5, pady=2)
        self.log_servings_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(form_frame, from_=0.25, to=10.0, increment=0.25, textvariable=self.log_servings_var, width=12).grid(row=4, column=3, padx=5, pady=2)
        
        # Log button
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            button_frame,
            text=" Log Meal",
            style='Action.TButton',
            command=self.log_meal
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text=" Clear Form",
            command=self.clear_log_form
        ).pack(side='left', padx=5)
        
        # Bottom section: Meal history
        history_frame = ttk.LabelFrame(tab, text="Meal History", padding="10")
        history_frame.pack(fill='both', expand=True, pady=5)
        
        # History treeview
        history_columns = ('ID', 'Date', 'Meal Time', 'Meal Name', 'Calories', 'Protein', 'Carbs', 'Fat')
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show='headings', height=10)
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            width = 60 if col == 'ID' else (100 if col in ['Date', 'Meal Time'] else (150 if col == 'Meal Name' else 80))
            self.history_tree.column(col, width=width)
        
        history_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')
        
        # History buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            history_btn_frame,
            text=" Refresh History",
            command=self.refresh_meal_history
        ).pack(side='left', padx=5)
        
        ttk.Button(
            history_btn_frame,
            text=" Delete Selected",
            command=self.delete_logged_meal
        ).pack(side='left', padx=5)
        
        # Load meal templates for dropdown
        self.refresh_meal_templates()

    def create_weekly_planning_tab(self):
        """Create weekly meal planning tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Weekly Plan")
        
        # Top section: Plan controls
        controls_frame = ttk.LabelFrame(tab, text="Plan Controls", padding="10")
        controls_frame.pack(fill='x', pady=5)
        
        # Week selector and plan name
        week_frame = ttk.Frame(controls_frame)
        week_frame.pack(fill='x', pady=5)
        
        ttk.Label(week_frame, text="Week Start:").pack(side='left', padx=5)
        self.plan_week_start_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(week_frame, textvariable=self.plan_week_start_var, width=12).pack(side='left', padx=5)
        
        ttk.Label(week_frame, text="Plan Name:").pack(side='left', padx=5)
        self.plan_name_var = tk.StringVar()
        ttk.Entry(week_frame, textvariable=self.plan_name_var, width=30).pack(side='left', padx=5)
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            button_frame,
            text=" Generate Plan",
            style='Action.TButton',
            command=self.generate_weekly_plan
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text=" Save Plan",
            command=self.save_weekly_plan
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text=" Load Plan",
            command=self.load_weekly_plan
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text=" Clear Plan",
            command=self.clear_weekly_plan
        ).pack(side='left', padx=5)
        
        # Weekly calendar view
        calendar_frame = ttk.LabelFrame(tab, text="Weekly Meal Plan", padding="10")
        calendar_frame.pack(fill='both', expand=True, pady=5)
        
        # Create 7-day grid
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.weekly_plan_widgets = {}
        
        # Header row
        header_frame = ttk.Frame(calendar_frame)
        header_frame.pack(fill='x')
        for day in days:
            day_frame = ttk.LabelFrame(header_frame, text=day, padding="5")
            day_frame.pack(side='left', fill='both', expand=True, padx=2)
            
            # Meal slots for each day
            meal_slots = {}
            for meal_time in ['Breakfast', 'Lunch', 'Dinner', 'Snack']:
                slot_frame = ttk.Frame(day_frame)
                slot_frame.pack(fill='x', pady=1)
                
                ttk.Label(slot_frame, text=f"{meal_time}:", font=('Helvetica', 8, 'bold')).pack(anchor='w')
                
                meal_label = ttk.Label(slot_frame, text="(empty)", font=('Helvetica', 8), foreground='gray')
                meal_label.pack(anchor='w', padx=5)
                
                meal_slots[meal_time.lower()] = meal_label
            
            self.weekly_plan_widgets[day.lower()] = meal_slots
        
        # Plan summary
        summary_frame = ttk.LabelFrame(tab, text="Plan Summary", padding="10")
        summary_frame.pack(fill='x', pady=5)
        
        self.plan_summary_text = scrolledtext.ScrolledText(
            summary_frame,
            height=6,
            width=80,
            font=('Courier', 9),
            state='disabled'
        )
        self.plan_summary_text.pack(fill='both', expand=True)
        
        # Store current plan
        self.current_weekly_plan = None

    def create_shopping_list_tab(self):
        """Create shopping list generator tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Shopping List")
        
        # Top section: Generate from weekly plan
        generate_frame = ttk.LabelFrame(tab, text="Generate Shopping List", padding="10")
        generate_frame.pack(fill='x', pady=5)
        
        ttk.Label(generate_frame, text="Generate from:").pack(side='left', padx=5)
        
        ttk.Button(
            generate_frame,
            text=" Current Weekly Plan",
            style='Action.TButton',
            command=self.generate_shopping_list_from_plan
        ).pack(side='left', padx=5)
        
        ttk.Label(generate_frame, text="OR Plan ID:").pack(side='left', padx=5)
        self.shopping_plan_id_var = tk.StringVar()
        ttk.Entry(generate_frame, textvariable=self.shopping_plan_id_var, width=10).pack(side='left', padx=5)
        ttk.Button(
            generate_frame,
            text=" Load Plan",
            command=self.generate_shopping_list_from_plan_id
        ).pack(side='left', padx=5)
        
        # Shopping list display
        list_frame = ttk.LabelFrame(tab, text="Shopping List", padding="10")
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.shopping_list_text = scrolledtext.ScrolledText(
            list_frame,
            height=20,
            width=80,
            font=('Courier', 10),
            state='disabled'
        )
        self.shopping_list_text.pack(fill='both', expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(tab)
        export_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            export_frame,
            text=" Copy to Clipboard",
            command=self.copy_shopping_list
        ).pack(side='left', padx=5)
        
        ttk.Button(
            export_frame,
            text=" Export to File",
            command=self.export_shopping_list
        ).pack(side='left', padx=5)
        
        ttk.Button(
            export_frame,
            text=" Clear List",
            command=self.clear_shopping_list
        ).pack(side='left', padx=5)
        
        # Store current shopping list
        self.current_shopping_list = None

    def create_budget_tab(self):
        """Create budget tracking tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=" Budget")
        
        # Top section: Budget overview
        overview_frame = ttk.LabelFrame(tab, text="Budget Overview", padding="10")
        overview_frame.pack(fill='x', pady=5)
        
        # Budget display
        budget_display_frame = ttk.Frame(overview_frame)
        budget_display_frame.pack(fill='x', pady=5)
        
        self.budget_limit_label = ttk.Label(budget_display_frame, text="Weekly Budget: $0.00", font=('Helvetica', 12, 'bold'))
        self.budget_limit_label.pack(side='left', padx=10)
        
        self.budget_spent_label = ttk.Label(budget_display_frame, text="Spent: $0.00", font=('Helvetica', 12))
        self.budget_spent_label.pack(side='left', padx=10)
        
        self.budget_remaining_label = ttk.Label(budget_display_frame, text="Remaining: $0.00", font=('Helvetica', 12))
        self.budget_remaining_label.pack(side='left', padx=10)
        
        self.budget_status_label = ttk.Label(budget_display_frame, text="Status: OK", font=('Helvetica', 12, 'bold'))
        self.budget_status_label.pack(side='left', padx=10)
        
        # Progress bar
        self.budget_progress_var = tk.DoubleVar()
        self.budget_progress_bar = ttk.Progressbar(overview_frame, variable=self.budget_progress_var, maximum=100, length=400)
        self.budget_progress_bar.pack(fill='x', pady=5)
        
        ttk.Button(overview_frame, text=" Refresh", command=self.refresh_budget_display).pack(pady=5)
        
        # Middle section: Add purchase
        add_frame = ttk.LabelFrame(tab, text="Add Purchase", padding="10")
        add_frame.pack(fill='x', pady=5)
        
        # Form fields
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')
        
        ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.purchase_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.purchase_name_var, width=25).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Date:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.purchase_date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(form_frame, textvariable=self.purchase_date_var, width=12).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Amount ($):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.purchase_amount_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.purchase_amount_var, width=12).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Category:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.purchase_category_var = tk.StringVar(value="groceries")
        ttk.Combobox(form_frame, textvariable=self.purchase_category_var, values=["groceries", "protein", "vegetables", "dairy", "grains", "snacks", "other"], width=15, state='readonly').grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Store:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.purchase_store_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.purchase_store_var, width=25).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Button(form_frame, text=" Add Purchase", style='Action.TButton', command=self.add_purchase).grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        # Bottom section: Spending history
        history_frame = ttk.LabelFrame(tab, text="Spending History", padding="10")
        history_frame.pack(fill='both', expand=True, pady=5)
        
        # History treeview
        history_columns = ('ID', 'Date', 'Item', 'Amount', 'Category', 'Store')
        self.budget_history_tree = ttk.Treeview(history_frame, columns=history_columns, show='headings', height=12)
        
        for col in history_columns:
            self.budget_history_tree.heading(col, text=col)
            width = 60 if col == 'ID' else (100 if col == 'Date' else (150 if col == 'Item' else 100))
            self.budget_history_tree.column(col, width=width)
        
        budget_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.budget_history_tree.yview)
        self.budget_history_tree.configure(yscrollcommand=budget_scrollbar.set)
        
        self.budget_history_tree.pack(side='left', fill='both', expand=True)
        budget_scrollbar.pack(side='right', fill='y')
        
        # Category breakdown display
        breakdown_frame = ttk.LabelFrame(tab, text="Category Breakdown (Last 30 Days)", padding="10")
        breakdown_frame.pack(fill='x', pady=5)
        
        self.budget_breakdown_text = scrolledtext.ScrolledText(
            breakdown_frame,
            height=6,
            width=80,
            font=('Courier', 9),
            state='disabled'
        )
        self.budget_breakdown_text.pack(fill='both', expand=True)

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
                
                # Refresh budget and metrics if tabs exist
                if hasattr(self, 'budget_tracker'):
                    try:
                        self.refresh_budget_display()
                    except Exception:
                        pass  # Tab might not be initialized yet
                
                if hasattr(self, 'metrics_history_tree'):
                    try:
                        self.refresh_metrics_history()
                    except Exception:
                        pass  # Tab might not be initialized yet
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
            print(f"[DEBUG] Generated targets for user {self.current_user_id}: {len(targets)} fields")

            # Save targets to database
            target_id = self.nutrition_calc.save_daily_targets(targets, self.current_user_id)

            if target_id:
                print(f"[SUCCESS] Targets saved with ID: {target_id}")
                messagebox.showinfo("Success", "Daily targets generated successfully!")
                self.refresh_dashboard()
                self.status_bar.config(text="Daily targets generated successfully")
                self.root.update_idletasks()
            else:
                error_msg = "Failed to save targets - save_daily_targets returned None"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", error_msg)

        except Exception as e:
            import traceback
            error_msg = f"Failed to generate targets: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            messagebox.showerror("Error", error_msg)
            self.status_bar.config(text=f"Error: {str(e)}")
            self.root.update_idletasks()

    def log_body_metrics(self):
        """Log body metrics to database."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            weight = self.metrics_weight_var.get()
            if weight <= 0:
                messagebox.showwarning("Warning", "Please enter a valid weight")
                return
            
            metrics_date_str = self.metrics_date_var.get()
            try:
                metrics_date = date.fromisoformat(metrics_date_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            body_fat = self.metrics_bodyfat_var.get() if self.metrics_bodyfat_var.get() > 0 else None
            muscle_mass = self.metrics_muscle_var.get() if self.metrics_muscle_var.get() > 0 else None
            
            # Insert into body_metrics_history
            query = """
                INSERT INTO body_metrics_history (
                    user_id, date, weight_lbs, body_fat_pct, muscle_mass_lbs
                ) VALUES (?, ?, ?, ?, ?)
            """
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (
                self.current_user_id,
                metrics_date,
                weight,
                body_fat,
                muscle_mass
            ))
            conn.commit()
            conn.close()
            
            # Update user profile with latest weight if it's today
            if metrics_date == date.today():
                self.user_manager.update_user(
                    user_id=self.current_user_id,
                    weight_lbs=weight,
                    body_fat_pct=body_fat if body_fat else None,
                    muscle_mass_lbs=muscle_mass if muscle_mass else None
                )
            
            # Clear form
            self.metrics_weight_var.set(0.0)
            self.metrics_bodyfat_var.set(0.0)
            self.metrics_muscle_var.set(0.0)
            self.metrics_date_var.set(str(date.today()))
            
            # Refresh history
            self.refresh_metrics_history()
            
            messagebox.showinfo("Success", "Body metrics logged successfully!")
            self.status_bar.config(text="Body metrics logged")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log body metrics: {e}")

    def refresh_metrics_history(self):
        """Refresh body metrics history display."""
        if not self.current_user_id:
            return
        
        try:
            # Clear existing items
            self.metrics_history_tree.delete(*self.metrics_history_tree.get_children())
            
            # Get metrics history (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            query = """
                SELECT date, weight_lbs, body_fat_pct, muscle_mass_lbs
                FROM body_metrics_history
                WHERE user_id = ? AND date >= ? AND date <= ?
                ORDER BY date DESC
                LIMIT 50
            """
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (self.current_user_id, start_date, end_date))
            metrics = cursor.fetchall()
            conn.close()
            
            # Add to treeview
            for metric in metrics:
                self.metrics_history_tree.insert('', 'end', values=(
                    metric[0],  # date
                    f"{metric[1]:.1f}" if metric[1] else 'N/A',  # weight
                    f"{metric[2]:.1f}%" if metric[2] else 'N/A',  # body_fat
                    f"{metric[3]:.1f}" if metric[3] else 'N/A'  # muscle_mass
                ))
            
            self.status_bar.config(text=f"Loaded {len(metrics)} metrics entries")
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"Error refreshing metrics history: {e}")

    def refresh_dashboard(self):
        """Refresh dashboard with current data."""
        if not self.current_user_id:
            return

        try:
            # Get today's targets
            targets = self.nutrition_calc.get_daily_targets(self.current_user_id, date.today())
            
            # Get today's progress
            progress = None
            if hasattr(self, 'meal_tracker'):
                try:
                    progress = self.meal_tracker.get_daily_progress(
                        user_id=self.current_user_id,
                        target_date=date.today()
                    )
                except Exception as e:
                    print(f"Error getting progress: {e}")

            # Update progress bars if available
            if progress and hasattr(self, 'dashboard_progress_bars'):
                totals = progress['totals']
                targets_dict = progress['targets']
                remaining = progress['remaining']
                percentages = progress['percentages']
                
                macros_map = {
                    'calories': ('calories_target', 'kcal'),
                    'protein_g': ('protein_target_g', 'g'),
                    'carbs_g': ('carbs_target_g', 'g'),
                    'fat_g': ('fat_target_g', 'g')
                }
                
                for key, (target_key, unit) in macros_map.items():
                    target_value = targets_dict.get(target_key, 0) or 0
                    consumed = totals.get(key, 0)
                    rem = remaining.get(key, 0)
                    pct = percentages.get(key, 0)
                    
                    # Update progress bar
                    self.dashboard_progress_bars[key].set(min(pct, 100))
                    
                    # Update label
                    label_text = f"{consumed:.0f} / {target_value:.0f} ({pct:.1f}%) | Remaining: {rem:.0f} {unit}"
                    self.dashboard_progress_labels[key].set(label_text)
                
                # Update meal count
                meal_count = progress['meal_count']
                self.dashboard_meal_count_label.config(text=f"Meals logged today: {meal_count}")

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
                
                # Add progress summary if available
                if progress:
                    totals = progress['totals']
                    percentages = progress['percentages']
                    output += "  PROGRESS SUMMARY:\n"
                    output += f"    • Calories:     {totals.get('calories', 0)} / {targets.get('calories_target', 0)} ({percentages.get('calories', 0):.1f}%)\n"
                    output += f"    • Protein:      {totals.get('protein_g', 0):.1f} / {targets.get('protein_target_g', 0)}g ({percentages.get('protein_g', 0):.1f}%)\n"
                    output += f"    • Carbs:        {totals.get('carbs_g', 0):.1f} / {targets.get('carbs_target_g', 0)}g ({percentages.get('carbs_g', 0):.1f}%)\n"
                    output += f"    • Fat:          {totals.get('fat_g', 0):.1f} / {targets.get('fat_target_g', 0)}g ({percentages.get('fat_g', 0):.1f}%)\n\n"
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

            # Also refresh meal templates dropdown in logging tab
            if hasattr(self, 'log_template_combo'):
                self.refresh_meal_templates()

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

            print(f"[DEBUG] Getting meal recommendation for user {self.current_user_id}")
            
            # Get recommendations (returns list of recommendations)
            recommendations = self.meal_recommender.recommend_meal(
                meal_time='dinner',
                user_id=self.current_user_id,
                target_date=date.today(),
                allow_online_search=True  # Explicitly allow online search as fallback
            )

            print(f"[DEBUG] Received {len(recommendations)} recommendations")

            if recommendations:
                # Get top recommendation
                meal = recommendations[0]
                print(f"[DEBUG] Top recommendation: {meal.get('name', 'Unknown')}")
                
                # Save recommended meal to database if it's an online recipe
                try:
                    saved_id = self.meal_recommender.save_recommended_meal(meal, self.current_user_id)
                    if saved_id:
                        print(f"[SUCCESS] Saved recommended meal to database with ID: {saved_id}")
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
                self.status_bar.config(text=f"Recommended: {meal['name']}")
                self.root.update_idletasks()
            else:
                print("[INFO] No recommendations found - database may be empty or online search unavailable")
                messagebox.showinfo("No Results", "No suitable meals found. Try searching online recipes!")
                self.status_bar.config(text="No meal recommendations available")
                self.root.update_idletasks()

        except Exception as e:
            import traceback
            error_msg = f"Failed to get recommendation: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            messagebox.showerror("Error", error_msg)
            self.status_bar.config(text=f"Error getting recommendation: {str(e)}")
            self.root.update_idletasks()

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

    def refresh_meal_templates(self):
        """Refresh meal templates dropdown in logging tab."""
        try:
            if not self.current_user_id:
                return
            
            meals = self.meal_recommender.get_meal_templates(user_id=self.current_user_id)
            meal_names = [f"{m['name']} ({m.get('calories', 0)} cal)" for m in meals]
            self.log_template_combo['values'] = meal_names
        except Exception as e:
            print(f"Error refreshing meal templates: {e}")

    def on_template_selected(self, event=None):
        """Fill form fields when a meal template is selected."""
        try:
            selection = self.log_template_var.get()
            if not selection:
                return
            
            # Extract meal name (before the parentheses)
            meal_name = selection.split(' (')[0]
            
            # Find the meal in database
            meals = self.meal_recommender.get_meal_templates(user_id=self.current_user_id)
            meal = next((m for m in meals if m['name'] == meal_name), None)
            
            if meal:
                self.log_name_var.set(meal['name'])
                self.log_calories_var.set(int(meal.get('calories', 0)))
                self.log_protein_var.set(float(meal.get('protein_g', 0)))
                self.log_carbs_var.set(float(meal.get('carbs_g', 0)))
                self.log_fat_var.set(float(meal.get('fat_g', 0)))
                self.log_meal_time_var.set(meal.get('meal_type', 'dinner'))
        except Exception as e:
            print(f"Error loading template: {e}")

    def log_meal(self):
        """Log a meal to the database."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            # Get form values
            meal_name = self.log_name_var.get().strip()
            if not meal_name:
                messagebox.showwarning("Warning", "Please enter a meal name")
                return
            
            calories = self.log_calories_var.get()
            protein = self.log_protein_var.get()
            carbs = self.log_carbs_var.get()
            fat = self.log_fat_var.get()
            meal_time = self.log_meal_time_var.get()
            servings = self.log_servings_var.get()
            
            print(f"[DEBUG] Logging meal: {meal_name}, calories={calories}, protein={protein}g, carbs={carbs}g, fat={fat}g")
            
            # Parse date
            meal_date_str = self.log_date_var.get()
            try:
                meal_date = date.fromisoformat(meal_date_str)
            except ValueError as ve:
                error_msg = f"Invalid date format. Use YYYY-MM-DD. Got: {meal_date_str}"
                print(f"[ERROR] {error_msg}: {ve}")
                messagebox.showerror("Error", error_msg)
                return
            
            # Apply servings multiplier
            if servings != 1.0:
                calories = int(calories * servings)
                protein = protein * servings
                carbs = carbs * servings
                fat = fat * servings
                print(f"[DEBUG] Applied servings multiplier {servings}x")
            
            # Log meal
            meal_id = self.meal_tracker.log_meal(
                meal_name=meal_name,
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
                meal_time=meal_time,
                user_id=self.current_user_id,
                meal_date=meal_date
            )
            
            if meal_id:
                print(f"[SUCCESS] Meal logged with ID: {meal_id}")
                messagebox.showinfo("Success", f"Meal logged successfully!")
                self.clear_log_form()
                self.refresh_progress()
                self.refresh_meal_history()
                self.status_bar.config(text=f"Meal logged: {meal_name}")
                self.root.update_idletasks()
            else:
                error_msg = "Failed to log meal - log_meal returned None"
                print(f"[ERROR] {error_msg}")
                messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            import traceback
            error_msg = f"Failed to log meal: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            messagebox.showerror("Error", error_msg)
            self.status_bar.config(text=f"Error: {str(e)}")
            self.root.update_idletasks()

    def clear_log_form(self):
        """Clear the meal logging form."""
        self.log_template_var.set('')
        self.log_name_var.set('')
        self.log_calories_var.set(0)
        self.log_protein_var.set(0.0)
        self.log_carbs_var.set(0.0)
        self.log_fat_var.set(0.0)
        self.log_meal_time_var.set('dinner')
        self.log_date_var.set(str(date.today()))
        self.log_servings_var.set(1.0)

    def refresh_progress(self):
        """Refresh the daily progress display."""
        if not self.current_user_id:
            return
        
        try:
            # Parse date
            progress_date_str = self.progress_date_var.get()
            try:
                progress_date = date.fromisoformat(progress_date_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Get progress data
            progress = self.meal_tracker.get_daily_progress(
                user_id=self.current_user_id,
                target_date=progress_date
            )
            
            totals = progress['totals']
            targets = progress['targets']
            remaining = progress['remaining']
            percentages = progress['percentages']
            
            # Update progress bars and labels
            macros_map = {
                'calories': ('calories_target', 'kcal'),
                'protein_g': ('protein_target_g', 'g'),
                'carbs_g': ('carbs_target_g', 'g'),
                'fat_g': ('fat_target_g', 'g')
            }
            
            for key, (target_key, unit) in macros_map.items():
                target_value = targets.get(target_key, 0) or 0
                consumed = totals.get(key, 0)
                rem = remaining.get(key, 0)
                pct = percentages.get(key, 0)
                
                # Update progress bar
                self.progress_bars[key].set(min(pct, 100))
                
                # Update label
                label_text = f"{consumed:.0f} / {target_value:.0f} ({pct:.1f}%) | Remaining: {rem:.0f} {unit}"
                self.progress_labels[key].set(label_text)
            
            # Update meal count
            meal_count = progress['meal_count']
            self.meal_count_label.config(text=f"Meals logged: {meal_count}")
            
            self.status_bar.config(text=f"Progress refreshed for {progress_date_str}")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh progress: {e}")

    def refresh_meal_history(self):
        """Refresh the meal history display."""
        if not self.current_user_id:
            return
        
        try:
            # Clear existing items
            self.history_tree.delete(*self.history_tree.get_children())
            
            # Get meal history (last 30 days)
            meals = self.meal_tracker.get_meal_history(
                days=30,
                user_id=self.current_user_id
            )
            
            # Add meals to treeview
            for meal in meals:
                self.history_tree.insert('', 'end', values=(
                    meal.get('id', ''),
                    meal.get('date', ''),
                    meal.get('meal_time', ''),
                    meal.get('meal_name', ''),
                    meal.get('calories', 0),
                    f"{meal.get('protein_g', 0):.1f}",
                    f"{meal.get('carbs_g', 0):.1f}",
                    f"{meal.get('fat_g', 0):.1f}"
                ))
            
            self.status_bar.config(text=f"Loaded {len(meals)} meals from history")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh meal history: {e}")

    def delete_logged_meal(self):
        """Delete a logged meal from history."""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a meal to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this meal?"):
            return
        
        try:
            item = self.history_tree.item(selection[0])
            meal_id = item['values'][0]
            
            # Delete from database
            query = "DELETE FROM daily_nutrition_progress WHERE id = ?"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (meal_id,))
            conn.commit()
            conn.close()
            
            # Refresh displays
            self.refresh_progress()
            self.refresh_meal_history()
            self.status_bar.config(text="Meal deleted successfully")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete meal: {e}")

    def switch_to_log_meals_tab(self):
        """Switch to the Log Meals tab."""
        # Find the Log Meals tab index
        for i in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(i, "text")
            if "Log Meals" in tab_text or "Log" in tab_text:
                self.notebook.select(i)
                break

    def generate_weekly_plan(self):
        """Generate a weekly meal plan."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            # Parse week start date
            week_start_str = self.plan_week_start_var.get()
            try:
                week_start = date.fromisoformat(week_start_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            plan_name = self.plan_name_var.get().strip()
            if not plan_name:
                plan_name = None  # Let WeeklyPlanner generate default name
            
            self.status_bar.config(text="Generating weekly plan...")
            self.root.update_idletasks()
            
            # Generate plan
            plan = self.weekly_planner.generate_weekly_plan(
                week_start=week_start,
                user_id=self.current_user_id,
                plan_name=plan_name,
                auto_recommend=True
            )
            
            self.current_weekly_plan = plan
            
            # Display plan
            self.display_weekly_plan(plan)
            
            # Update summary
            self.update_plan_summary(plan)
            
            self.status_bar.config(text=f"Weekly plan generated: {plan['plan_name']}")
            self.root.update_idletasks()
            messagebox.showinfo("Success", "Weekly plan generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate weekly plan: {e}")

    def display_weekly_plan(self, plan):
        """Display weekly plan in the calendar view."""
        if not plan or 'daily_plans' not in plan:
            return
        
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day_name in days_order:
            # Find the daily plan for this day
            daily_plan = None
            for dp in plan['daily_plans']:
                if dp.get('day_of_week', '').lower() == day_name:
                    daily_plan = dp
                    break
            
            if day_name in self.weekly_plan_widgets:
                meal_slots = self.weekly_plan_widgets[day_name]
                
                for meal_time in ['breakfast', 'lunch', 'dinner', 'snack']:
                    if meal_time in meal_slots:
                        label = meal_slots[meal_time]
                        
                        if daily_plan and meal_time in daily_plan.get('meals', {}):
                            meal = daily_plan['meals'][meal_time]
                            meal_name = meal.get('meal_name', 'Unknown')
                            calories = meal.get('calories', 0)
                            label.config(text=f"{meal_name}\n({calories} cal)", foreground='black')
                        else:
                            label.config(text="(empty)", foreground='gray')

    def update_plan_summary(self, plan):
        """Update the plan summary display."""
        if not plan:
            return
        
        try:
            # Calculate nutrition
            nutrition = self.weekly_planner.calculate_plan_nutrition(plan)
            
            self.plan_summary_text.config(state='normal')
            self.plan_summary_text.delete('1.0', tk.END)
            
            output = "═" * 70 + "\n"
            output += f"  {plan.get('plan_name', 'Weekly Plan')}\n"
            output += f"  {plan.get('week_start')} to {plan.get('week_end')}\n"
            output += "═" * 70 + "\n\n"
            output += f"  Estimated Total Cost: ${plan.get('total_cost_estimate', 0):.2f}\n\n"
            output += "  Daily Averages:\n"
            output += f"    • Calories: {nutrition['daily_averages']['calories']:.0f} kcal\n"
            output += f"    • Protein:  {nutrition['daily_averages']['protein_g']:.1f}g\n"
            output += f"    • Carbs:    {nutrition['daily_averages']['carbs_g']:.1f}g\n"
            output += f"    • Fat:      {nutrition['daily_averages']['fat_g']:.1f}g\n"
            
            self.plan_summary_text.insert('1.0', output)
            self.plan_summary_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error updating plan summary: {e}")

    def save_weekly_plan(self):
        """Save the current weekly plan to database."""
        if not self.current_weekly_plan:
            messagebox.showwarning("Warning", "No plan to save. Generate a plan first.")
            return
        
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            plan_id = self.weekly_planner.save_plan(self.current_weekly_plan, user_id=self.current_user_id)
            
            if plan_id:
                messagebox.showinfo("Success", f"Plan saved successfully! Plan ID: {plan_id}")
                self.status_bar.config(text=f"Plan saved (ID: {plan_id})")
                self.root.update_idletasks()
            else:
                messagebox.showerror("Error", "Failed to save plan")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plan: {e}")

    def load_weekly_plan(self):
        """Load a saved weekly plan."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        # Simple dialog to enter plan ID
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Weekly Plan")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter Plan ID:").pack(pady=10)
        plan_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=plan_id_var, width=20).pack(pady=5)
        
        def load_plan():
            try:
                plan_id = int(plan_id_var.get())
                plan = self.weekly_planner.get_plan(plan_id, user_id=self.current_user_id)
                
                if plan:
                    self.current_weekly_plan = plan
                    self.plan_name_var.set(plan.get('plan_name', ''))
                    self.plan_week_start_var.set(str(plan.get('week_start', date.today())))
                    self.display_weekly_plan(plan)
                    self.update_plan_summary(plan)
                    dialog.destroy()
                    messagebox.showinfo("Success", "Plan loaded successfully!")
                else:
                    messagebox.showerror("Error", "Plan not found")
            except ValueError:
                messagebox.showerror("Error", "Invalid plan ID")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load plan: {e}")
        
        ttk.Button(dialog, text="Load", command=load_plan).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def clear_weekly_plan(self):
        """Clear the current weekly plan."""
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the current plan?"):
            return
        
        self.current_weekly_plan = None
        self.plan_name_var.set('')
        
        # Clear all meal slots
        for day_name, meal_slots in self.weekly_plan_widgets.items():
            for meal_time, label in meal_slots.items():
                label.config(text="(empty)", foreground='gray')
        
        # Clear summary
        self.plan_summary_text.config(state='normal')
        self.plan_summary_text.delete('1.0', tk.END)
        self.plan_summary_text.config(state='disabled')
        
        self.status_bar.config(text="Plan cleared")
        self.root.update_idletasks()

    def generate_shopping_list_from_plan(self):
        """Generate shopping list from current weekly plan."""
        if not self.current_weekly_plan:
            messagebox.showwarning("Warning", "No weekly plan loaded. Generate or load a plan first.")
            return
        
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            # Check if plan is saved
            if 'id' not in self.current_weekly_plan:
                # Plan needs to be saved first
                if messagebox.askyesno("Save Plan", "Plan must be saved first. Save now?"):
                    plan_id = self.weekly_planner.save_plan(self.current_weekly_plan, user_id=self.current_user_id)
                    if not plan_id:
                        messagebox.showerror("Error", "Failed to save plan")
                        return
                    self.current_weekly_plan['id'] = plan_id
                else:
                    return
            
            plan_id = self.current_weekly_plan['id']
            shopping_list = self.weekly_planner.generate_shopping_list_from_plan(plan_id, user_id=self.current_user_id)
            
            self.current_shopping_list = shopping_list
            self.display_shopping_list(shopping_list)
            
            self.status_bar.config(text="Shopping list generated successfully")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate shopping list: {e}")

    def generate_shopping_list_from_plan_id(self):
        """Generate shopping list from a saved plan ID."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        plan_id_str = self.shopping_plan_id_var.get().strip()
        if not plan_id_str:
            messagebox.showwarning("Warning", "Please enter a plan ID")
            return
        
        try:
            plan_id = int(plan_id_str)
            shopping_list = self.weekly_planner.generate_shopping_list_from_plan(plan_id, user_id=self.current_user_id)
            
            self.current_shopping_list = shopping_list
            self.display_shopping_list(shopping_list)
            
            self.status_bar.config(text=f"Shopping list generated from plan {plan_id}")
            self.root.update_idletasks()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid plan ID")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate shopping list: {e}")

    def display_shopping_list(self, shopping_list):
        """Display shopping list in the text widget."""
        if not shopping_list:
            return
        
        try:
            # Format shopping list
            formatted = self.weekly_planner.shopping_gen.format_shopping_list(shopping_list, group_by='category')
            
            self.shopping_list_text.config(state='normal')
            self.shopping_list_text.delete('1.0', tk.END)
            self.shopping_list_text.insert('1.0', formatted)
            self.shopping_list_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display shopping list: {e}")

    def copy_shopping_list(self):
        """Copy shopping list to clipboard."""
        if not self.current_shopping_list:
            messagebox.showwarning("Warning", "No shopping list to copy. Generate a list first.")
            return
        
        try:
            formatted = self.weekly_planner.shopping_gen.format_shopping_list(self.current_shopping_list, group_by='category')
            self.root.clipboard_clear()
            self.root.clipboard_append(formatted)
            self.status_bar.config(text="Shopping list copied to clipboard")
            self.root.update_idletasks()
            messagebox.showinfo("Success", "Shopping list copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy shopping list: {e}")

    def export_shopping_list(self):
        """Export shopping list to a text file."""
        if not self.current_shopping_list:
            messagebox.showwarning("Warning", "No shopping list to export. Generate a list first.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            formatted = self.weekly_planner.shopping_gen.format_shopping_list(self.current_shopping_list, group_by='category')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            self.status_bar.config(text=f"Shopping list exported to {filename}")
            self.root.update_idletasks()
            messagebox.showinfo("Success", f"Shopping list exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export shopping list: {e}")

    def clear_shopping_list(self):
        """Clear the shopping list display."""
        self.current_shopping_list = None
        self.shopping_list_text.config(state='normal')
        self.shopping_list_text.delete('1.0', tk.END)
        self.shopping_list_text.config(state='disabled')
        self.status_bar.config(text="Shopping list cleared")
        self.root.update_idletasks()

    def refresh_budget_display(self):
        """Refresh budget overview and history."""
        if not self.current_user_id:
            return
        
        try:
            # Get weekly summary
            summary = self.budget_tracker.get_weekly_summary(user_id=self.current_user_id)
            
            # Update overview labels
            self.budget_limit_label.config(text=f"Weekly Budget: ${summary['budget_limit']:.2f}")
            self.budget_spent_label.config(text=f"Spent: ${summary['total_spent']:.2f}")
            self.budget_remaining_label.config(text=f"Remaining: ${summary['remaining']:.2f}")
            
            # Update status
            if summary['is_over_budget']:
                self.budget_status_label.config(text="Status: OVER BUDGET", foreground='red')
            elif summary['percent_used'] > 80:
                self.budget_status_label.config(text="Status: WARNING", foreground='orange')
            else:
                self.budget_status_label.config(text="Status: OK", foreground='green')
            
            # Update progress bar
            self.budget_progress_var.set(min(summary['percent_used'], 100))
            
            # Refresh history
            self.refresh_spending_history()
            
            # Refresh category breakdown
            self.refresh_category_breakdown()
            
            self.status_bar.config(text="Budget display refreshed")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh budget: {e}")

    def add_purchase(self):
        """Add a new purchase to shopping history."""
        if not self.current_user_id:
            messagebox.showwarning("Warning", "Please load or create a user profile first")
            return
        
        try:
            item_name = self.purchase_name_var.get().strip()
            if not item_name:
                messagebox.showwarning("Warning", "Please enter an item name")
                return
            
            amount = self.purchase_amount_var.get()
            if amount <= 0:
                messagebox.showwarning("Warning", "Please enter a valid amount")
                return
            
            purchase_date_str = self.purchase_date_var.get()
            try:
                purchase_date = date.fromisoformat(purchase_date_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            category = self.purchase_category_var.get()
            store = self.purchase_store_var.get().strip()
            
            # Insert into shopping_history
            query = """
                INSERT INTO shopping_history (
                    user_id, purchase_date, item_name, quantity, unit,
                    unit_price_usd, total_price_usd, store, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (
                self.current_user_id,
                purchase_date,
                item_name,
                1.0,  # Default quantity
                'count',  # Default unit
                amount,  # unit_price
                amount,  # total_price
                store if store else None,
                category
            ))
            conn.commit()
            conn.close()
            
            # Clear form
            self.purchase_name_var.set('')
            self.purchase_amount_var.set(0.0)
            self.purchase_store_var.set('')
            self.purchase_date_var.set(str(date.today()))
            
            # Refresh display
            self.refresh_budget_display()
            
            messagebox.showinfo("Success", "Purchase added successfully!")
            self.status_bar.config(text="Purchase added")
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add purchase: {e}")

    def refresh_spending_history(self):
        """Refresh spending history table."""
        if not self.current_user_id:
            return
        
        try:
            # Clear existing items
            self.budget_history_tree.delete(*self.budget_history_tree.get_children())
            
            # Get recent purchases (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            query = """
                SELECT id, purchase_date, item_name, total_price_usd, category, store
                FROM shopping_history
                WHERE user_id = ? AND purchase_date >= ? AND purchase_date <= ?
                ORDER BY purchase_date DESC
                LIMIT 100
            """
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (self.current_user_id, start_date, end_date))
            purchases = cursor.fetchall()
            conn.close()
            
            # Add to treeview
            for purchase in purchases:
                self.budget_history_tree.insert('', 'end', values=(
                    purchase[0],  # id
                    purchase[1],  # date
                    purchase[2],  # item_name
                    f"${purchase[3]:.2f}",  # amount
                    purchase[4] or 'N/A',  # category
                    purchase[5] or 'N/A'  # store
                ))
            
        except Exception as e:
            print(f"Error refreshing spending history: {e}")

    def refresh_category_breakdown(self):
        """Refresh category breakdown display."""
        if not self.current_user_id:
            return
        
        try:
            breakdown = self.budget_tracker.get_category_breakdown(days=30, user_id=self.current_user_id)
            
            self.budget_breakdown_text.config(state='normal')
            self.budget_breakdown_text.delete('1.0', tk.END)
            
            if breakdown:
                output = "═" * 70 + "\n"
                output += "  CATEGORY BREAKDOWN (Last 30 Days)\n"
                output += "═" * 70 + "\n\n"
                
                total = sum(cat['total_spent'] for cat in breakdown)
                
                for cat in breakdown:
                    output += f"  {cat['category']:20} ${cat['total_spent']:>8.2f} ({cat['percent_of_total']:>5.1f}%)\n"
                
                output += f"\n  Total: ${total:.2f}\n"
            else:
                output = "\n  No purchases in the last 30 days.\n"
            
            self.budget_breakdown_text.insert('1.0', output)
            self.budget_breakdown_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error refreshing category breakdown: {e}")


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
