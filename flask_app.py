from flask import Flask, request
import sqlite3
import asyncio
from telegram import Bot

# BOT TOKEN e CHAT DO GRUPO
BOT_TOKEN = "7974795888:AAE5S_mCFfFr98vn31EEo2doLOJIzc5rI9k"
GROUP_CHAT_ID = -4823398373
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Função para mandar msg pro grupo após recarga
async def notify_recharge(user_id, amount):
    message = f"📩 Recarregado: R${amount:.2f} adicionados ao saldo do usuário ID {user_id}."
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Webhook recebido:", data)

    # PEGAR DADOS DO PAGAMENTO
    try:
        if 'data' in data and 'id' in data['data']:
            payment_id = data['data']['id']

            # Aqui é onde você deveria bater na API do Mercado Pago e puxar os dados do pagamento.
            # MAS PRA TESTE, vamos simular:

            # Exemplo fake (na prática: extrai user_id do description ou external_reference)
            user_id = int(request.args.get("user_id", 0))  # Pode vir como GET param
            amount = float(request.args.get("amount", 0))  # Idem

            # Atualiza saldo no banco
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()
            conn.close()

            # Dispara a notificação no Telegram
            asyncio.run(notify_recharge(user_id, amount))

            return "OK", 200
        else:
            return "Dados incompletos", 400
    except Exception as e:
        print("Erro no webhook:", e)
        return "Erro interno", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
