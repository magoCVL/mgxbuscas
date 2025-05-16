import mercadopago
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import asyncio
from datetime import datetime

# Configurações
TOKEN_TELEGRAM = "7974795888:AAE5S_mCFfFr98vn31EEo2doLOJIzc5rI9k"
TOKEN_MERCADO_PAGO = "APP_USR-1158aa36-1a39-4885-8d16-456c1953952a"
API_KEY_CPF = "e1833c8cfdff82a383cc295d040dcbc0deb280ad742b5c7279b13d5f7e50335a"
IMAGE_TUTORIAL = "https://i.imghippo.com/files/wjDs7486h.jpg"

ADMIN_ID = 6721636303
USUARIOS = {}  # user_id: {saldo, indicados, nome}
PAGAMENTOS = {}

sdk = mercadopago.SDK(TOKEN_MERCADO_PAGO)
logging.basicConfig(level=logging.INFO)

# MENU 2x2x1
async def start(update: Update, context):
    user = update.effective_user
    user_id = user.id
    if user_id not in USUARIOS:
        USUARIOS[user_id] = {"saldo": 0, "indicados": 0, "nome": user.first_name}

    keyboard = [
        [InlineKeyboardButton("🔎 Consultar CPF", callback_data="consultar"), InlineKeyboardButton("➕ Adicionar Saldo", callback_data="saldo")],
        [InlineKeyboardButton("👤 Carteira", callback_data="carteira"), InlineKeyboardButton("🎁 Busca Grátis", callback_data="gratis")],
        [InlineKeyboardButton("📞 Suporte", url="https://t.me/tacto7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = f"<b>Bem-vindo {user.first_name}!</b>\nEscolha uma opção abaixo:"
    await update.message.reply_html(msg, reply_markup=reply_markup)

async def handle_callback(update: Update, context):
    query = update.callback_query
    data = query.data
    if data == "consultar":
        await query.message.edit_text(
            f"<b>Como Consultar um CPF:</b>\n\nDigite o comando assim:\n<code>/cpf_12345678900</code>\n\n1 crédito será descontado do seu saldo.\n\n<a href='{IMAGE_TUTORIAL}'>Clique aqui para ver imagem</a>", parse_mode="HTML")
    elif data == "saldo":
        await query.message.edit_text("Digite /recarga VALOR (ex: /recarga 10) para gerar um PIX do valor desejado.")
    elif data == "carteira":
        user = USUARIOS.get(query.from_user.id, {})
        msg = f"👤 Nome: {user.get('nome')}\n💰 Saldo: {user.get('saldo')}\n👥 Indicados: {user.get('indicados')}"
        await query.message.edit_text(msg)
    elif data == "gratis":
        msg = ("🎁 Você ganha 1 consulta grátis a cada 5 amigos indicados.\n"
               "Peça que eles enviem seu @username na primeira mensagem que mandarem pro bot!")
        await query.message.edit_text(msg)

# CONSULTA CPF
async def comando_cpf(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in USUARIOS or USUARIOS[user_id]['saldo'] <= 0:
        await update.message.reply_text("❌ Saldo insuficiente. Use /recarga para adicionar crédito.")
        return

    cpf = update.message.text.split("_", 1)[-1]
    response = requests.get(f"https://apicpf.com/api/consulta?cpf={cpf}", headers={"X-API-KEY": API_KEY_CPF})
    if response.status_code == 200:
        USUARIOS[user_id]['saldo'] -= 1
        await update.message.reply_text(f"✅ Resultado da consulta CPF {cpf}:\n{response.text}")
    else:
        await update.message.reply_text("❌ Erro na API de consulta. Tente novamente.")

# RECARGA COM PIX
async def comando_recarga(update: Update, context):
    user_id = update.effective_user.id
    try:
        valor = float(update.message.text.split()[1])
        pref = {
            "transaction_amount": valor,
            "description": "Recarga CPF Bot",
            "payment_method_id": "pix",
            "payer": {"email": "lead@cpfbotsus.com"}
        }
        payment = sdk.payment().create(pref)
        pix = payment["response"]["point_of_interaction"]["transaction_data"]
        PAGAMENTOS[user_id] = {
            "id": payment["response"]["id"],
            "valor": valor
        }
        await update.message.reply_html(
            f"🔐 PIX criado para recarga de R${valor:.2f}:\n\n<code>{pix['qr_code']}</code>\n\n<a href='{pix['qr_code_base64']}'>Clique aqui para pagar</a>\n\nApós pagar, seu saldo será atualizado automaticamente."
        )
    except Exception as e:
        logging.error(f"Erro ao gerar PIX: {e}")
        await update.message.reply_text("❌ Comando inválido. Use: /recarga VALOR")

# ADM ADICIONA SALDO
async def comando_addsaldo(update: Update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Você não tem permissão pra usar esse comando.")
        return

    try:
        partes = update.message.text.split()
        alvo = int(partes[1])
        valor = int(partes[2])

        if alvo not in USUARIOS:
            USUARIOS[alvo] = {"saldo": 0, "indicados": 0, "nome": "SemNome"}

        USUARIOS[alvo]['saldo'] += valor
        await update.message.reply_text(f"✅ Saldo de {valor} adicionado para ID {alvo}.")
    except:
        await update.message.reply_text("❌ Use corretamente: /addsaldo ID VALOR")

# SETUP
if __name__ == '__main__':
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recarga", comando_recarga))
    app.add_handler(CommandHandler("addsaldo", comando_addsaldo))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^/cpf_\d{11}$"), comando_cpf))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
