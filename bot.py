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
import requests
from bs4 import BeautifulSoup

def get_best_exchange_rates():
    headers = {"User-Agent": "Mozilla/5.0"}

    # URLs for USD and EUR exchange rates in Moscow
    urls = {
        "USD": "https://www.banki.ru/products/currency/cash/usd/moskva/",
        "EUR": "https://www.banki.ru/products/currency/cash/eur/moskva/"
    }

    results = "\n💰 **Best Exchange Rates in Moscow:**\n"

    for currency, url in urls.items():
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            results += f"\n⚠️ Error fetching {currency} rates.\n"
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Extracting bank names
        bank_names = [bank.text.strip() for bank in soup.find_all("div", class_="Text__sc-vycpdy-0 OiTuY")]

        # Extracting buy and sell rates
        all_rates = [rate.text.strip() for rate in soup.find_all("div", class_="Text__sc-vycpdy-0 cQqMIr") if "₽" in rate.text]

        if len(bank_names) == 0 or len(all_rates) < 2 * len(bank_names):
            results += f"\n⚠️ No valid {currency} exchange rates found.\n"
            continue

        # Pairing banks with their buy and sell rates
        exchange_data = []
        for i in range(len(bank_names)):
            bank = bank_names[i]
            buy_rate = all_rates[i * 2]  # Every first rate is Buy
            sell_rate = all_rates[i * 2 + 1]  # Every second rate is Sell
            exchange_data.append((bank, buy_rate, sell_rate))

        # Sort by highest buy rate
        exchange_data = sorted(exchange_data, key=lambda x: float(x[1].replace(",", ".")), reverse=True)

        # Get the top 7 buy rates
        results += f"\n🔹 **Top 7 Buy Rates for {currency}:**\n"
        for bank, buy_rate, sell_rate in exchange_data[:7]:
            results += f"{bank}: Buy {buy_rate} ₽ | Sell {sell_rate} ₽\n"

    return results




# Command to fetch and send exchange rates
async def send_exchange_rates(update: Update, context: CallbackContext):
    rates = get_best_exchange_rates()
    await update.message.reply_text(rates, parse_mode='Markdown')

# Scheduled function to send daily updates
async def daily_update(app):
    rates = get_best_exchange_rates()
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
