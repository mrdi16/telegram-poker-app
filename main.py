# main.py
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN, ADMIN_ID
from bot.bot_handlers import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Сохраняем ID админа
    application.bot_data['admin_id'] = ADMIN_ID
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("poker", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()