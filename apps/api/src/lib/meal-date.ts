/**
 * Calendar date in UTC derived from a timestamp (for meal_date column).
 */
export function toUtcMealDate(date: Date): Date {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

/**
 * YYYY-MM-DD in UTC for the given instant.
 */
export function utcDateKey(date: Date): string {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, '0');
  const d = String(date.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function parseUtcDateKey(key: string): Date {
  const [y, mo, d] = key.split('-').map(Number);
  if (!y || !mo || !d) throw new Error('Invalid date');
  return new Date(Date.UTC(y, mo - 1, d));
}
