from yookassa import Payment, Configuration
from datetime import datetime

# Ваши данные для ЮKassa
account_id = "your_account_id"  # Укажите свой account_id
secret_key = "your_secret_key"  # Укажите свой secret_key

# Настройка ЮKassa с вашими данными
Configuration.configure(account_id=account_id, secret_key=secret_key)

async def create_recurring_payment(user_id: str, amount: int, description: str):
    """Создает платеж для привязки карты с подпиской на рекуррентную оплату"""
    try:
        # Создаем рекуррентный платеж
        payment = Payment.create({
            "amount": {
                "value": str(amount),  # Сумма подписки
                "currency": "RUB"
            },
            "capture_mode": "AUTOMATIC",
            "confirmation": {
                "type": "redirect",
                "return_url": "https://your_website.com/success"  # URL для возврата после успешного платежа
            },
            "description": description,
            "subscription": {
                "frequency": "weekly",  # Частота платежей: еженедельно
                "count": 0  # Неограниченное количество платежей
            }
        })
        
        # Возвращаем ссылку для перенаправления пользователя на страницу для ввода данных карты
        return payment.confirmation.confirmation_url
    except Exception as e:
        print(f"Ошибка при создании рекуррентного платежа: {e}")
        return None
