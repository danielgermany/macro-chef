/**
 * Utility functions for exporting data to CSV format
 */

export function downloadCSV(data: any[], filename: string) {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    // Header row
    headers.map(h => `"${h}"`).join(','),
    // Data rows
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Handle null/undefined
        if (value === null || value === undefined) return '""';
        // Escape quotes and wrap in quotes
        return `"${String(value).replace(/"/g, '""')}"`;
      }).join(',')
    ),
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

export function exportMealLogs(meals: any[], filename?: string) {
  const exportData = meals.map(meal => ({
    Date: meal.meal_date,
    'Meal Time': meal.meal_time,
    'Meal Name': meal.meal_name,
    Calories: meal.calories,
    'Protein (g)': meal.protein_g,
    'Carbs (g)': meal.carbs_g,
    'Fat (g)': meal.fat_g,
    'Fiber (g)': meal.fiber_g || '',
    'Sugar (g)': meal.sugar_g || '',
    'Saturated Fat (g)': meal.saturated_fat_g || '',
    'Sodium (mg)': meal.sodium_mg || '',
    'Cholesterol (mg)': meal.cholesterol_mg || '',
    'Serving Size': meal.serving_size || '',
    Rating: meal.rating || '',
    Notes: meal.notes || '',
  }));

  downloadCSV(exportData, filename || `meal_logs_${new Date().toISOString().split('T')[0]}.csv`);
}

export function exportNutritionSummary(progress: any[], filename?: string) {
  const exportData = progress.map(day => ({
    Date: day.date,
    'Calories Consumed': day.totals?.calories || 0,
    'Calories Target': day.targets?.calories_target || 0,
    'Calories Remaining': day.remaining?.calories || 0,
    'Protein Consumed (g)': day.totals?.protein_g || 0,
    'Protein Target (g)': day.targets?.protein_target_g || 0,
    'Protein Remaining (g)': day.remaining?.protein_g || 0,
    'Carbs Consumed (g)': day.totals?.carbs_g || 0,
    'Carbs Target (g)': day.targets?.carbs_target_g || 0,
    'Carbs Remaining (g)': day.remaining?.carbs_g || 0,
    'Fat Consumed (g)': day.totals?.fat_g || 0,
    'Fat Target (g)': day.targets?.fat_target_g || 0,
    'Fat Remaining (g)': day.remaining?.fat_g || 0,
  }));

  downloadCSV(exportData, filename || `nutrition_summary_${new Date().toISOString().split('T')[0]}.csv`);
}

export function exportBodyMetrics(metrics: any[], filename?: string) {
  const exportData = metrics.map(metric => ({
    Date: metric.date,
    'Weight (lbs)': metric.weight_lbs,
    'Body Fat (%)': metric.body_fat_pct || '',
    'Muscle Mass (lbs)': metric.muscle_mass_lbs || '',
    'Waist (inches)': metric.waist_inches || '',
    'Chest (inches)': metric.chest_inches || '',
    'Arms (inches)': metric.arms_inches || '',
    'Legs (inches)': metric.legs_inches || '',
    Notes: metric.notes || '',
  }));

  downloadCSV(exportData, filename || `body_metrics_${new Date().toISOString().split('T')[0]}.csv`);
}

export function exportInventory(items: any[], filename?: string) {
  const exportData = items.map(item => ({
    'Item Name': item.item_name,
    Quantity: item.quantity,
    Unit: item.unit,
    Category: item.category || '',
    Location: item.location || '',
    'Expiration Date': item.expiration_date || '',
    Notes: item.notes || '',
  }));

  downloadCSV(exportData, filename || `inventory_${new Date().toISOString().split('T')[0]}.csv`);
}
