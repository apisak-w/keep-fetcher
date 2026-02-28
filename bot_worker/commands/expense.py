from utils import parse_record_message

async def handle_expense(ctx, text):
    """Handles the /expense command."""
    print("Handling /expense command")
    record = parse_record_message(text, is_expense=True)
    
    if not record:
        error = "Invalid format. Use: /expense <amount> <description> [category]"
        await ctx.reply(error)
    else:
        row = [record['date'], record['category'], record['description'], record['amount'], record['uncleared']]
        await ctx.sheets_client.append_row(row)
        await ctx.reply(f"✅ Recorded expense: ฿{record['amount']} for {record['description']}")
