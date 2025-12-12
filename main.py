import os
import logging
from flask import Flask
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔐 Token e link vindos de variáveis de ambiente
TOKEN = os.getenv("TOKEN")
EXTERNAL_LINK = os.getenv("EXTERNAL_LINK", "https://rhapsody.criptocash.app")

# 🎥 file_id do vídeo
VIDEO_FILE_ID = "BAACAgEAAxkBAAMyaTtJds7IEDJZKrPlUClLPkQ6gdsAAsMGAAKQcthFypomT3bj9iM2BA"

if not TOKEN:
    raise ValueError("A variável de ambiente 'TOKEN' não foi definida.")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🤖 Lógica do bot
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()
    if text in ["como comprar", "quero comprar", "onde compro", "como faço para comprar"]:
        keyboard = [[InlineKeyboardButton("🛒 Ir para a loja", url=EXTERNAL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            update.message.reply_video(
                video=VIDEO_FILE_ID,
                caption="🎥 Veja como comprar seus $RHAP!",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Erro ao enviar vídeo: {e}")
            update.message.reply_text("❌ Desculpe, não consegui enviar o vídeo. Tente novamente mais tarde.")

def error_handler(update: Update, context: CallbackContext):
    logging.error("Erro no bot:", exc_info=context.error)

# 🌐 Servidor Flask para keep-alive
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "✅ Bot online!", 200

@app_flask.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

# 🚀 Inicialização
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Adiciona handlers
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)

    logging.info("Bot iniciado com sucesso!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    main()
