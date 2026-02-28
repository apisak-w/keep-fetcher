import re
from datetime import datetime
from shared.config.constants import EXPENSE_CATEGORIES

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
            report += f"- {cat}: ฿{amt:,.2 f}\n"
    
    report += f"\n*Total Expense:* ฿{total_expense:,.2f}"
    report += f"\n*Total Income:* ฿{total_income:,.2f}"
    report += f"\n*Balance:* ฿{total_income - total_expense:,.2f}"
    
    return report
