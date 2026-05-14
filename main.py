import telebot
import requests
import random
from groq import Groq
import threading
import time
import os
from datetime import datetime

# --- НАСТРОЙКИ ---
# Убедись, что добавил BOT_TOKEN в настройки Render!
TOKEN = os.getenv('BOT_TOKEN')
MY_CHAT_ID = int(os.getenv('MY_CHAT_ID', 505230353))

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Данные для слежки
last_price = None
last_week_price = None

def get_aaa():
    length = random.randint(3, 7)
    return "".join(random.choice(['а', 'А']) for _ in range(length)) + "..."

def get_strk_price():
    """Получение цены Starknet с CoinGecko"""
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=starknet&vs_currencies=usd", timeout=10).json()
        return res['starknet']['usd']
    except:
        return None

def ask_groq_ai(prompt, limit=500):
    """Ответ от Директора через Groq"""
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": f"Ты Директор-Циник. Ответ короткий, до {limit} симв. В начале всегда пиши '{get_aaa()}'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens= limit // 2 
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Ошибка Groq: {e}")
        return f"{get_aaa()} Мозг перегрелся. Жди."

# --- ФОНОВЫЙ МОНИТОРИНГ ---
def monitor_engine():
    global last_price, last_week_price
    
    while True:
        try:
            now = datetime.now()
            aaa = get_aaa()
            price = get_strk_price()
            
            if price:
                # 1. ПРОВЕРКА РЕЗКОГО ИЗМЕНЕНИЯ (10%)
                if last_price:
                    diff = (price - last_price) / last_price
                    if abs(diff) >= 0.10:
                        trend = "ВЗЛЕТ" if diff > 0 else "ОБВАЛ"
                        bot.send_message(MY_CHAT_ID, f"{aaa} STRK {trend} на {abs(diff)*100:.0f}%! Цена: ${price}. Твои 13k стоят ${price*13000:,.0f}.")
                        last_price = price

                if last_price is None: last_price = price
                if last_week_price is None: last_week_price = price

                # 2. ОТЧЕТ ЗА НЕДЕЛЮ (Воскресенье 18:00)
                if now.weekday() == 6 and now.hour == 18 and now.minute < 10:
                    w_diff = (price - last_week_price) / last_week_price
                    bot.send_message(MY_CHAT_ID, f"{aaa} Итог недели: STRK {'вырос' if w_diff>0 else 'упал'} на {abs(w_diff)*100:.1f}%.")
                    last_week_price = price

            # 3. ДЕНЬ РОЖДЕНИЯ (06.24)
            if now.strftime("%m.%d") == "06.24" and now.hour == 9 and now.minute < 10:
                bot.send_message(MY_CHAT_ID, f"{aaa} С днюхой, Валентин. Стань богаче.")

            # 4. РАЗЛОКИ (15-е число)
            # Сегодня 14 мая, напоминание на 12:00 уже прошло, ждем завтра 08:00
            if now.day == 15 and now.hour == 8 and now.minute < 10:
                bot.send_message(MY_CHAT_ID, f"{aaa} РАЗЛОК 13 000 STRK СЕГОДНЯ. Не спи.")

        except Exception as e: 
            print(f"Ошибка монитора: {e}")
        
        time.sleep(600) # Проверка раз в 10 минут

# Запуск мониторинга в отдельном потоке
threading.Thread(target=monitor_engine, daemon=True).start()

# --- ОБЩЕНИЕ ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    text = message.text.lower()
    
    # Реакция на крипту
    if any(word in text for word in ['strk', 'starknet', 'цена', 'курс']):
        price = get_strk_price()
        if price:
            bot.reply_to(message, f"📊 Курс STRK: ${price}\n💰 Твои 13,000 монет: ${price*13000:,.2f}\n🚀 Разлок — завтра, 15 мая!")
        else:
            bot.reply_to(message, "Не смог поймать цену, но разлок точно завтра!")
        return

    # Остальное — через Groq
    response = ask_groq_ai(message.text)
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("Директор запущен...")
    bot.infinity_polling()
