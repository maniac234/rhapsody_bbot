from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TOKEN = os.getenv("TOKEN")
BOT_ID = os.getenv("BOT_ID", "")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# URL do jogo no GitHub Pages
GAME_URL = os.getenv("GAME_URL", "https://maniac234.github.io/game3/")

# Armazena última mensagem de boas-vindas por chat_id
last_welcome_message = {}

# Gatilhos de compra
TRIGGERS = ["como comprar", "onde comprar", "quero comprar", "comprar rhap", "como compra"]

# --- CONFIGURAR WEBHOOK ---
def set_webhook():
    """Configura o webhook para receber mensagens do Telegram"""
    if not RENDER_EXTERNAL_URL:
        print("⚠️ RENDER_EXTERNAL_URL não configurada!")
        return
    
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
    try:
        payload = {"url": webhook_url}
        response = requests.post(f"{TELEGRAM_API}/setWebhook", json=payload)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Webhook configurado com sucesso!")
            print(f"URL: {webhook_url}")
        else:
            print(f"❌ Erro ao configurar webhook: {result}")
    except Exception as e:
        print(f"❌ Erro: {e}")

# --- FUNÇÕES DE SUPORTE ---
def send_welcome(chat_id, first_name):
    global last_welcome_message

    if chat_id in last_welcome_message:
        try:
            requests.post(f"{TELEGRAM_API}/deleteMessage", json={
                "chat_id": chat_id,
                "message_id": last_welcome_message[chat_id]
            })
        except:
            pass

    welcome_text = (
        f"🎮 Bem-vindo, {first_name}, à Comunidade Rhapsody!\n\n"
        "Este é o espaço oficial para quem acredita no poder da gamificação e das novas formas de engajar pessoas.\n\n"
        "Aqui você vai:\n"
        "✅ Descobrir novidades do projeto e do token RHAP\n"
        "✅ Entender como funciona nosso ecossistema de recompensas\n"
        "✅ Participar de eventos, ativações e conversas sobre o futuro digital\n"
        "✅ Conectar-se com outras pessoas que estão construindo junto\n\n"
        "🚀 Rhapsody Protocol — A nova camada do engajamento digital.\n\n"
        "🌐 rhapsodycoin.com"
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 Site oficial", "url": "https://www.rhapsodycoin.com"}],
            [
                {"text": "📌 FAQ", "callback_data": "faq"},
                {"text": "🛒 Compre RHAP", "url": "https://rhapsody.criptocash.app/"}
            ],
            [
                {"text": "🎮 Jogar Rhaps Catcher", "web_app": {"url": GAME_URL}}
            ],
            [{"text": "📱 Redes sociais", "callback_data": "redes_sociais"}],
            [{"text": "⚡ Desafio Maniac", "url": "https://maniac234.github.io/game3/"}]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
        if response.status_code == 200:
            msg_data = response.json()
            if msg_data.get("ok"):
                last_welcome_message[chat_id] = msg_data["result"]["message_id"]
                print(f"✅ Mensagem de boas-vindas enviada com sucesso!")
            else:
                print(f"❌ Erro ao enviar mensagem: {msg_data}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exceção ao enviar: {e}")

def send_faq(chat_id):
    faq_text = (
        "📌 *Aqui está a lista de perguntas frequentes atualizada sobre o Rhapsody Protocol*\n\n"
        "*Em que situação está o projeto atualmente?*\n"
        "O Rhapsody Protocol está em fase de pré-venda, que vai até 20 de janeiro de 2026 na plataforma CriptoCash. O lançamento oficial do token $RHAP ocorrerá em 23 de janeiro de 2026 na Bitcoin Brasil (BBT).\n\n"
        "*O token $RHAP já foi lançado?*\n"
        "Não, o token $RHAP ainda não foi lançado publicamente. Ele será disponibilizado oficialmente em 23 de janeiro de 2026 na Bitcoin Brasil.\n\n"
        "*Em qual rede o projeto e o token serão lançados?*\n"
        "O Rhapsody Protocol e o token $RHAP operam na rede Ethereum, seguindo o padrão ERC-20.\n\n"
        "*Qual o supply total do token $RHAP?*\n"
        "O supply total é fixo em 1.000.000.000 (1 bilhão) de tokens RHAP.\n\n"
        "*Qual será a função do token $RHAP?*\n"
        "O $RHAP é o token utilitário central do ecossistema. Será usado para acessar aplicações gamificadas, participar de mecânicas de recompensas, mintar NFTs e futuramente votar em decisões da DAO."
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "📘 Leia nosso Whitepaper", "url": "https://rhapsody-coin.gitbook.io/rhapsody-protocol/"}]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": faq_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
        "reply_markup": keyboard
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def send_social_media(chat_id):
    payload = {
        "chat_id": chat_id,
        "text": "📱 *Redes Sociais*:\n\n"
                "🔗 [Twitter/X](https://twitter.com/rhapsodycoin)\n"
                "📸 [Instagram](https://instagram.com/rhapsodycoin)\n"
                "💼 [LinkedIn](https://linkedin.com/company/rhapsody-protocol)\n"
                "🎥 [YouTube](https://youtube.com/@rhapsodyprotocol)\n"
                "💬 [Telegram Oficial](https://t.me/rhapsodycoin)",
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def send_buy_message(chat_id):
    """Resposta ao detectar gatilhos de compra"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "💰 Compre RHAP Agora", "url": "https://rhapsody.criptocash.app/"}],
            [{"text": "📌 Ver FAQ", "callback_data": "faq"}]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "💎 *Quer comprar $RHAP?*\n\n"
                "Acesse nossa plataforma de pré-venda na CriptoCash e comece a acumular tokens para o lançamento oficial!",
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

# --- WEBHOOK ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]

        # Novo membro entrou no grupo → Enviar boas-vindas
        if "new_chat_member" in message:
            new_member = message["new_chat_member"]
            user_id = new_member.get("id")
            is_bot = new_member.get("is_bot", False)
            first_name = new_member.get("first_name", "amigo")
            
            print(f"🔔 Novo membro detectado: {first_name} (ID: {user_id}, Bot: {is_bot})")
            
            # Ignorar se for outro bot (mas não o nosso)
            if is_bot:
                print(f"❌ Ignorando bot: {first_name}")
                return "OK"
            
            # Ignorar se for o próprio bot entrando
            if BOT_ID and str(user_id) == BOT_ID:
                print(f"❌ Ignorando o próprio bot")
                return "OK"
            
            print(f"✅ Enviando boas-vindas para {first_name}")
            send_welcome(chat_id, first_name)
            return "OK"

        # Mensagens de texto
        if "text" in message:
            text = message["text"].lower().strip()
            first_name = message["from"].get("first_name", "amigo")

            if text == "/start":
                if message["chat"]["type"] == "private":
                    send_welcome(chat_id, first_name)
                else:
                    reply = {
                        "chat_id": chat_id,
                        "text": "👋 Olá! Para ver todas as opções, envie /start em uma conversa privada comigo.",
                        "reply_to_message_id": message["message_id"]
                    }
                    requests.post(f"{TELEGRAM_API}/sendMessage", json=reply)
                return "OK"

            # Gatilhos de compra
            for trigger in TRIGGERS:
                if trigger in text:
                    send_buy_message(chat_id)
                    return "OK"

    # Callbacks
    if data and "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        callback_data = callback.get("data", "")

        if callback_data == "faq":
            send_faq(chat_id)
        elif callback_data == "redes_sociais":
            send_social_media(chat_id)

        # Responder callback
        requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    return "OK"

# Inicializar webhook ao rodar
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=5000)
