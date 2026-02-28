from utils import get_pivot_report_data
from telegram_light import escape_markdown_v2

CATEGORY_EMOJIS = {
    'Shopping': '🛍️',
    'Food': '🍴',
    'Transport': '🚗',
    'Utilities': '💡',
    'Entertainment': '🎭',
    'Personal': '👤',
    'Housing/Car': '🏠',
    'Other': '📦',
    'Income': '💰'
}

async def handle_report(ctx):
    """Handles the /report command using the Pivot Annual Report."""
    print("Handling /report command")
    # Send loading message and store the response to get message_id
    loading_msg = await ctx.reply("Fetching annual report... please wait.")
    loading_id = loading_msg.get("result", {}).get("message_id")
    
    try:
        # Fetch data from the specific Pivot sheet
        range_name = "'(Pivot) Annual Report'!A:K"
        values = await ctx.sheets_client.get_values(range_name)
        
        data = get_pivot_report_data(values)
        if not data:
            error_msg = "No records found for this period."
            if loading_id:
                await ctx.delete_message(loading_id)
            await ctx.reply(error_msg)
            return

        # Build simplified MarkdownV2 report with partial masking
        # For a full block quote, every line must start with '>'
        title = f"📅 Annual Report: {data['month']} {data['year']}"
        report = f">*{escape_markdown_v2(title)}*\n>\n"
        
        if data['summary']:
            report += f">*{escape_markdown_v2('Expenses by Category:')}*\n"
            # Sort by amount descending
            for cat, amt in sorted(data['summary'].items(), key=lambda x: x[1], reverse=True):
                emoji = CATEGORY_EMOJIS.get(cat, '📦')
                masked_amt = f"||{escape_markdown_v2(f'฿{amt:,.2f}')}||"
                report += f">{emoji} {escape_markdown_v2(cat)}: {masked_amt}\n"
        
        total_label = "Total Monthly Expense:"
        total_val = data['total']
        masked_total = f"||{escape_markdown_v2(f'฿{total_val:,.2f}')}||"
        
        report += f">\n>💰 *{escape_markdown_v2(total_label)}* {masked_total}"
        
        # Delete the "Fetching..." message if we have its ID
        if loading_id:
            await ctx.delete_message(loading_id)
        
        # Send the final report using MarkdownV2 and protect_content
        await ctx.reply(report, parse_mode='MarkdownV2', protect_content=True)
        
    except Exception as e:
        print(f"Error in handle_report: {e}")
        error_msg = "Sorry, failed to fetch the report."
        if loading_id:
            await ctx.delete_message(loading_id)
        await ctx.reply(error_msg)
