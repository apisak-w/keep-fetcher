import re
from datetime import datetime

EXPENSE_CATEGORIES = {
    'Shopping': [
        'book', 'gift', 'clothes', 'shoes', 'bag', 'amazon', 'lazada', 
        'shopee', 'sofa', 'tuya', 'adapter', 'phone', 'belt', 'coffee table', 
        'battery', 'key', 'ladle', 'lamp', 'perfume', 'rug', 'stairs', 
        'home appliance', 'housewares', 'shirt', 'shorts', 'toothpaste'
    ],
    'Food': [
        'food', 'lunch', 'dinner', 'breakfast', 'snack', 'meal', 'drink'
    ],
    'Transport': [
        'mrt', 'bts', 'taxi', 'motorcycle', 'bus', 'rabbit', 'grab', 'uber', 
        'train', 'flight', 'tsubaru', 'airport', 'express', 'two row car', 
        'arl', 'srt'
    ],
    'Utilities': [
        'mobile', 'top-up', 'mobile top up', 'icloud', 'internet', 'bill', 
        'subscription', 'netflix', 'spotify'
    ],
    'Entertainment': [
        'movie', 'cinema', 'game', 'concert', 'ticket', 'show', 'party', 
        'bar', 'club', 'youtube', 'disney', 'badminton'
    ],
    'Personal': [
        'haircut', 'gym', 'sport', 'massage', 'spa', 'doctor', 'medicine', 
        'driving', 'medical', 'personal care'
    ],
    'Housing/Car': [
        'car', 'rent', 'condo', 'electricity', 'water', 'home', 'house'
    ],
}

def parse_record_message(text, is_expense=True):
    """
    Parse a message for recording income or expense.
    Expected format: 
    - /expense <amount> <description> [category]
    - /income <amount> <description>
    """
    # Remove command
    clean_text = re.sub(r'^/(expense|income)\s*', '', text, flags=re.IGNORECASE).strip()
    if not clean_text:
        return None

    # Split by whitespace, max split for description/category
    # Pattern: <amount> <description...> [category]
    parts = clean_text.split()
    if len(parts) < 2:
        return None

    try:
        amount = float(parts[0])
    except ValueError:
        return None

    if is_expense:
        # Check if the last word is a known category
        category = 'Other'
        description = " ".join(parts[1:])
        
        last_word = parts[-1].capitalize()
        if last_word in EXPENSE_CATEGORIES:
            category = last_word
            description = " ".join(parts[1:-1])
        else:
            # Try to auto-categorize based on description
            desc_lower = description.lower()
            for cat, keywords in EXPENSE_CATEGORIES.items():
                if any(keyword in desc_lower for keyword in keywords):
                    category = cat
                    break
        
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'category': category,
            'description': description,
            'amount': amount,
            'uncleared': False  # Default to False for bot entries
        }
    else:
        # Income parsing
        description = " ".join(parts[1:])
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'category': 'Income',
            'description': description,
            'amount': amount,
            'uncleared': False
        }

def format_report(records):
    """
    Format a list of records into a readable report.
    """
    if not records:
        return "No records found for this period."

    # Group by category for the current month
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    month_records = [r for r in records if str(r.get('date', '')).startswith(current_month)]
    
    if not month_records:
        return f"No records found for {now.strftime('%B %Y')}."

    summary = {}
    total_expense = 0
    total_income = 0

    for r in month_records:
        cat = r.get('category', 'Other')
        amount = float(r.get('amount', 0))
        if cat == 'Income':
            total_income += amount
        else:
            total_expense += amount
            summary[cat] = summary.get(cat, 0) + amount

    report = f"*Report for {now.strftime('%B %Y')}*\n\n"
    
    if summary:
        report += "*Expenses by Category:*\n"
        for cat, amt in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            report += f"- {cat}: ฿{amt:,.2f}\n"
    
    report += f"\n*Total Expense:* ฿{total_expense:,.2f}"
    report += f"\n*Total Income:* ฿{total_income:,.2f}"
    report += f"\n*Balance:* ฿{total_income - total_expense:,.2f}"
    
    return report

def get_pivot_report_data(values):
    """
    Extract structured data from pivot table values.
    Returns: {
        'month': 'Feb',
        'year': '2026',
        'summary': {'Food': 123.45, ...},
        'total': 1234.56
    } or None if not found.
    """
    if not values or len(values) < 3:
        return None

    # Row 2 contains headers
    headers = values[1]
    # Categories are from column index 2 to second to last (before Grand Total)
    categories = headers[2:-1]
    
    now = datetime.now()
    target_year = now.strftime("%Y")
    target_month = now.strftime("%b") # e.g., 'Feb'
    
    current_year = ""
    target_row = None
    
    for row in values[2:]:
        # Update current year if present in Column A
        if len(row) > 0 and str(row[0]).strip() and "Total" not in str(row[0]):
            current_year = str(row[0]).strip()
        
        # Check if this row matches our target year and month
        if current_year == target_year and len(row) > 1 and str(row[1]).strip() == target_month:
            target_row = row
            break
            
    if not target_row:
        return None

    summary = {}
    total_expense = 0
    
    # Extract category values (start from index 2)
    for i, cat in enumerate(categories):
        val_idx = i + 2
        if val_idx < len(target_row):
            val = target_row[val_idx]
            try:
                amount = float(val) if val != "" else 0
                if amount > 0:
                    summary[cat] = amount
                    total_expense += amount
            except (ValueError, TypeError):
                continue
    
    # Grand Total is the last column
    try:
        grand_total = float(target_row[len(headers)-1]) if len(target_row) >= len(headers) else total_expense
    except (ValueError, TypeError):
        grand_total = total_expense

    return {
        'month': target_month,
        'year': target_year,
        'summary': summary,
        'total': grand_total
    }

def format_pivot_report(values):
    """
    Format a report from pivot table values.
    """
    data = get_pivot_report_data(values)
    if not data:
        return "No report data found for this period."

    report = f"*Annual Report: {data['month']} {data['year']}*\n\n"
    
    if data['summary']:
        report += "*Expenses by Category:*\n"
        # Sort by amount descending
        for cat, amt in sorted(data['summary'].items(), key=lambda x: x[1], reverse=True):
            report += f"- {cat}: ฿{amt:,.2f}\n"
    
    report += f"\n*Total Monthly Expense:* ฿{data['total']:,.2f}"
    
    return report
