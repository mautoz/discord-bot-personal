#!/usr/bin/env python3.8
import os
from datetime import datetime, timedelta
import logging
import random
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN_SCREENSHOT"))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DEFAULT_URL = os.getenv("DEFAULT_JN_URL")

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

def get_last_screenshots(days: int) -> list:
    days_before = THIS_DAY - timedelta(days=days)

    screenschots_directory = os.getenv('SCREENSHOT_DIRECTORY')
    png_files = [
        filename
        for filename in os.listdir(screenschots_directory)
        if filename.endswith(".png")
    ]

    file_dates = {}

    for filename in png_files:
        full_path = os.path.join(str(screenschots_directory), str(filename))
        stat_info = os.stat(full_path)
        timestamp = stat_info.st_mtime
        date = datetime.fromtimestamp(timestamp)
        if date > days_before:
            file_dates[filename] = date

    sorted_files = sorted(file_dates.items(), key=lambda x: x[1])
    logging.info(sorted_files)

    return sorted_files


def get_photo_msg(update, days: int, chat_id: int, want_img: bool = False):
    chat_id = update.message.chat_id

    screenschots_directory = os.getenv('SCREENSHOT_DIRECTORY')

    images_files = get_last_screenshots(days)

    if not images_files:
        update.message.reply_text(f"Sem screenshots novos para {days} dia(s) atrás!")
        return

    update.message.reply_text(random.choice(DATENA_QUOTES))
    for image_file in images_files:
        with open(
            os.path.join(screenschots_directory, image_file[0]), "rb"
        ) as image:
            image_name = str(image_file[0]).split(".")
            if want_img:
                bot.send_photo(chat_id, photo=image)
            bot.send_message(
                chat_id,
                f"{DEFAULT_URL}{image_name[0]}"
            )


def medaibagens(update, context):
    chat_id = update.message.chat_id
    try:
        if not context.args:
            bot.send_message(
                chat_id,
                "Você não forneceu um intervalo de dias! Faça algo como medaibagens 7 (para os últimos 7 dias)"
            )
        else:
            interval = int(context.args[0])

    except ValueError:
        bot.send_message(
                chat_id,
                "O intervalo de dias dado não é válido!"
            )

    else: 
        if interval >=0:
            get_photo_msg(update, interval, chat_id, want_img=True)
        else:
            bot.send_message(
                chat_id,
                "Aqui não é De Volta Para O Futuro! Digite um número maior que zero!"
            )


def medalinks(update, context):
    chat_id = update.message.chat_id
    try:
        if not context.args:
            bot.send_message(
                chat_id,
                "Você não forneceu um intervalo de dias! Faça algo como medalinks 7 (para os últimos 7 dias)"
            )
        else:
            interval = int(context.args[0])


    except ValueError:        
        bot.send_message(
                chat_id,
                "O intervalo de dias dado não é válido!"
            )

    else: 
        if interval >=0:
            get_photo_msg(update, interval, chat_id)
        else:
            bot.send_message(
                chat_id,
                "Aqui não é De Volta Para O Futuro! Digite um número maior que zero!"
            )


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Type /help if it's your first time!")


def datena(update, context):
    update.message.reply_text(random.choice(DATENA_QUOTES))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message with information about available commands."""
    user = update.effective_user
    message = (
        f"Olá, {user.mention_markdown_v2()}\n"
        "Comandos válidos:\n\n"
        "/help Mostra os comandos atuais\n"
        "/datena Frases aleatórias do Datena\n"
        "/medaibagens N Troque N pelo número de dias retroativos que deseja\n"
        "/medalinks N Troque N pelo número de dias retroativos que deseja"
    )
    update.message.reply_markdown_v2(message)


def main():
    """Start the bot."""
    updater = Updater(
        token=os.getenv("TELEGRAM_TOKEN_SCREENSHOT"), use_context=True
    )
    dp = updater.dispatcher

    # My commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("medaibagens", medaibagens))
    dp.add_handler(CommandHandler("medalinks", medalinks))
    dp.add_handler(CommandHandler("datena", datena))
    dp.add_handler(CommandHandler("help", help_command))

    # Errors
    dp.add_error_handler(error)

    # Starting the bot
    updater.start_polling()

    # If you want to stop, press CTRL+C
    updater.idle()


if __name__ == "__main__":
    main()
