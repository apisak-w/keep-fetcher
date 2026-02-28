from utils import parse_record_message

async def handle_income(ctx, text):
    """Handles the /income command."""
    print("Handling /income command")
    record = parse_record_message(text, is_expense=False)
    
    if not record:
        error = "Invalid format. Use: /income <amount> <description>"
        await ctx.reply(error)
    else:
        row = [record['date'], record['category'], record['description'], record['amount'], record['uncleared']]
        await ctx.sheets_client.append_row(row)
        await ctx.reply(f"✅ Recorded income: ฿{record['amount']} for {record['description']}")
