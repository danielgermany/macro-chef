"""
Inventory management for tracking food items.
CRUD operations for food inventory with expiration tracking.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from config.config import DEFAULT_USER_ID


class InventoryManager(DatabaseManager):
    """Manage food inventory with expiration tracking."""

    def add_item(
        self,
        item_name: str,
        quantity: float,
        unit: str,
        category: Optional[str] = None,
        purchase_date: Optional[date] = None,
        expiration_date: Optional[date] = None,
        location: str = "pantry",
        notes: Optional[str] = None,
        user_id: int = DEFAULT_USER_ID
    ) -> int:
        """Add item to inventory."""

        if not purchase_date:
            purchase_date = date.today()

        # Validate location
        valid_locations = ['fridge', 'freezer', 'pantry']
        if location not in valid_locations:
            print(f"[WARNING] Location '{location}' not standard. Valid: {valid_locations}")

        # Validate category
        valid_categories = ['protein', 'grain', 'vegetable', 'fruit', 'dairy', 'pantry', 'frozen', 'other']
        if category and category not in valid_categories:
            print(f"[WARNING] Category '{category}' not standard. Valid: {valid_categories}")

        query = """
            INSERT INTO inventory (
                user_id, item_name, quantity, unit, category,
                purchase_date, expiration_date, location, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_id, item_name, quantity, unit, category,
            purchase_date, expiration_date, location, notes
        )

        item_id = self.execute_write(query, params)
        print(f"[SUCCESS] Added to inventory: {quantity} {unit} {item_name}")
        return item_id

    def get_item(self, item_id: int) -> Optional[Dict]:
        """Get single inventory item by ID."""
        query = "SELECT * FROM inventory WHERE id = ?"
        return self.execute_single(query, (item_id,))

    def get_all_items(
        self,
        user_id: int = DEFAULT_USER_ID,
        location: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get all inventory items, optionally filtered by location or category."""

        if location and category:
            query = """
                SELECT * FROM inventory
                WHERE user_id = ? AND location = ? AND category = ?
                ORDER BY expiration_date ASC NULLS LAST, item_name ASC
            """
            params = (user_id, location, category)
        elif location:
            query = """
                SELECT * FROM inventory
                WHERE user_id = ? AND location = ?
                ORDER BY expiration_date ASC NULLS LAST, item_name ASC
            """
            params = (user_id, location)
        elif category:
            query = """
                SELECT * FROM inventory
                WHERE user_id = ? AND category = ?
                ORDER BY expiration_date ASC NULLS LAST, item_name ASC
            """
            params = (user_id, category)
        else:
            query = """
                SELECT * FROM inventory
                WHERE user_id = ?
                ORDER BY expiration_date ASC NULLS LAST, item_name ASC
            """
            params = (user_id,)

        return self.execute_query(query, params)

    def search_items(self, search_term: str, user_id: int = DEFAULT_USER_ID) -> List[Dict]:
        """Search inventory items by name."""
        query = """
            SELECT * FROM inventory
            WHERE user_id = ? AND item_name LIKE ?
            ORDER BY item_name ASC
        """
        return self.execute_query(query, (user_id, f"%{search_term}%"))

    def update_item(
        self,
        item_id: int,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        expiration_date: Optional[date] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Update inventory item fields."""

        # Build dynamic update query
        updates = []
        params = []

        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)
        if unit is not None:
            updates.append("unit = ?")
            params.append(unit)
        if expiration_date is not None:
            updates.append("expiration_date = ?")
            params.append(expiration_date)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        if not updates:
            print("[WARNING] No fields to update")
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(item_id)

        query = f"""
            UPDATE inventory
            SET {', '.join(updates)}
            WHERE id = ?
        """

        self.execute_write(query, tuple(params))
        print(f"[SUCCESS] Inventory item updated (ID: {item_id})")
        return True

    def use_item(self, item_id: int, quantity_used: float) -> bool:
        """Reduce item quantity. Delete if quantity reaches 0."""

        item = self.get_item(item_id)
        if not item:
            print(f"[ERROR] Item not found (ID: {item_id})")
            return False

        new_quantity = item['quantity'] - quantity_used

        if new_quantity <= 0:
            self.delete_item(item_id)
            print(f"[SUCCESS] Used all {item['item_name']} - removed from inventory")
        else:
            self.update_item(item_id, quantity=new_quantity)
            print(f"[SUCCESS] Used {quantity_used} {item['unit']} {item['item_name']} ({new_quantity} {item['unit']} remaining)")

        return True

    def delete_item(self, item_id: int) -> bool:
        """Delete item from inventory."""
        query = "DELETE FROM inventory WHERE id = ?"
        self.execute_write(query, (item_id,))
        print(f"[SUCCESS] Item removed from inventory (ID: {item_id})")
        return True

    def get_expiring_soon(
        self,
        days: int = 7,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get items expiring within specified days."""

        query = """
            SELECT * FROM inventory
            WHERE user_id = ?
            AND expiration_date IS NOT NULL
            AND expiration_date <= date('now', '+' || ? || ' days')
            ORDER BY expiration_date ASC
        """

        return self.execute_query(query, (user_id, days))

    def get_expired_items(self, user_id: int = DEFAULT_USER_ID) -> List[Dict]:
        """Get items that have already expired."""

        query = """
            SELECT * FROM inventory
            WHERE user_id = ?
            AND expiration_date IS NOT NULL
            AND expiration_date < date('now')
            ORDER BY expiration_date DESC
        """

        return self.execute_query(query, (user_id,))

    def get_inventory_summary(self, user_id: int = DEFAULT_USER_ID) -> Dict:
        """Get summary of inventory by location and category."""

        # By location
        location_query = """
            SELECT location, COUNT(*) as count, SUM(quantity) as total_items
            FROM inventory
            WHERE user_id = ?
            GROUP BY location
            ORDER BY location
        """
        by_location = self.execute_query(location_query, (user_id,))

        # By category
        category_query = """
            SELECT category, COUNT(*) as count
            FROM inventory
            WHERE user_id = ?
            GROUP BY category
            ORDER BY category
        """
        by_category = self.execute_query(category_query, (user_id,))

        # Total items
        total_query = "SELECT COUNT(*) as total FROM inventory WHERE user_id = ?"
        total_result = self.execute_single(total_query, (user_id,))
        total_items = total_result['total'] if total_result else 0

        # Expiring soon count
        expiring = len(self.get_expiring_soon(days=7, user_id=user_id))
        expired = len(self.get_expired_items(user_id=user_id))

        return {
            'total_items': total_items,
            'by_location': by_location,
            'by_category': by_category,
            'expiring_soon_7days': expiring,
            'expired': expired
        }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inventory Manager")
    parser.add_argument('--add', action='store_true', help='Add item to inventory')
    parser.add_argument('--list', action='store_true', help='List all inventory items')
    parser.add_argument('--search', type=str, help='Search for item by name')
    parser.add_argument('--expiring', action='store_true', help='Show items expiring soon')
    parser.add_argument('--summary', action='store_true', help='Show inventory summary')
    parser.add_argument('--use', type=int, help='Use item by ID')

    # Add item arguments
    parser.add_argument('--name', type=str, help='Item name')
    parser.add_argument('--quantity', type=float, help='Quantity')
    parser.add_argument('--unit', type=str, help='Unit (lbs, oz, count, cups, etc)')
    parser.add_argument('--category', type=str, help='Category (protein, grain, vegetable, etc)')
    parser.add_argument('--location', type=str, default='pantry', help='Location (fridge, freezer, pantry)')
    parser.add_argument('--expires', type=str, help='Expiration date (YYYY-MM-DD)')
    parser.add_argument('--days-until-expire', type=int, help='Days until expiration')

    # Filter arguments
    parser.add_argument('--filter-location', type=str, help='Filter by location')
    parser.add_argument('--filter-category', type=str, help='Filter by category')
    parser.add_argument('--days', type=int, default=7, help='Days for expiring soon (default: 7)')

    # Use item arguments
    parser.add_argument('--amount', type=float, help='Amount to use from item')

    args = parser.parse_args()

    manager = InventoryManager()

    if args.add:
        if not all([args.name, args.quantity, args.unit]):
            print("[ERROR] --name, --quantity, --unit are required for adding items")
            parser.print_help()
        else:
            # Parse expiration date
            expiration_date = None
            if args.expires:
                expiration_date = date.fromisoformat(args.expires)
            elif args.days_until_expire:
                expiration_date = date.today() + timedelta(days=args.days_until_expire)

            manager.add_item(
                item_name=args.name,
                quantity=args.quantity,
                unit=args.unit,
                category=args.category,
                expiration_date=expiration_date,
                location=args.location
            )

    elif args.list:
        items = manager.get_all_items(
            location=args.filter_location,
            category=args.filter_category
        )

        if not items:
            print("No items in inventory.")
        else:
            print(f"\nInventory ({len(items)} items)")
            print("=" * 80)

            current_location = None
            for item in items:
                if item['location'] != current_location:
                    current_location = item['location']
                    print(f"\n{current_location.upper()}")
                    print("-" * 80)

                exp_str = f"Expires: {item['expiration_date']}" if item['expiration_date'] else "No expiration"
                cat_str = f"[{item['category']}]" if item['category'] else ""

                print(f"ID {item['id']:3} | {item['item_name']:30} | {item['quantity']:6.1f} {item['unit']:8} | {exp_str} {cat_str}")

    elif args.search:
        items = manager.search_items(args.search)

        if not items:
            print(f"No items found matching '{args.search}'")
        else:
            print(f"\nSearch results for '{args.search}' ({len(items)} items)")
            print("=" * 80)
            for item in items:
                exp_str = f"Expires: {item['expiration_date']}" if item['expiration_date'] else "No expiration"
                print(f"ID {item['id']:3} | {item['item_name']:30} | {item['quantity']:6.1f} {item['unit']:8} | {exp_str}")

    elif args.expiring:
        items = manager.get_expiring_soon(days=args.days)
        expired = manager.get_expired_items()

        if expired:
            print(f"\n[WARNING] EXPIRED ITEMS ({len(expired)})")
            print("=" * 80)
            for item in expired:
                days_ago = (date.today() - date.fromisoformat(item['expiration_date'])).days
                print(f"ID {item['id']:3} | {item['item_name']:30} | {item['quantity']:6.1f} {item['unit']:8} | Expired {days_ago} days ago")

        if items:
            print(f"\nExpiring within {args.days} days ({len(items)} items)")
            print("=" * 80)
            for item in items:
                days_left = (date.fromisoformat(item['expiration_date']) - date.today()).days
                urgency = "[URGENT]" if days_left <= 3 else ""
                print(f"ID {item['id']:3} | {item['item_name']:30} | {item['quantity']:6.1f} {item['unit']:8} | {days_left} days left {urgency}")

        if not items and not expired:
            print(f"No items expiring within {args.days} days.")

    elif args.summary:
        summary = manager.get_inventory_summary()

        print("\nInventory Summary")
        print("=" * 60)
        print(f"Total items: {summary['total_items']}")

        if summary['expired'] > 0:
            print(f"[WARNING] Expired items: {summary['expired']}")
        if summary['expiring_soon_7days'] > 0:
            print(f"Expiring within 7 days: {summary['expiring_soon_7days']}")

        if summary['by_location']:
            print("\nBy Location:")
            print("-" * 60)
            for loc in summary['by_location']:
                print(f"  {loc['location']:10} | {loc['count']:3} items")

        if summary['by_category']:
            print("\nBy Category:")
            print("-" * 60)
            for cat in summary['by_category']:
                cat_name = cat['category'] or 'uncategorized'
                print(f"  {cat_name:15} | {cat['count']:3} items")

    elif args.use:
        if not args.amount:
            print("[ERROR] --amount required when using --use")
        else:
            manager.use_item(args.use, args.amount)

    else:
        parser.print_help()
