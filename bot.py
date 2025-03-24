import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = '7233591034:AAGBxHiNul11QLiOXJ-fYp1c3pAvThK_LMI'
CHAT_ID = '1937722356'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to scrape exchange rates from Banki.ru
def get_exchange_rates():
    url = "https://www.banki.ru/products/currency/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Error fetching exchange rates. Try again later."

    soup = BeautifulSoup(response.text, "html.parser")

    # Known list of major currencies in the order they appear on Banki.ru
    known_currencies = ["USD", "EUR", "GBP", "CNY"]  # Add more if needed

    # Extract exchange rates
    rate_divs = soup.find_all("div", class_="Text__sc-vycpdy-0 cQqMIr")

    if not rate_divs or len(rate_divs) < len(known_currencies) * 2:
        return "Failed to extract exchange rate data."

    rates = "\n💰 **Daily Exchange Rates:**\n"

    # Iterate through rates and assign to known currencies
    for i in range(len(known_currencies)):
        currency = known_currencies[i]
        buy_rate = rate_divs[i * 2].text.strip()
        sell_rate = rate_divs[i * 2 + 1].text.strip()
        rates += f"{currency}: Buy {buy_rate} | Sell {sell_rate}\n"

    return rates

# Command to fetch and send exchange rates
async def send_exchange_rates(update: Update, context: CallbackContext):
    rates = get_exchange_rates()
    await update.message.reply_text(rates, parse_mode='Markdown')

# Scheduled function to send daily updates
async def daily_update(app):
    rates = get_exchange_rates()
    await app.bot.send_message(chat_id=CHAT_ID, text=rates, parse_mode='Markdown')

# Main function to start the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("rates", send_exchange_rates))
    
    # Schedule daily updates at 9 AM Moscow Time
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.create_task(daily_update(app)), 'cron', hour=9, minute=0)
    scheduler.start()
    
    app.run_polling()

if __name__ == "__main__":
    main()
