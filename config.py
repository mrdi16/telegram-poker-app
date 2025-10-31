# config.py
TABLE_LIMITS = {
    100: {
        "small_blind": 0.1,
        "big_blind": 0.2,
        "min_buyin": 10,
        "max_buyin": 100
    },
    1000: {
        "small_blind": 1,
        "big_blind": 2, 
        "min_buyin": 100,
        "max_buyin": 1000
    },
    10000: {
        "small_blind": 10,
        "big_blind": 20,
        "min_buyin": 1000,
        "max_buyin": 10000
    }
}

# Настройки бота
BOT_TOKEN = "8325072767:AAFFRL2ozb_XcR7SaPSJFeUZONSRS7gM8_Q"
ADMIN_ID = 5917286646  # Твой ID
ACTION_TIMEOUT = 60  # 60 секунд на ход

# Настройки сервера
WEBHOOK_URL = ""  # Пока оставляем пустым, будем использовать polling