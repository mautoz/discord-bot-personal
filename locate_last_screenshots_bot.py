#!/usr/bin/env python3.8
import os
from datetime import datetime, timedelta
import logging
import random
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv


load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN_SCREENSHOT"))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DATENA_QUOTES = [
    "No Brasil, o Presidente da República é quem manda menos!",
    "Mudem as leis!",
    "Existe o princípio coercitivo da lei! Matou, é cana, vai preso!",
    "Não adianta [o Brasil] ser a quinta potência se isso aí não chega à mesa, às escolas, aos hospitais… essa é que é a grande verdade.",
    "Eu quero 'ibagens' cadê as 'ibagens', comandante Hamilton?!",
    "Você vê a que ponto chegamos com a banalização da vida humana?",
    "Helicóptero Águia, vôo pela vida!",
    "Essa é a grande realidade!",
    "Cadê as autoridades que não vêem isso?",
    "Isso é uma calamidade pública!",
    "Isso é um tapa na cara da sociedade!",
    "Isso é uma pouca vergonha!",
    "Comandante Hamilton, o Melhor News no ar do mundo",
    "Isso é uma barbárie!",
    "As estradas brasileiras são verdadeiros matadouros a céu aberto!",
    "Me ajuda aí, ô!",
    "O crime cospe na cara da sociedade!",
    "Ôoo, cara pálida!",
    "Jesus, ao vivo aqui! Marcelo 'Gigante', aqui! Latino, põe na tela, por gentileza!",
    "Bandido na cadeia e polícia na rua!",
    "Bandido da pior espécie!",
    "Se levantar a arma para a polícia, prega fogo nele!",
    "…ou eu tô errado? Ou eu tô mentindo?",
    "O povo é quem paga a conta!",
    "Porrada neles!",
    "Parem de mamar nas tetas do governo!",
    "Coitado do aposentado!",
    "Onde nós vamos parar?!",
    "Os canalhas também envelhecem!",
    "O serviço público no Brasil, seja ele qual for, é sempre uma porcaria! PORCARIA!!!",
    "Chupa que a cana é doce!!",
    "Banana para vocês!!",
    "Olha a destreza dos pilotos do Águia, tô mentindo comandante 'Uan'!",
    "Comandante Hamilton, filho de peixe, peixinho é!",
    "Tá de brincadeira comigo!",
]

THIS_DAY = datetime.today()
LAST_WEEK = THIS_DAY - timedelta(days=7)

def get_last_screenshots() -> list:
    screenschots_directory = os.getenv('SCREENSHOT_DIRECTORY')
    png_files = [
        filename
        for filename in os.listdir(screenschots_directory)
        if filename.endswith(".png")
    ]

    print(png_files)
    file_dates = {}

    for filename in png_files:
        print(type(screenschots_directory), type(filename))
        full_path = os.path.join(str(screenschots_directory), str(filename))
        stat_info = os.stat(full_path)
        timestamp = stat_info.st_mtime
        date = datetime.fromtimestamp(timestamp)
        if date > LAST_WEEK:
            file_dates[filename] = date

    sorted_files = sorted(file_dates.items(), key=lambda x: x[1])
    logging.info(sorted_files)

    return sorted_files


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Type /help if it's your first time!")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("/medaibagens")


def medaibagens(update, context):
    # Get the chat ID
    chat_id = update.message.chat_id

    # Specify the folder where your images are located
    screenschots_directory = os.getenv('SCREENSHOT_DIRECTORY')

    images_files = get_last_screenshots()

    if not images_files:
        update.message.reply_text("Sem screenshots novos")
        return

    update.message.reply_text(random.choice(DATENA_QUOTES))
    # Iterate through the image files and send each one
    for image_file in images_files:
        with open(
            os.path.join(screenschots_directory, image_file[0]), "rb"
        ) as image:
            bot.send_photo(chat_id, photo=image)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Here is where you will put your token
    updater = Updater(
        token=os.getenv("TELEGRAM_TOKEN_SCREENSHOT"), use_context=True
    )
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
