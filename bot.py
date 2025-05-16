import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import sqlite3
import os

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Conectar ao banco de dados
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criar tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    balance REAL,
    join_date TEXT,
    referrals INTEGER,
    referral_code TEXT,
    referred_by TEXT,
    free_credits INTEGER
)
''')
conn.commit()

# Função para iniciar o bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (user_id, name, balance, join_date, referrals, referral_code, referred_by, free_credits) VALUES (?, ?, ?, DATE("now"), ?, ?, ?, ?)',
                       (user.id, user.full_name, 0.0, 0, str(user.id), None, 1))
        conn.commit()

    keyboard = [
        [InlineKeyboardButton("💼 Carteira", callback_data='wallet')],
        [InlineKeyboardButton("➕ Adicionar Saldo", callback_data='add_balance')],
        [InlineKeyboardButton("📊 Consultar", callback_data='consult')],
        [InlineKeyboardButton("👥 Indicar Amigos", callback_data='refer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(photo=open('templates/menu_preview.jpg', 'rb'),
                                     caption="Bem-vindo ao Bot Store de Consultas!",
                                     reply_markup=reply_markup)

# Função para lidar com os botões
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'wallet':
        cursor.execute('SELECT balance, join_date, referrals, free_credits FROM users WHERE user_id = ?', (query.from_user.id,))
        user_data = cursor.fetchone()
        if user_data:
            balance, join_date, referrals, free_credits = user_data
            message = f"💼 *Carteira*\n\nSaldo: R${balance:.2f}\nConsultas Grátis: {free_credits}\nData de Entrada: {join_date}\nIndicações: {referrals}"
            await query.edit_message_text(text=message, parse_mode='Markdown')
    elif query.data == 'add_balance':
        keyboard = [
            [InlineKeyboardButton("R$15", callback_data='add_15')],
            [InlineKeyboardButton("R$30", callback_data='add_30')],
            [InlineKeyboardButton("R$50", callback_data='add_50')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Escolha o valor para adicionar saldo:", reply_markup=reply_markup)
    elif query.data == 'consult':
        await query.edit_message_text(text="Funcionalidade de consulta ainda não implementada.")
    elif query.data == 'refer':
        referral_link = f"https://t.me/MgXBuscasbot?start={query.from_user.id}"
        message = f"👥 *Indique Amigos*\n\nCompartilhe este link com seus amigos:\n{referral_link}\n\nA cada 5 amigos que se cadastrarem, você ganha uma consulta grátis!"
        await query.edit_message_text(text=message, parse_mode='Markdown')

# Função para notificar recarga
async def notify_recharge(application, user_id, amount):
    message = f"✉️ Recarregado: R${amount:.2f} adicionados ao saldo do usuário ID {user_id}."
    await application.bot.send_message(chat_id=-4823398373, text=message)

# Função principal
def main():
    application = ApplicationBuilder().token("7974795888:AAE5S_mCFfFr98vn31EEo2doLOJIzc5rI9k").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
