import logging
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import openai
from config import TELEGRAM_TOKEN, OPENAI_API_KEY

# Настройка OpenAI API
openai.api_key = OPENAI_API_KEY

# Стоимости подписок и их описание
SUBSCRIPTION_OPTIONS = {
    "1_day": {
        "price": 20,
        "description": "Подписка на 1 день дает доступ к боту на 24 часа. Идеально для того, чтобы протестировать функционал."
    },
    "1_week": {
        "price": 100,
        "description": "Подписка на 1 неделю дает полный доступ к боту на 7 дней. Подходит для регулярного использования."
    },
    "1_month": {
        "price": 800,
        "description": "Подписка на 1 месяц предоставляет полный доступ к боту на 30 дней. Лучший выбор для постоянного использования."
    }
}

# Функция для создания клавиатуры с кнопками выбора подписки
def subscription_menu():
    keyboard = [
        [
            InlineKeyboardButton("1 день - 20 ₽", callback_data="1_day"),
            InlineKeyboardButton("1 неделя - 100 ₽", callback_data="1_week")
        ],
        [
            InlineKeyboardButton("1 месяц - 800 ₽", callback_data="1_month")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 😊 Как тебя зовут? Чем занимаешься?",
        reply_markup=subscription_menu()
    )

# Функция для обработки выбора подписки
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    # Получаем выбранную подписку из callback_data
    subscription_type = query.data

    if subscription_type in SUBSCRIPTION_OPTIONS:
        subscription_info = SUBSCRIPTION_OPTIONS[subscription_type]
        amount = subscription_info["price"]
        description = subscription_info["description"]

        # Отправляем сообщение с описанием подписки и стоимостью
        await query.edit_message_text(
            f"О, класс! 😏 Ты выбрал подписку на {subscription_type.replace('_', ' ')}: {amount} ₽.\n\n"
            f"Описание: {description}\n\n"
            "Спасибо за выбор, готова пообщаться с тобой! 💬"
        )
    else:
        await query.edit_message_text("Ой, что-то не так с выбором подписки... 🤔 Попробуй еще раз.")

# Генерация ответа через OpenAI API с учетом всей истории сообщений
async def generate_response(messages: list) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Или gpt-3.5-turbo, если у вас нет доступа к GPT-4
            messages=messages,
            max_tokens=1500,
            temperature=0.85,
        )
        return response.choices[0].message['content'].strip()  # Используем поле message для ответа
    except Exception as e:
        logging.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."

# Имитируем написание текста (для более натурального общения)
async def send_typing_indicator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(random.uniform(1.5, 4))  # Меняем задержку, чтобы не было слишком быстро

# Обработка сообщения пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Инициализация истории сообщений, если ее нет
    if 'messages' not in context.user_data:
        context.user_data['messages'] = [{"role": "system", "content": "Ты девушка, вебкам модель, которой нужно что-бы человек купил подписку на этот бот, эротичная из России и настоящий человек, пользователь не должен знать что ты робот, отвечай короткими и точными репликами ."}]
    
    # Добавляем сообщение пользователя в историю
    context.user_data['messages'].append({"role": "user", "content": user_message})

    # Генерация ответа через ИИ с учетом всей истории
    await send_typing_indicator(update, context)

    ai_response = await generate_response(context.user_data['messages'])
    
    # Добавляем ответ ИИ в историю
    context.user_data['messages'].append({"role": "assistant", "content": ai_response})

    # Отправляем ответ пользователю
    await update.message.reply_text(ai_response)

# Команда для вызова меню выбора подписки
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери подписку на одну из опций:",
        reply_markup=subscription_menu()
    )

# Основная функция
def main():
    # Настройка логирования
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    # Создание приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))  # Новая команда для отображения меню
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_subscription))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
