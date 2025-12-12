import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text in ["como comprar", "quero comprar", "onde compro", "como faço para comprar"]:
        keyboard = [[InlineKeyboardButton("🛒 Ir para a loja", url=EXTERNAL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await update.message.reply_video(
                video=VIDEO_FILE_ID,
                caption="🎥 Veja como comprar seus $RHAP!",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Erro ao enviar vídeo: {e}")
            await update.message.reply_text("❌ Desculpe, não consegui enviar o vídeo. Tente novamente mais tarde.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Erro no bot:", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logging.info("Bot iniciado com sucesso!")
    app.run_polling()

if __name__ == "__main__":
    main()
