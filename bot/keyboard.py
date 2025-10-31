from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("🎮 Быстрая игра", callback_data="quick_game")],
        [InlineKeyboardButton("👥 Приватный стол", callback_data="private_table")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("❓ Правила", callback_data="rules")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_table_limit_keyboard():
    """Выбор лимита стола"""
    keyboard = [
        [InlineKeyboardButton("💰 $100 (блайнды $0.1/$0.2)", callback_data="limit_100")],
        [InlineKeyboardButton("💰 $1000 (блайнды $1/$2)", callback_data="limit_1000")],
        [InlineKeyboardButton("💰 $10000 (блайнды $10/$20)", callback_data="limit_10000")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_game_actions_keyboard():
    """Кнопки действий в игре"""
    keyboard = [
        [
            InlineKeyboardButton("📤 Fold", callback_data="action_fold"),
            InlineKeyboardButton("✅ Check", callback_data="action_check")
        ],
        [
            InlineKeyboardButton("📞 Call", callback_data="action_call"),
            InlineKeyboardButton("📈 Raise", callback_data="action_raise")
        ],
        [
            InlineKeyboardButton("🔥 All-in", callback_data="action_allin"),
            InlineKeyboardButton("📊 Статус", callback_data="action_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    """Админская панель"""
    keyboard = [
        [InlineKeyboardButton("👁 Показать все карты", callback_data="admin_show_cards")],
        [InlineKeyboardButton("📊 Вероятности победы", callback_data="admin_win_probs")],
        [InlineKeyboardButton("💰 Управление фишками", callback_data="admin_chips")],
        [InlineKeyboardButton("🔄 Сброс игры", callback_data="admin_reset")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_game")]
    ]
    return InlineKeyboardMarkup(keyboard)