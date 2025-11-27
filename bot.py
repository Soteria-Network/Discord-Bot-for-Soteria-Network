#bot.py
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import logging
import time
import os
from dotenv import load_dotenv

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("soteria-bot")

# --- Load environment variables ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
RPC_URL = os.getenv("SOTERIA_RPC_URL", "https://soteria-rpc-mainnet.soteria-network.site/rpc")
SUPPLY_URL = os.getenv("SOTERIA_SUPPLY_URL", "https://explorer.soteria-network.site/api/getcoinsupply")
COINGECKO_URL = os.getenv(
    "COINGECKO_URL",
    "https://api.coingecko.com/api/v3/coins/soteria?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
)

# --- Discord intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

# --- Channel keys for normalization ---
CHANNEL_KEYS = {
    "members": "Members:",
    "difficulty_soterg": "Difficulty (SoterG):",
    "hashrate_soterg": "Hashrate (SoterG): GH/s",
    "block": "Block:",
    "supply": "Supply:",
    "price": "Price:",
    "volume_24h": "24h Volume: $",
    "market_cap": "Market Cap: $",
}

# --- RPC helper ---
async def make_rpc_call(session, method, params=None):
    if params is None:
        params = []
    payload = {"method": method, "params": params}
    try:
        async with session.post(RPC_URL, headers={"Content-Type": "application/json"}, json=payload) as response:
            if response.status != 200:
                log.warning(f"RPC {method} returned HTTP {response.status}")
                return None
            data = await response.json(content_type=None)
            return data.get("result")
    except Exception as e:
        log.error(f"Error making RPC call {method}: {e}")
        return None

# --- Channel helpers ---
def norm(s: str) -> str:
    return s.lower().replace(" ", "").strip()

async def get_or_create_channel(category, channel_key):
    target = CHANNEL_KEYS[channel_key]
    target_norm = norm(target)
    for ch in category.voice_channels:
        if norm(ch.name).startswith(target_norm):
            return ch
    return await category.create_voice_channel(target)

async def set_channel_private(category, channel):
    try:
        if isinstance(channel, discord.VoiceChannel) and channel.category == category:
            await channel.set_permissions(channel.guild.default_role, connect=False)
    except Exception as e:
        log.error(f"Error setting channel private: {e}")

async def update_channel(guild, category, key, value):
    try:
        channel = await get_or_create_channel(category, key)
        await channel.edit(name=f"{CHANNEL_KEYS[key]} {value}")
    except Exception as e:
        log.error(f"Error updating channel {key}: {e}")

# --- Stats updater ---
async def update_stats_channels(guild):
    try:
        async with aiohttp.ClientSession() as session:
            # Difficulty
            difficulty_soterg = await make_rpc_call(session, "getdifficulty", [0]) or "N/A"

            # Hashrate
            hashrate_soterg = await make_rpc_call(session, "getnetworkhashps", [0, -1, "soterg"])
            hashrate_soterg = f"{hashrate_soterg/1e9:,.3f}" if isinstance(hashrate_soterg, (int, float)) else "N/A"

            # Block count
            block_count = await make_rpc_call(session, "getblockcount", []) or "N/A"

            # Supply
            try:
                async with session.get(SUPPLY_URL) as response:
                    supply_data = await response.json()
                    supply = f"{float(supply_data['coinsupply'])/1_000_000_000:,.2f}B SOTER"
            except Exception:
                supply = "N/A"

            # CoinGecko
            try:
                async with session.get(COINGECKO_URL) as response:
                    data = await response.json()
                    md = data.get("market_data", {})
                    current_price = (md.get("current_price") or {}).get("usd")
                    volume_24h = (md.get("total_volume") or {}).get("usd")
                    market_cap = (md.get("market_cap") or {}).get("usd")
                    change_24h = md.get("price_change_percentage_24h")

                    price_core = f"${current_price:.6f}" if isinstance(current_price, (int, float)) else "N/A"
                    if isinstance(change_24h, (int, float)):
                        arrow = "▲ +"+f"{change_24h:.2f}%" if change_24h >= 0 else "▼ "+f"{change_24h:.2f}%"
                        price_display = f"{price_core} ({arrow} 24h)"
                    else:
                        price_display = price_core

                    volume_display = f"{volume_24h:,.0f}" if isinstance(volume_24h, (int, float)) else "N/A"
                    market_cap_display = f"{market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"

                log.info("CoinGecko data retrieved successfully")
            except Exception as e:
                log.error(f"Error fetching CoinGecko data: {e}")
                price_display = volume_display = market_cap_display = "N/A"

        member_count = guild.member_count or "N/A"

        # Category
        category_name = "Soteria Server Stats"
        category = discord.utils.get(guild.categories, name=category_name)

        if not category:
            log.info(f"Creating category '{category_name}'")
            category = await guild.create_category(category_name)

        await asyncio.sleep(0.5)

        # Update channels
        await update_channel(guild, category, "members", f"{member_count:,}")
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "difficulty_soterg", difficulty_soterg)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "hashrate_soterg", hashrate_soterg)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "block", block_count)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "supply", supply)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "price", price_display)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "volume_24h", volume_display)
        await asyncio.sleep(0.5)
        await update_channel(guild, category, "market_cap", market_cap_display)

        # Lock channels
        for ch in category.voice_channels:
            await set_channel_private(category, ch)

    except Exception as e:
        log.exception("Error updating stats channels")

# --- Task loop ---
@tasks.loop(minutes=5)
async def update_stats_task():
    for guild in client.guilds:
        log.info(f"Updating stats for guild '{guild.name}'")
        await update_stats_channels(guild)

@client.event
async def on_ready():
    log.info("Bot is ready")
    update_stats_task.start()

client.run(TOKEN)
