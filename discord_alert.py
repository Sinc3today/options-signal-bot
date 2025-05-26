# output/discord_alert.py

import discord
import asyncio

# === REQUIRED: Replace with your actual Discord bot token and channel ID ===
TOKEN = "MTM3NDEyMzAzMjQxMDU4NzI0OA.GepmHS.32j1zXzlGMS_2bskSP8R1k8Bu-ShEUGF8x1FXQ"
CHANNEL_ID = 1373889877002944593  # Your channel ID where alerts should go

# === Initialize client ===
intents = discord.Intents.default()
intents.messages = True  # Allow receiving message events (needed to suppress command errors)
client = discord.Client(intents=intents)

# This queue holds messages until the bot is ready
alert_queue = []

def send_discord_alert(symbol, trend, signals):
    """Builds a formatted alert message and queues it for Discord posting."""
    emoji = "📈" if trend == "Bullish" else "📉" if trend == "Bearish" else "⚖️"

    content = (
        f"{emoji} **{symbol}**: **{trend}**\n"
        f"- EMA: {'✔️' if signals.get('ema_bullish') else '❌'}\n"
        f"- VWAP: {'Above' if signals.get('vwap_above') else 'Below'}\n"
        f"- MACD: {'Positive' if signals.get('macd_positive') else 'Negative'}\n"
        f"- RSI: {round(signals.get('rsi', 0), 2)}\n"
        f"- Volume Spike: {'🚀' if signals.get('volume_spike') else '—'}"
    )

    alert_queue.append(content)

@client.event
async def on_ready():
    """Triggered when the bot logs in successfully."""
    print(f"[DISCORD BOT ✅] Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("[DISCORD ERROR] Channel not found. Check CHANNEL_ID.")
        await client.close()
        return

    for content in alert_queue:
        try:
            await channel.send(content)
            print("[DISCORD ✅] Alert sent.")
        except Exception as e:
            print(f"[DISCORD ❌] Failed to send alert: {e}")

    # Close the bot once alerts are sent
    await client.close()

@client.event
async def on_message(message):
    """
    Suppresses accidental command inputs like `!clear`.
    This avoids Discord command errors showing up in the log.
    """
    if message.content.startswith("!") and not message.author.bot:
        print(f"[DISCORD INFO] Suppressed command input: {message.content}")

def run_discord_bot():
    """Safely runs the bot."""
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"[DISCORD ERROR] Bot failed to run: {e}")
