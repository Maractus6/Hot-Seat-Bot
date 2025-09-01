# Hot-Seat-Bot

A Discord bot designed to facilitate a fun "hot seat" question game among friends in your server. The bot asks a series of engaging questions, and users can take turns answering in the "hot seat," leading to entertaining discussions and discoveries.

## Prerequisites

- Python 3.8+
- A virtual environment named `bot-env/`
- Required dependencies listed in `requirements.txt`
- A Discord Bot Token (see "Setup" below)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/Hot-Seat-Bot.git](https://github.com/your-username/Hot-Seat-Bot.git)
    cd Hot-Seat-Bot
    ```
2.  **Create and activate the virtual environment:**
    ```bash
    python3 -m venv bot-env
    source bot-env/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure your Discord Bot Token:**
    Your bot requires a token to connect to Discord. You can obtain this token from the Discord Developer Portal. For a detailed guide on how to get your bot token, please refer to this article: [How To Get A Discord Bot Token (Step-by-Step Guide)](https://www.writebots.com/discord-bot-token/)

    Once you have your token, create a file named `.env` in the root directory of the project and add your Discord bot token:
    ```
    DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
    ```
    (Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token.)

## Running the Bot

1.  **Activate the virtual environment:**
    ```bash
    source bot-env/bin/activate
    ```
2.  **Run the bot:**
    ```bash
    python3 main.py
    ```

## How to Play / Commands

Once the bot is running and invited to your server, you can use the following commands:

* `/start_game`: Initiates a new "hot seat" game.
* `/next_question`: Asks the next question in the sequence.
* `/end_game`: Ends the current hot seat game.

(Adjust commands based on your bot's actual functionality.)

## Contributing

---
