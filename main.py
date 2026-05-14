import telebot
import requests
import random
import g4f
import threading
import time
from datetime import datetime

# --- НАСТРОЙКИ ---
TOKEN = 'ТВОЙ_ТОКЕН_ТЕЛЕГРАМ'
MY_CHAT_ID = 123456789  # ВСТАВЬ СВОЙ ID СЮДА
bot = telebot.TeleBot(TOKEN)

# Данные для слежки
last_price = None
last_week_price = None
last_news_title = ""

def get_aaa():
    length = random.randint(3, 7)
    return "".join(random.choice(['а', 'А']) for _ in range(length)) + "..."

def ask_free_ai(prompt, limit=100):
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "system", "content": f"Ты Директор-Циник. Ответ до {limit} симв. В начале '{get_aaa()}'."},
                      {"role": "user", "content": prompt}]
        )
        return response[:limit]
    except: return f"{get_aaa()} ИИ занят. Жди."

# --- ФОНОВЫЙ МОНИТОРИНГ (Работает 24/7) ---
def monitor_engine():
    global last_price, last_week_price, last_news_title
    
    while True:
        try:
            now = datetime.now()
            aaa = get_aaa()
            
            # 1. ПРОВЕРКА ЦЕНЫ (10%)
            res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=starknet&vs_currencies=usd").json()
            price = res['starknet']['usd']
            
            if last_price:
                diff = (price - last_price) / last_price
                if abs(diff) >= 0.10:
                    trend = "ВЗЛЕТ" if diff > 0 else "ОБВАЛ"
                    bot.send_message(MY_CHAT_ID, f"{aaa} STRK {trend} на {abs(diff)*100:.0f}%! Цена: ${price}. Твои 13k монет теперь стоят ${price*13000:,.0f}.")
                    last_price = price # Обновляем точку отсчета

            if last_price is None: last_price = price
            if last_week_price is None: last_week_price = price

            # 2. ДЕНЬ РОЖДЕНИЯ (06.24)
            if now.strftime("%m.%d") == "06.24" and now.hour == 9 and now.minute == 0:
                bot.send_message(MY_CHAT_ID, f"{aaa} С днюхой, Валентин. Стань богаче, чтобы не бесить меня.")

            # 3. НОВОСТИ И ИИ-ФИЛЬТР
            # Тянем новости через открытый API (пример CryptoPanic или подобных)
            news_res = requests.get("https://cryptopanic.com/api/v1/posts/?kind=news&currencies=STRK,BTC,ETH&public=true").json()
            latest_news = news_res['results'][0]['title']
            
            if latest_news != last_news_title:
                # Спрашиваем ИИ, важна ли новость для STRK
                check_prompt = f"Эта новость влияет на монету Starknet? Ответь только ДА или НЕТ. Новость: {latest_news}"
                decision = ask_free_ai(check_prompt, limit=10)
                
                if "ДА" in decision.upper():
                    bot.send_message(MY_CHAT_ID, f"{aaa} ВАЖНО: {latest_news}. Анализируй, раб.")
                last_news_title = latest_news

            # 4. РАЗЛОКИ (15-е число)
            if now.day == 14 and now.hour == 12: # За день
                bot.send_message(MY_CHAT_ID, f"{aaa} Завтра разлок 127M STRK. Готовь стаканы.")
            if now.day == 15 and now.hour == 8: # За час (условно)
                bot.send_message(MY_CHAT_ID, f"{aaa} РАЗЛОК ЧЕРЕЗ ЧАС. Не спи, пухляш.")

            # 5. ОТЧЕТ ЗА НЕДЕЛЮ (каждое воскресенье в 18:00)
            if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
                w_diff = (price - last_week_price) / last_week_price
                bot.send_message(MY_CHAT_ID, f"{aaa} Итог недели: STRK {'вырос' if w_diff>0 else 'упал'} на {abs(w_diff)*100:.1f}%.")
                last_week_price = price

        except Exception as e: print(f"Ошибка монитора: {e}")
        time.sleep(600) # Проверка раз в 10 минут

# Запуск мониторинга
threading.Thread(target=monitor_engine, daemon=True).start()

# --- ОБЫЧНОЕ ОБЩЕНИЕ ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    is_crypto = any(word in message.text.lower() for word in ['strk', 'btc', 'eth', 'starknet'])
    limit = 100 if is_crypto else 25
    response = ask_free_ai(message.text, limit=limit)
    bot.reply_to(message, response)

if __name__ == "__main__":
    bot.infinity_polling()
