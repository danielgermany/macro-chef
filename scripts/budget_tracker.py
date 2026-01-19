"""
Budget tracking and spending analysis.
Monitor grocery spending against budget limits with weekly/monthly summaries.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.user_profile import UserProfileManager
from config.config import DEFAULT_USER_ID


class BudgetTracker(DatabaseManager):
    """Track and analyze grocery spending."""

    def __init__(self, db_path=None):
        super().__init__(db_path=db_path)
        self.user_manager = UserProfileManager(db_path=db_path) if db_path else UserProfileManager()

    def get_period_spending(
        self,
        start_date: date,
        end_date: date,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Get spending summary for a date range."""

        query = """
            SELECT
                COUNT(*) as num_items,
                COUNT(DISTINCT purchase_date) as num_trips,
                SUM(total_price_usd) as total_spent,
                AVG(total_price_usd) as avg_item_price,
                category,
                COUNT(*) as category_count,
                SUM(total_price_usd) as category_total
            FROM shopping_history
            WHERE user_id = ?
            AND purchase_date >= ?
            AND purchase_date <= ?
            GROUP BY category
        """

        by_category = self.execute_query(query, (user_id, start_date, end_date))

        # Calculate totals
        total_spent = sum(cat['category_total'] or 0 for cat in by_category)
        num_trips = max((cat['num_trips'] for cat in by_category), default=0)
        num_items = sum(cat['category_count'] for cat in by_category)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_spent': round(total_spent, 2),
            'num_trips': num_trips,
            'num_items': num_items,
            'avg_per_trip': round(total_spent / num_trips, 2) if num_trips > 0 else 0,
            'by_category': by_category
        }

    def get_weekly_summary(
        self,
        week_start: Optional[date] = None,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Get weekly spending summary."""

        if not week_start:
            # Current week (Monday-Sunday)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        week_end = week_start + timedelta(days=6)

        spending = self.get_period_spending(week_start, week_end, user_id)

        # Get user budget
        user = self.user_manager.get_user(user_id)
        weekly_budget = user.get('weekly_budget_usd', 0) if user else 0

        # Calculate budget status
        remaining = weekly_budget - spending['total_spent']
        percent_used = (spending['total_spent'] / weekly_budget * 100) if weekly_budget > 0 else 0

        return {
            **spending,
            'period_type': 'weekly',
            'budget_limit': weekly_budget,
            'remaining': round(remaining, 2),
            'percent_used': round(percent_used, 1),
            'is_over_budget': spending['total_spent'] > weekly_budget
        }

    def get_monthly_summary(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Get monthly spending summary."""

        if not year or not month:
            today = date.today()
            year = today.year
            month = today.month

        # First and last day of month
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        spending = self.get_period_spending(month_start, month_end, user_id)

        # Get user budget (weekly budget * 4 for monthly estimate)
        user = self.user_manager.get_user(user_id)
        weekly_budget = user.get('weekly_budget_usd', 0) if user else 0
        monthly_budget = weekly_budget * 4

        # Calculate budget status
        remaining = monthly_budget - spending['total_spent']
        percent_used = (spending['total_spent'] / monthly_budget * 100) if monthly_budget > 0 else 0

        return {
            **spending,
            'period_type': 'monthly',
            'budget_limit': monthly_budget,
            'remaining': round(remaining, 2),
            'percent_used': round(percent_used, 1),
            'is_over_budget': spending['total_spent'] > monthly_budget
        }

    def save_budget_period(
        self,
        period_type: str,
        start_date: date,
        end_date: date,
        total_spent: float,
        budget_limit: float,
        num_trips: int,
        user_id: int = DEFAULT_USER_ID,
        notes: Optional[str] = None
    ) -> int:
        """Save a budget period summary to database."""

        remaining = budget_limit - total_spent

        query = """
            INSERT INTO budget_tracking (
                user_id, period_start, period_end, period_type,
                total_spent_usd, budget_limit_usd, remaining_usd,
                num_shopping_trips, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id, start_date, end_date, period_type,
            total_spent, budget_limit, remaining,
            num_trips, notes
        )

        budget_id = self.execute_write(query, params)
        print(f"[SUCCESS] Budget period saved (${total_spent:.2f}/${budget_limit:.2f})")
        return budget_id

    def get_spending_trends(
        self,
        weeks: int = 4,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """Analyze spending trends over multiple weeks."""

        trends = []
        today = date.today()

        for i in range(weeks):
            week_start = today - timedelta(days=today.weekday() + (i * 7))
            week_end = week_start + timedelta(days=6)

            spending = self.get_period_spending(week_start, week_end, user_id)
            trends.append({
                'week_start': week_start,
                'week_end': week_end,
                'total_spent': spending['total_spent'],
                'num_trips': spending['num_trips']
            })

        # Calculate averages
        total_spent = sum(t['total_spent'] for t in trends)
        avg_weekly = total_spent / weeks if weeks > 0 else 0

        # Get user budget
        user = self.user_manager.get_user(user_id)
        weekly_budget = user.get('weekly_budget_usd', 0) if user else 0

        return {
            'weeks_analyzed': weeks,
            'weekly_data': trends,
            'avg_weekly_spending': round(avg_weekly, 2),
            'weekly_budget': weekly_budget,
            'avg_over_under': round(avg_weekly - weekly_budget, 2),
            'is_trending_over': avg_weekly > weekly_budget
        }

    def get_category_breakdown(
        self,
        days: int = 30,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get spending breakdown by category."""

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        query = """
            SELECT
                category,
                COUNT(*) as num_items,
                SUM(total_price_usd) as total_spent,
                AVG(total_price_usd) as avg_item_price
            FROM shopping_history
            WHERE user_id = ?
            AND purchase_date >= ?
            AND purchase_date <= ?
            GROUP BY category
            ORDER BY total_spent DESC
        """

        categories = self.execute_query(query, (user_id, start_date, end_date))

        # Calculate percentages
        total = sum(cat['total_spent'] or 0 for cat in categories)

        for cat in categories:
            cat['percent_of_total'] = round((cat['total_spent'] / total * 100), 1) if total > 0 else 0
            cat['total_spent'] = round(cat['total_spent'] or 0, 2)
            cat['avg_item_price'] = round(cat['avg_item_price'] or 0, 2)

        return categories

    def get_price_history(
        self,
        item_name: str,
        days: int = 90,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get price history for a specific item."""

        query = """
            SELECT purchase_date, quantity, unit, unit_price_usd, total_price_usd, store
            FROM shopping_history
            WHERE user_id = ?
            AND item_name LIKE ?
            AND purchase_date >= date('now', '-' || ? || ' days')
            ORDER BY purchase_date DESC
        """

        return self.execute_query(query, (user_id, f"%{item_name}%", days))


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Budget Tracker")
    parser.add_argument('--weekly', action='store_true', help='Show weekly summary')
    parser.add_argument('--monthly', action='store_true', help='Show monthly summary')
    parser.add_argument('--trends', action='store_true', help='Show spending trends')
    parser.add_argument('--categories', action='store_true', help='Show category breakdown')
    parser.add_argument('--price-history', type=str, help='Show price history for item')

    parser.add_argument('--weeks', type=int, default=4, help='Weeks for trends (default: 4)')
    parser.add_argument('--days', type=int, default=30, help='Days for categories (default: 30)')

    args = parser.parse_args()

    tracker = BudgetTracker()

    if args.weekly:
        summary = tracker.get_weekly_summary()

        print("\nWeekly Budget Summary")
        print("=" * 60)
        print(f"Week: {summary['start_date']} to {summary['end_date']}")
        print(f"\nSpending: ${summary['total_spent']:.2f} / ${summary['budget_limit']:.2f}")
        print(f"Remaining: ${summary['remaining']:.2f} ({100 - summary['percent_used']:.1f}%)")

        if summary['is_over_budget']:
            print(f"\n[WARNING] Over budget by ${abs(summary['remaining']):.2f}!")
        else:
            print(f"\n[OK] Under budget by ${summary['remaining']:.2f}")

        print(f"\nShopping trips: {summary['num_trips']}")
        print(f"Items purchased: {summary['num_items']}")
        print(f"Avg per trip: ${summary['avg_per_trip']:.2f}")

        if summary['by_category']:
            print("\nBy Category:")
            print("-" * 60)
            for cat in sorted(summary['by_category'], key=lambda x: x['category_total'], reverse=True):
                cat_name = cat['category'] or 'uncategorized'
                print(f"  {cat_name:15} | ${cat['category_total']:7.2f} ({cat['category_count']:2} items)")

    elif args.monthly:
        summary = tracker.get_monthly_summary()

        print("\nMonthly Budget Summary")
        print("=" * 60)
        print(f"Month: {summary['start_date'].strftime('%B %Y')}")
        print(f"Period: {summary['start_date']} to {summary['end_date']}")
        print(f"\nSpending: ${summary['total_spent']:.2f} / ${summary['budget_limit']:.2f}")
        print(f"Remaining: ${summary['remaining']:.2f} ({100 - summary['percent_used']:.1f}%)")

        if summary['is_over_budget']:
            print(f"\n[WARNING] Over budget by ${abs(summary['remaining']):.2f}!")
        else:
            print(f"\n[OK] Under budget by ${summary['remaining']:.2f}")

        print(f"\nShopping trips: {summary['num_trips']}")
        print(f"Items purchased: {summary['num_items']}")
        print(f"Avg per trip: ${summary['avg_per_trip']:.2f}")

    elif args.trends:
        trends = tracker.get_spending_trends(weeks=args.weeks)

        print(f"\nSpending Trends (Last {trends['weeks_analyzed']} weeks)")
        print("=" * 60)
        print(f"Weekly budget: ${trends['weekly_budget']:.2f}")
        print(f"Avg weekly spending: ${trends['avg_weekly_spending']:.2f}")

        if trends['is_trending_over']:
            print(f"Trending OVER budget by ${abs(trends['avg_over_under']):.2f}/week")
        else:
            print(f"Trending UNDER budget by ${abs(trends['avg_over_under']):.2f}/week")

        print("\nWeekly Data:")
        print("-" * 60)
        for week in trends['weekly_data']:
            status = "OVER" if week['total_spent'] > trends['weekly_budget'] else "OK"
            print(f"{week['week_start']} | ${week['total_spent']:6.2f} | {week['num_trips']} trips | {status}")

    elif args.categories:
        categories = tracker.get_category_breakdown(days=args.days)

        print(f"\nCategory Breakdown (Last {args.days} days)")
        print("=" * 80)

        total = sum(cat['total_spent'] for cat in categories)
        print(f"Total spent: ${total:.2f}\n")

        for cat in categories:
            cat_name = (cat['category'] or 'uncategorized').title()
            bar_length = int(cat['percent_of_total'] / 2)
            bar = '#' * bar_length

            print(f"{cat_name:15} | ${cat['total_spent']:7.2f} ({cat['percent_of_total']:5.1f}%) | {bar}")
            print(f"                | {cat['num_items']:3} items @ ${cat['avg_item_price']:.2f} avg")
            print()

    elif args.price_history:
        history = tracker.get_price_history(args.price_history)

        if not history:
            print(f"No price history found for '{args.price_history}'")
        else:
            print(f"\nPrice History: {args.price_history}")
            print("=" * 80)

            for entry in history:
                store_str = f" @ {entry['store']}" if entry.get('store') else ""
                unit_price = f"${entry['unit_price_usd']:.2f}/{entry['unit']}" if entry.get('unit_price_usd') else "N/A"

                print(f"{entry['purchase_date']} | {entry['quantity']:.1f} {entry['unit']} | {unit_price}{store_str}")

            # Calculate average
            prices = [e['unit_price_usd'] for e in history if e.get('unit_price_usd')]
            if prices:
                avg_price = sum(prices) / len(prices)
                print(f"\nAverage price: ${avg_price:.2f}")

    else:
        parser.print_help()
