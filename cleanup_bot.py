# cleanup_bot.py (Command-based version)

import discord
from discord.ext import commands
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("Discord_Cleanup_Bot_Token")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🧹 Cleanup Bot is online as {bot.user}")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    """Deletes a specified number of messages (default 10)."""
    deleted = await ctx.channel.purge(limit=amount + 1)  # includes the !clear command itself
    await ctx.send(f"🧼 Deleted {len(deleted) - 1} messages.", delete_after=5)
    print(f"[CLEANUP] {len(deleted) - 1} messages deleted in #{ctx.channel.name}")

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to delete messages.", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Usage: `!clear 10`", delete_after=5)
    else:
        await ctx.send("❌ Something went wrong.", delete_after=5)
        print(f"[ERROR] {error}")


@bot.command(name="show_pending")
async def show_pending(ctx):
    """Displays all pending entries from pending_entries.csv"""
    path = "output/logs/pending_entries.csv"
    if not os.path.exists(path):
        await ctx.send("📂 No pending entries file found.")
        return

    df = pd.read_csv(path)
    pending = df[df["Status"] == "waiting"]

    if pending.empty:
        await ctx.send("✅ No pending entries right now.")
        return

    preview = pending[["Symbol", "Entry Condition", "Signal Source Time"]].head(10)
    lines = "\n".join([f"`{row.Symbol}` | {row['Entry Condition']} | {row['Signal Source Time'][:16]}" for _, row in
                       preview.iterrows()])

    await ctx.send(f"📋 **Pending Entries**:\n{lines}")

    @bot.command(name="status")
    async def status(ctx, symbol: str):
        """Show the latest prediction or trade status for a given stock symbol."""
        symbol = symbol.upper()

        pred_path = "output/logs/predictions.csv"
        trades_path = "output/logs/trades.csv"

        try:
            # Load predictions
            if not os.path.exists(pred_path):
                await ctx.send("❌ Predictions file not found.")
                return
            df_pred = pd.read_csv(pred_path)
            df_pred = df_pred[df_pred["Symbol"].str.upper() == symbol]

            # Load trades
            trade_lines = []
            if os.path.exists(trades_path):
                df_trades = pd.read_csv(trades_path)
                df_trades = df_trades[df_trades["Symbol"].str.upper() == symbol]
                if not df_trades.empty:
                    last_trade = df_trades.iloc[-1]
                    trade_lines.append(
                        f"💼 Last Trade: `{last_trade['Entry Time'][:16]}` at `{last_trade['Entry Price']}`")
                    if pd.notna(last_trade["Exit Time"]):
                        trade_lines.append(
                            f"➡️ Exit: `{last_trade['Exit Time'][:16]}` at `{last_trade['Exit Price']}` ({last_trade['Outcome']})")
                    else:
                        trade_lines.append("⏳ Trade still open.")

            if df_pred.empty:
                await ctx.send(f"📉 No recent prediction found for `{symbol}`.")
                return

            last_pred = df_pred.iloc[-1]
            lines = [
                f"📊 **{symbol} Status**",
                f"• Trend: **{last_pred['Trend']}**",
                f"• RSI: {last_pred['RSI']}",
                f"• MACD: {last_pred['MACD']}",
                f"• EMA: {last_pred['EMA']}",
                f"• VWAP: {last_pred['VWAP']}",
                f"• Volume Spike: {'🚀' if last_pred['Volume Spike'] == 'True' else '—'}",
                f"• Signal Time: `{last_pred['Signal Source Time'][:16]}`",
            ]

            lines += trade_lines
            await ctx.send("\n".join(lines))

        except Exception as e:
            await ctx.send(f"⚠️ Error fetching status for `{symbol}`.")
            print(f"[ERROR] status command: {e}")

@bot.command(name="mark_entry")
async def mark_entry(ctx, symbol: str):
    """Marks a pending entry as entered and logs it as a trade."""
    symbol = symbol.upper()
    path = "output/logs/pending_entries.csv"

    if not os.path.exists(path):
        await ctx.send("❌ No pending entries file found.")
        return

    df = pd.read_csv(path)
    df_symbol = df[(df["Symbol"].str.upper() == symbol) & (df["Status"] == "waiting")]

    if df_symbol.empty:
        await ctx.send(f"⚠️ No waiting entry found for `{symbol}`.")
        return

    row = df_symbol.iloc[-1]  # Use the most recent one
    entry_price = float(row["signal_high"]) if row["Trend"] == "Bullish" else float(row["signal_low"])
    now = pd.Timestamp.now()

    # Update pending entry
    df.loc[df_symbol.index[-1], "Status"] = "entered"
    df.loc[df_symbol.index[-1], "Entry Time"] = now.isoformat()
    df.to_csv(path, index=False)


    await ctx.send(f"✅ `{symbol}` marked as entered and logged to trades.")

bot.run(TOKEN)
