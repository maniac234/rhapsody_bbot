from flask import Flask, request
import requests
import os
import threading
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TOKEN = os.getenv("TOKEN")
BOT_ID = os.getenv("BOT_ID", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# URL do jogo no GitHub Pages
GAME_URL = os.getenv("GAME_URL", "https://maniac234.github.io/game3/")

# Armazena última mensagem de boas-vindas por chat_id
last_welcome_message = {}

# Armazena usuários aguardando confirmação: {user_id: chat_id}
pending_users = {}

# Gatilhos de compra
TRIGGERS = ["como comprar", "onde comprar", "quero comprar", "comprar rhap", "como compra"]

# --- FUNÇÕES DE SUPORTE ---
def remove_user_if_pending(chat_id, user_id):
    time.sleep(60)
    if user_id in pending_users:
        try:
            requests.post(f"{TELEGRAM_API}/banChatMember", json={"chat_id": chat_id, "user_id": user_id})
            time.sleep(1)
            requests.post(f"{TELEGRAM_API}/unbanChatMember", json={"chat_id": chat_id, "user_id": user_id})
        except:
            pass
        pending_users.pop(user_id, None)

def send_captcha(chat_id, user_id, first_name):
    message = f"👋 Olá, {first_name}! Para confirmar que você é humano, clique no botão abaixo:"
    keyboard = {"inline_keyboard": [[{"text": "✅ Sou humano", "callback_data": f"captcha_{user_id}"}]]}
    payload = {"chat_id": chat_id, "text": message, "reply_markup": keyboard}
    response = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
    if response.status_code == 200:
        msg_data = response.json()
        if msg_data.get("ok"):
            pending_users[user_id] = chat_id
            thread = threading.Thread(target=remove_user_if_pending, args=(chat_id, user_id))
            thread.daemon = True
            thread.start()

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
                {"text": "🎮 Jogar Rhaps Catcher", "callback_data": "play_game"}
            ],
            [{"text": "📱 Redes sociais", "callback_data": "redes_sociais"}]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard,
        "disable_web_page_preview": True
    }

    response = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
    if response.status_code == 200:
        msg_data = response.json()
        if msg_data.get("ok"):
            last_welcome_message[chat_id] = msg_data["result"]["message_id"]

def send_faq(chat_id):
    faq_text = (
        "📌 *Aqui está a lista de perguntas frequentes atualizada sobre o Rhapsody Protocol*\n\n"
        "*Em que situação está o projeto atualmente?*\n"
        "O Rhapsody Protocol está em fase de pré-venda, que vai até 20 de janeiro de 2026 na plataforma CriptoCash. O lançamento oficial do token $RHAP ocorrerá em 23 de janeiro de 2026 na Bitcoin Brasil (BBT). A Musicplayce é apenas o primeiro case de uso dentro do protocolo — uma demonstração prática de como empresas podem integrar gamificação, NFTs e recompensas com RHAP.\n\n"
        "*O token $RHAP já foi lançado?*\n"
        "Não, o token $RHAP ainda não foi lançado publicamente. Ele será disponibilizado oficialmente em 23 de janeiro de 2026 na Bitcoin Brasil, após encerrar a pré-venda em 20 de janeiro na CriptoCash.\n\n"
        "*Em qual rede o projeto e o token serão lançados?*\n"
        "O Rhapsody Protocol e o token $RHAP operam na rede Ethereum, seguindo o padrão ERC-20. Essa escolha garante compatibilidade com wallets amplamente utilizadas, segurança e acesso ao ecossistema DeFi consolidado.\n\n"
        "*Qual o supply total do token $RHAP?*\n"
        "O supply total é fixo em 1.000.000.000 (1 bilhão) de tokens RHAP. Não haverá novas emissões além desse limite, garantindo escassez programada.\n\n"
        "*Qual será a função do token $RHAP?*\n"
        "O $RHAP é o token utilitário central do ecossistema. Ele será usado para:\n"
        "- Acessar e interagir com aplicações gamificadas (como Rhaps Catcher),\n"
        "- Participar de mecânicas de gacha, staking e recompensas,\n"
        "- Mintar NFTs certificados com utilidade real,\n"
        "- Futuramente, votar em decisões da DAO e pagar por serviços dentro do protocolo.\n\n"
        "*Qual a função dos usuários nessa fase do projeto?*\n"
        "Nesta fase, os usuários podem:\n"
        "- Participar da pré-venda (até 20/01/2026 em CriptoCash),\n"
        "- Se preparar para o lançamento oficial (23/01/2026 na Bitcoin Brasil),\n"
        "- Acompanhar os cases de uso como o Rhaps Catcher (jogo gamificado),\n"
        "- *Tornar-se um parceiro de divulgação*: se você tem um canal, comunidade ou audiência e quer promover o Rhapsody Protocol, inscreva-se no programa de afiliados e ganhe até *15% de comissão* sobre todas as vendas geradas por você!\n\n"
        "*Terá recompensas para os participantes da pré-venda?*\n"
        "Sim! Os participantes da pré-venda terão acesso antecipado, possíveis bonificações de alocação, e poderão ser os primeiros a utilizar o token em aplicações reais do ecossistema, como o Rhaps Catcher e o marketplace de NFTs."
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

def send_game(chat_id):
    """Envia o botão do jogo Rhaps Catcher com Web App"""
    keyboard = {
        "inline_keyboard": [
            [{
                "text": "🎮 Jogar Rhaps Catcher",
                "web_app": {"url": GAME_URL}
            }]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "🌟 *Bem-vindo ao Rhaps Catcher!*\n\n"
                "Colete moedas $RHAP no nosso jogo exclusivo!\n\n"
                "💡 *Controles:*\n"
                "• 🖱️ Mouse ou 👉 Toque para mover\n"
                "• ⌨️ Setas ou botões para mobile\n\n"
                "⚡ A velocidade aumenta conforme você pega moedas!\n\n"
                "Seu recorde pessoal é salvo automaticamente.",
        "parse_mode": "Markdown",
        "reply_markup": keyboard
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
        "text": "🚀 *Ótima pergunta!*\n\n"
                "Você pode adquirir $RHAP na plataforma CriptoCash durante a pré-venda (até 20/01/2026).\n\n"
                "O lançamento oficial acontecerá em 23/01/2026 na Bitcoin Brasil (BBT).",
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

        if "new_chat_member" in message:
            new_member = message["new_chat_member"]
            user_id = new_member.get("id")
            if str(user_id) == BOT_ID:
                return "OK"
            first_name = new_member.get("first_name", "amigo")
            send_captcha(chat_id, user_id, first_name)
            return "OK"

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
            
            if text == "/jogo":
                send_game(chat_id)
                return "OK"

            if text == "/faq":
                send_faq(chat_id)
                return "OK"

            if text == "/redes":
                send_social_media(chat_id)
                return "OK"

            if text == "/comprar":
                send_buy_message(chat_id)
                return "OK"

            # Detecta gatilhos de compra em mensagens normais
            if any(trigger in text for trigger in TRIGGERS):
                send_buy_message(chat_id)
                return "OK"

    # Callback queries (botões inline)
    if data and "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        callback_data = callback["data"]
        user_id = callback["from"]["id"]

        if callback_data == "captcha_" + str(user_id):
            if user_id in pending_users:
                pending_users.pop(user_id, None)
                response = requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={
                    "callback_query_id": callback["id"],
                    "text": "✅ Bem-vindo! Você foi verificado.",
                    "show_alert": False
                })
            return "OK"

        if callback_data == "faq":
            send_faq(chat_id)
            requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
            return "OK"

        if callback_data == "play_game":
            send_game(chat_id)
            requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
            return "OK"

        if callback_data == "redes_sociais":
            send_social_media(chat_id)
            requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
            return "OK"

    return "OK"

# --- ROTAS ---
@app.route("/", methods=["GET"])
def index():
    return "Bot Rhapsody Protocol + Rhaps Catcher running!", 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

