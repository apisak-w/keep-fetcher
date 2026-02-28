from utils import format_report

async def handle_report(ctx):
    """Handles the /report command."""
    print("Handling /report command")
    await ctx.reply("Fetching report... please wait.")
    records = await ctx.sheets_client.get_all_records()
    report_text = format_report(records)
    await ctx.reply(report_text)
