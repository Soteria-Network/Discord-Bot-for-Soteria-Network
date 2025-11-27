# Discord Bot for Soteria Network (SOTER)

Welcome to the Discord Bot designed to provide real-time updates and statistics for Soteria Network (SOTER) cryptocurrency. This bot automatically creates and updates voice channels in your Discord server, displaying essential information such as difficulty, hashrate, block count, supply, price, and market cap.

## Features

- **Real-time Updates:** Stay informed with up-to-date statistics from the Soteria blockchain.
- **Automatic Channel Creation:** The bot dynamically generates voice channels to display key metrics.
- **Privacy Management:** Channels are automatically set to private, restricting access to maintain data integrity.

Coming soon:

    block height

    difficulty

    hashrate

    supply

    price and market cap

    member count

That’s already enough to give our community confidence and a sense of “pulse” on the network. Later, you will expand with:

    staking stats (once we add staking features)

    charity fund balances (to highlight social impact)

    donor reward tracking (so contributors see their recognition in real time)

    latest block explorer links (quick jump to transactions)

    alerts for milestones (e.g., supply thresholds, difficulty spikes, price surges)


## Installation and Configuration

Follow these steps to install, configure, and run the bot on your Discord server:

### Step 1: Prerequisites

- [Python](https://www.python.org/) installed on your machine.
- Discord account with the necessary permissions to add a bot to your server.

### Step 2: Clone the Repository

```bash
git clone https://github.com/Soteria-Network/Discord-Bot-for-Soteria-Network.git
cd Soteria-Discord-Bot
```

### Step 3: Create and Activate a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
### Step 4: Install Dependencies

```bash
pip install discord requests python-dotenv aiohttp
```

### Step 5: Configure the Bot

1. Copy the `.env.template` file to `.env`.
2. Add your Discord bot token to the .env file:

```bash
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
API_TOKEN=YOUR_TOKEN_HERE
```

3. Set Permissions for .env
```bash
chmod 600 .env
```
This step ensures that only the owner of the file has read and write permissions, providing an extra layer of security for sensitive information.

### Step 6: Run the Bot

```bash
python bot.py
```

### Step 7: Invite the Bot to Your Server
1. Go to the Discord Developer Portal.
2. Create a new application and add a bot to it.
3. Copy the bot token.
4. On OAuth2 --> URL Generator --> select bot and set administrator permission.
5. Use the link to invite the bot to your server

### Step 8: Enjoy!
Your Soteria Discord bot is now set up and running on your server. Channels will be automatically created under the category "Server Stats" and updated with the latest data of the Soteria blockchain.

Feel free to customize the bot to suit your server's needs, and don't hesitate to reach out for any assistance or feature requests.
# Soteria-Discord-Bot
