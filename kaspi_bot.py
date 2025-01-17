import logging
import requests
import time
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Токен твоего Telegram-бота
TOKEN = '7624858629:AAEqjSLnmAbxewipW4TetFX78BlYAWXerds'
# Твой Telegram чат ID
CHAT_ID = 'A1KaspiShop_bot'

# Твой API ключ Kaspi
KASPI_API_KEY = 'p/rDNokBkAvEj6cRgFvKSAXgYIWRx7fKUqvITAz4bj4='
# URL для получения заказов (замени на реальный URL)
KASPI_ORDERS_URL = 'https://kaspi.kz/mc/#/current-orders?status=NEW'

# Инициализация Telegram-бота
bot = Bot(token=TOKEN)

# Логирование
logging.basicConfig(level=logging.INFO)

# Функция для отправки уведомлений в Telegram
def send_telegram_notification(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")

# Функция для получения заказов с Kaspi API
def get_orders_from_kaspi():
    headers = {
        'Authorization': f'Bearer {KASPI_API_KEY}',  # Заголовок для аутентификации
        'Content-Type': 'application/json',
    }

    # Выполняем запрос к API Kaspi
    response = requests.get(KASPI_ORDERS_URL, headers=headers)

    if response.status_code == 200:
        # Если запрос успешен, возвращаем данные о заказах
        return response.json()
    else:
        logging.error(f"Ошибка при запросе к API Kaspi: {response.status_code}")
        return None

# Функция для проверки новых заказов и отправки уведомлений
def check_new_orders():
    orders = get_orders_from_kaspi()
    
    if orders:
        # Пример обработки полученных заказов
        for order in orders:
            order_id = order.get('order_id', 'неизвестен')
            customer_name = order.get('customer_name', 'неизвестен')
            total_amount = order.get('total_amount', 'неизвестна')
            
            # Добавляем наименование товара и количество
            items = order.get('items', [])
            item_details = ""
            for item in items:
                item_name = item.get('item_name', 'неизвестно')
                quantity = item.get('quantity', 'неизвестно')
                item_details += f"\n- {item_name}, Количество: {quantity}"

            # Формируем сообщение для Telegram
            message = f"Новый заказ:\nID: {order_id}\nКлиент: {customer_name}\nСумма: {total_amount}\nТовары:{item_details}"

            # Отправляем уведомление в Telegram
            send_telegram_notification(message)

# Обработчик команды /start
async def start(update, context):
    await update.message.reply_text("Привет! Я твой бот, готов отправлять уведомления о новых заказах!")

# Главная функция для периодической проверки заказов
async def main():
    # Создаем объект Application и передаем токен
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    
    # Запускаем бота в фоне
    await application.run_polling()

    # Запускаем проверку заказов с задержкой
    while True:
        check_new_orders()  # Проверяем новые заказы
        time.sleep(300)  # Ожидаем 5 минут (300 секунд) перед следующим запросом

# Запуск бота, если скрипт выполняется напрямую
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Создаем задачу для main
    loop.run_forever()  # Запускаем бесконечный цикл событий
