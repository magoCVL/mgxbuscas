import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

API_KEY_CPF = "e1833c8cfdff82a383cc295d040dcbc0deb280ad742b5c7279b13d5f7e50335a"

async def bot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Consultar CPF", callback_data="consultar"),
         InlineKeyboardButton("Adicionar Saldo", callback_data="saldo")],
        [InlineKeyboardButton("Carteira", callback_data="carteira"),
         InlineKeyboardButton("Busca Grátis", callback_data="gratis")],
        [InlineKeyboardButton("Suporte", url="https://t.me/tacto7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Menu Principal:", reply_markup=reply_markup)

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "consultar":
        await query.edit_message_text(
            "🔍 Para consultar um CPF, digite o comando: \n/cpf_12345678900\n\nExemplo: /cpf_12345678900",
            parse_mode="HTML")

    elif query.data == "saldo":
        await query.edit_message_text(
            "💰 Para adicionar saldo, use o comando: /recarga VALOR\n\nExemplo: /recarga 10",
            parse_mode="HTML")

    elif query.data == "carteira":
        # Aqui poderia puxar do banco de dados, mock por enquanto
        await query.edit_message_text(
            "👤 Nome: Fulano\n💵 Saldo: R$ 20,00\n👥 Indicados: 3",
            parse_mode="HTML")

    elif query.data == "gratis":
        await query.edit_message_text(
            "🎁 A cada 5 amigos indicados, você ganha 1 busca grátis!\n\nCompartilhe o bot com seus amigos!",
            parse_mode="HTML")

async def consultar_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Formato inválido. Use: /cpf_12345678900")
        return

    cpf = context.args[0]
    url = f"https://apicpf.com/api/consulta?cpf={cpf}"
    headers = {"X-API-KEY": API_KEY_CPF}
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        msg = f"✅ Resultado da Consulta:\nNome: {data.get('nome')}\nCPF: {data.get('cpf')}"
    else:
        msg = "❌ Erro ao consultar CPF. Tente novamente mais tarde."

    await update.message.reply_text(msg)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", bot_menu))
    application.add_handler(CallbackQueryHandler(handle_query))
    application.add_handler(CommandHandler("cpf_", consultar_cpf))
