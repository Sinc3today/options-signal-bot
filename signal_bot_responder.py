import discord
import csv
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("Discord_Alert_Bot_Token")
EMOJI_TRIGGER = "👀"
PREDICTIONS_PATH = "output/logs/predictions.csv"

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_predictions():
    predictions = {}
    try:
        with open(PREDICTIONS_PATH, "r") as f:
            reader = csv.DictReader(f)
            for row in reversed(list(reader)):
                symbol = row["Symbol"].strip().upper()
                if symbol not in predictions:
                    predictions[symbol] = row
        print(f"[DEBUG] Loaded predictions for symbols: {list(predictions.keys())}")
    except Exception as e:
        print(f"[ERROR] Could not load predictions: {e}")
    return predictions

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user.name}")

@bot.event
async def on_reaction_add(reaction, user):
    print(f"[DEBUG] A reaction was added: {reaction.emoji} by {user.name}")

    if user.bot:
        print("[DEBUG] Bot reacted — skipping.")
        return

    if str(reaction.emoji) != EMOJI_TRIGGER:
        print(f"[DEBUG] Ignored non-👀 emoji: {reaction.emoji}")
        return

    message = reaction.message
    print(f"[DEBUG] Processing 👀 reaction for message from {message.author}")

    predictions = load_predictions()

    try:
        lines = message.content.splitlines()
        if not lines:
            print("[DEBUG] Message has no lines.")
            return

        first_line = lines[0]
        print(f"[DEBUG] First message line: {first_line}")

        if "**" not in first_line:
            print("[DEBUG] No symbol formatting found.")
            return

        symbol = first_line.split("**")[1].strip().upper()
        print(f"[DEBUG] Extracted symbol: {symbol}")

        if symbol not in predictions:
            print(f"[DEBUG] Symbol '{symbol}' not found in predictions.")
            await message.reply(f"🔍 No signal breakdown found for **{symbol}**")
            return

        data = predictions[symbol]
        trend = data['Trend']
        response = (
            f"🧠 **Signal Breakdown for {symbol}**\n"
            f"> Trend: **{trend}**\n"
            f"- EMA: {data['EMA']}\n"
            f"- VWAP: {data['VWAP']}\n"
            f"- MACD: {data['MACD']}\n"
            f"- RSI: {data['RSI']}\n"
            f"- Volume Spike: {'🚀' if data['Volume Spike'] == 'True' else '—'}\n\n"
            f"{'📈' if trend == 'Bullish' else '📉' if trend == 'Bearish' else '⚖️'} "
            f"{_tip(trend)}"
        )

        await message.reply(response)
        print(f"[DEBUG] Replied with breakdown for {symbol}.")

    except Exception as e:
        print(f"[ERROR] While handling reaction: {e}")


def _tip(trend):
    if trend == "Bullish":
        return "Consider calls or bull spreads if volume supports."
    elif trend == "Bearish":
        return "Consider puts or bear spreads based on confirmation."
    return "Neutral trend — consider waiting for a stronger signal."

bot.run(TOKEN)
