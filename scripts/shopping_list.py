"""
Shopping list generation from meal plans.
Creates optimized shopping lists, checks inventory, and aggregates ingredients.
"""

from datetime import date
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.db_manager import DatabaseManager
from scripts.inventory_manager import InventoryManager
from config.config import DEFAULT_USER_ID


class ShoppingListGenerator(DatabaseManager):
    """Generate and manage shopping lists."""

    def __init__(self, db_path=None):
        super().__init__(db_path=db_path)
        self.inventory_manager = InventoryManager(db_path=db_path) if db_path else InventoryManager()

        # Category mapping for organization
        self.category_map = {
            'protein': ['chicken', 'beef', 'pork', 'fish', 'turkey', 'eggs', 'tofu'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
            'produce': ['lettuce', 'tomato', 'onion', 'garlic', 'potato', 'carrot', 'broccoli', 'spinach', 'banana', 'apple', 'berry', 'berries'],
            'grain': ['rice', 'pasta', 'bread', 'oats', 'quinoa', 'tortilla'],
            'pantry': ['oil', 'salt', 'pepper', 'sauce', 'vinegar', 'honey', 'nuts'],
            'frozen': ['frozen'],
        }

    def generate_from_meals(
        self,
        meal_ids: List[int],
        servings_per_meal: Optional[List[int]] = None,
        check_inventory: bool = True,
        user_id: int = DEFAULT_USER_ID
    ) -> Dict:
        """
        Generate shopping list from selected meals.

        Args:
            meal_ids: List of meal template IDs
            servings_per_meal: Number of servings for each meal (default: 1 each)
            check_inventory: Whether to check inventory and subtract items on hand
            user_id: User ID
        """

        if not servings_per_meal:
            servings_per_meal = [1] * len(meal_ids)

        if len(servings_per_meal) != len(meal_ids):
            raise ValueError("servings_per_meal must match meal_ids length")

        # Aggregate ingredients across all meals
        ingredient_totals = defaultdict(lambda: {'quantity': 0, 'unit': None, 'meals': []})

        for meal_id, servings in zip(meal_ids, servings_per_meal):
            # Get meal info
            meal = self.execute_single("SELECT name, servings FROM meal_templates WHERE id = ?", (meal_id,))
            if not meal:
                print(f"[WARNING] Meal ID {meal_id} not found")
                continue

            # Get ingredients
            ingredients_query = """
                SELECT ingredient_name, quantity, unit, optional
                FROM meal_ingredients
                WHERE meal_template_id = ?
            """
            ingredients = self.execute_query(ingredients_query, (meal_id,))

            # Scale quantities based on servings
            serving_multiplier = servings / meal['servings'] if meal['servings'] else 1

            for ing in ingredients:
                if ing['optional']:
                    continue  # Skip optional ingredients

                name = ing['ingredient_name'].lower()
                scaled_quantity = ing['quantity'] * serving_multiplier

                # Aggregate (simple approach - same unit)
                if ingredient_totals[name]['unit'] is None:
                    ingredient_totals[name]['unit'] = ing['unit']
                    ingredient_totals[name]['quantity'] = scaled_quantity
                elif ingredient_totals[name]['unit'] == ing['unit']:
                    ingredient_totals[name]['quantity'] += scaled_quantity
                else:
                    # Different units - keep separate (TODO: unit conversion)
                    name_with_unit = f"{name} ({ing['unit']})"
                    ingredient_totals[name_with_unit]['unit'] = ing['unit']
                    ingredient_totals[name_with_unit]['quantity'] = scaled_quantity

                ingredient_totals[name]['meals'].append(meal['name'])

        # Check inventory
        items_to_buy = {}
        items_on_hand = []

        if check_inventory:
            inventory = self.inventory_manager.get_all_items(user_id)
            inventory_map = {item['item_name'].lower(): item for item in inventory}

            for ingredient, data in ingredient_totals.items():
                # Check if we have this ingredient
                if ingredient in inventory_map:
                    inv_item = inventory_map[ingredient]

                    # Check if we have enough (simple check - same unit)
                    if inv_item['unit'] == data['unit'] and inv_item['quantity'] >= data['quantity']:
                        items_on_hand.append({
                            'name': ingredient,
                            'quantity_needed': data['quantity'],
                            'quantity_on_hand': inv_item['quantity'],
                            'unit': data['unit']
                        })
                    else:
                        # Need more
                        shortage = data['quantity'] - (inv_item['quantity'] if inv_item['unit'] == data['unit'] else 0)
                        items_to_buy[ingredient] = {
                            'quantity': max(shortage, data['quantity']),
                            'unit': data['unit'],
                            'category': self._categorize_ingredient(ingredient),
                            'meals': list(set(data['meals']))
                        }
                else:
                    # Not in inventory
                    items_to_buy[ingredient] = {
                        'quantity': data['quantity'],
                        'unit': data['unit'],
                        'category': self._categorize_ingredient(ingredient),
                        'meals': list(set(data['meals']))
                    }
        else:
            # Don't check inventory - buy everything
            for ingredient, data in ingredient_totals.items():
                items_to_buy[ingredient] = {
                    'quantity': data['quantity'],
                    'unit': data['unit'],
                    'category': self._categorize_ingredient(ingredient),
                    'meals': list(set(data['meals']))
                }

        return {
            'items_to_buy': items_to_buy,
            'items_on_hand': items_on_hand,
            'total_items': len(items_to_buy),
            'meals_count': len(meal_ids)
        }

    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize ingredient for shopping list organization."""

        ingredient_lower = ingredient_name.lower()

        for category, keywords in self.category_map.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                return category

        return 'other'

    def format_shopping_list(self, shopping_list: Dict, group_by: str = 'category') -> str:
        """
        Format shopping list for display.

        Args:
            shopping_list: Shopping list dict from generate_from_meals
            group_by: 'category' or 'none'
        """

        items = shopping_list['items_to_buy']

        if not items:
            return "No items to buy - you have everything!"

        output = []
        output.append(f"Shopping List ({shopping_list['total_items']} items)")
        output.append("=" * 60)

        if group_by == 'category':
            # Group by category
            by_category = defaultdict(list)
            for name, data in items.items():
                by_category[data['category']].append((name, data))

            # Sort categories
            category_order = ['produce', 'protein', 'dairy', 'grain', 'frozen', 'pantry', 'other']
            for category in category_order:
                if category not in by_category:
                    continue

                output.append(f"\n{category.upper()}")
                output.append("-" * 60)

                for name, data in sorted(by_category[category]):
                    qty_str = f"{data['quantity']:.1f} {data['unit']}"
                    output.append(f"  [ ] {name.title():30} {qty_str:15}")

        else:
            # No grouping - alphabetical
            output.append("")
            for name, data in sorted(items.items()):
                qty_str = f"{data['quantity']:.1f} {data['unit']}"
                output.append(f"  [ ] {name.title():30} {qty_str:15}")

        # Show items already on hand
        if shopping_list['items_on_hand']:
            output.append(f"\n\nAlready on hand ({len(shopping_list['items_on_hand'])} items)")
            output.append("-" * 60)
            for item in shopping_list['items_on_hand']:
                output.append(f"  [X] {item['name'].title()} - have {item['quantity_on_hand']:.1f} {item['unit']}")

        return '\n'.join(output)

    def save_shopping_trip(
        self,
        items_purchased: List[Dict],
        user_id: int = DEFAULT_USER_ID,
        purchase_date: date = None,
        store: Optional[str] = None
    ) -> int:
        """
        Record a shopping trip.

        Args:
            items_purchased: List of dicts with {name, quantity, unit, total_price, unit_price}
            user_id: User ID
            purchase_date: Date of purchase (default: today)
            store: Store name
        """

        if not purchase_date:
            purchase_date = date.today()

        count = 0
        total_spent = 0

        for item in items_purchased:
            query = """
                INSERT INTO shopping_history (
                    user_id, purchase_date, item_name, quantity, unit,
                    unit_price_usd, total_price_usd, store, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            category = self._categorize_ingredient(item['name'])
            total_price = item.get('total_price', 0)
            total_spent += total_price

            params = (
                user_id,
                purchase_date,
                item['name'],
                item['quantity'],
                item['unit'],
                item.get('unit_price'),
                total_price,
                store,
                category
            )

            self.execute_write(query, params)
            count += 1

        print(f"[SUCCESS] Recorded {count} items from shopping trip (${total_spent:.2f})")
        return count

    def get_shopping_history(
        self,
        days: int = 30,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Dict]:
        """Get shopping history for recent days."""

        query = """
            SELECT * FROM shopping_history
            WHERE user_id = ?
            AND purchase_date >= date('now', '-' || ? || ' days')
            ORDER BY purchase_date DESC, item_name ASC
        """

        return self.execute_query(query, (user_id, days))


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shopping List Generator")
    parser.add_argument('--generate', nargs='+', type=int, help='Generate list from meal IDs')
    parser.add_argument('--servings', nargs='+', type=int, help='Servings for each meal (default: 1)')
    parser.add_argument('--no-inventory', action='store_true', help='Don\'t check inventory')
    parser.add_argument('--history', action='store_true', help='Show shopping history')
    parser.add_argument('--days', type=int, default=30, help='Days for history (default: 30)')

    args = parser.parse_args()

    generator = ShoppingListGenerator()

    if args.generate:
        print(f"\nGenerating shopping list for {len(args.generate)} meals...")
        print("=" * 60)

        shopping_list = generator.generate_from_meals(
            meal_ids=args.generate,
            servings_per_meal=args.servings,
            check_inventory=not args.no_inventory
        )

        print(generator.format_shopping_list(shopping_list, group_by='category'))

        print(f"\n\nTotal items to buy: {shopping_list['total_items']}")
        if shopping_list['items_on_hand']:
            print(f"Items already on hand: {len(shopping_list['items_on_hand'])}")

    elif args.history:
        history = generator.get_shopping_history(days=args.days)

        if not history:
            print(f"No shopping history in the last {args.days} days")
        else:
            print(f"\nShopping History (Last {args.days} days)")
            print("=" * 80)

            total_spent = sum(item.get('total_price_usd', 0) or 0 for item in history)
            trips = len(set(item['purchase_date'] for item in history))

            print(f"Total spent: ${total_spent:.2f}")
            print(f"Shopping trips: {trips}")
            print(f"Items purchased: {len(history)}")

            current_date = None
            for item in history:
                if item['purchase_date'] != current_date:
                    current_date = item['purchase_date']
                    print(f"\n{current_date}")
                    if item.get('store'):
                        print(f"Store: {item['store']}")
                    print("-" * 80)

                price_str = f"${item['total_price_usd']:.2f}" if item.get('total_price_usd') else 'N/A'
                print(f"  {item['item_name']:30} | {item['quantity']:6.1f} {item['unit']:8} | {price_str}")

    else:
        parser.print_help()
