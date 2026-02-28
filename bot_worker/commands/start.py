async def handle_start(ctx):
    """Handles the /start command."""
    print("Handling /start command")
    welcome = (
        "Hi! I'm your Expense Manager Bot (Lightweight Worker Edition).\n\n"
        "Commands:\n"
        "/expense <amount> <description> [category]\n"
        "/income <amount> <description>\n"
        "/report - Get current month summary\n"
        "/report [mm-yyyy] - Get specific month summary"
    )
    await ctx.reply(welcome)
