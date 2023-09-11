#!/usr/bin/env python3.8
import os
from datetime import datetime, timedelta
import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv


load_dotenv()
bot = Bot(token=os.getenv('TELEGRAM_TOKEN_SCREENSHOT'))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

THIS_DAY = datetime.today()
LAST_WEEK = THIS_DAY - timedelta(days=7)

def get_last_screenshots() -> list:
    current_directory = os.getcwd()
    png_files = [filename for filename in os.listdir(current_directory) if filename.endswith(".png")]

    print(png_files)
    file_dates = {}

    for filename in png_files:
        print(type(current_directory), type(filename))
        full_path = os.path.join(str(current_directory), str(filename))
        stat_info = os.stat(full_path)
        timestamp = stat_info.st_mtime
        date = datetime.fromtimestamp(timestamp)
        if date > LAST_WEEK and date <= THIS_DAY:
            file_dates[filename] = date

    sorted_files = sorted(file_dates.items(), key=lambda x: x[1])
    logging.info(sorted_files)

    return sorted_files


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Type /help if it's your first time!")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "/medaibagens"
    )


def medaibagens(update, context):
    # Get the chat ID
    chat_id = update.message.chat_id

    # Specify the folder where your images are located
    current_directory = os.getcwd()

    images_files = get_last_screenshots()

    if not images_files:
        update.message.reply_text("Sem screen shots novos")
        return

    # Iterate through the image files and send each one
    for image_file in images_files:
        with open(os.path.join(current_directory, image_file[0]), "rb") as image:
            bot.send_photo(chat_id, photo=image)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Here is where you will put your token
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN_SCREENSHOT'), use_context=True)
    dp = updater.dispatcher

    # My commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("medaibagens", medaibagens))


    # Errors
    dp.add_error_handler(error)

    # Starting the bot
    updater.start_polling()

    # If you want to stop, press CTRL+C
    updater.idle()


if __name__ == "__main__":
    main()

