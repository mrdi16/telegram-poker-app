import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from game.table_manager import PokerTable
from game.player_manager import Player
from admin.chip_manager import ChipManager
from admin.admin_tools import AdminTools
from admin.admin_logger import AdminLogger
from bot.keyboard import *

# Глобальные переменные (временное хранилище)
tables = {}
active_games = {}

# Инициализация админских инструментов
chip_manager = ChipManager()
admin_logger = AdminLogger()
admin_tools = AdminTools(chip_manager, admin_logger)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    welcome_text = f"""
🎉 Добро пожаловать в PokerBot, {user.first_name}!

♠️ Играйте в Техасский Холдем с друзьями!
💰 Виртуальные фишки, реальные эмоции!

Выберите действие:
    """
    
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "quick_game":
        await show_table_limits(query, context)
    
    elif data.startswith("limit_"):
        limit = int(data.split("_")[1])
        await join_quick_game(query, context, limit)
    
    elif data == "private_table":
        await create_private_table(query, context)
    
    elif data == "stats":
        await show_stats(query, context, user_id)
    
    elif data == "rules":
        await show_rules(query, context)
    
    elif data.startswith("action_"):
        await handle_game_action(query, context, data)
    
    elif data.startswith("admin_"):
        await handle_admin_action(query, context, data, user_id)
    
    elif data == "back_main":
        await start_callback(query, context)

async def show_table_limits(query, context):
    """Показать выбор лимитов"""
    text = "🎯 Выберите лимит стола:"
    await query.edit_message_text(text, reply_markup=get_table_limit_keyboard())

async def join_quick_game(query, context, limit: int):
    """Присоединиться к быстрой игре"""
    user = query.from_user
    user_id = user.id
    
    # Создаем или находим стол
    table_key = f"quick_{limit}"
    if table_key not in tables:
        tables[table_key] = PokerTable(table_id=len(tables) + 1, limit=limit)
    
    table = tables[table_key]
    
    # Проверяем является ли пользователь админом
    is_admin = (user_id == context.bot_data.get('admin_id', 0))
    
    # Добавляем игрока
    success = table.player_manager.add_player(user_id, user.first_name, 1000, is_admin=is_admin)
    
    if success:
        text = f"✅ Вы присоединились к столу ${limit}\n👥 Игроков: {len(table.player_manager.players)}/6"
        
        # Если набралось 2+ игрока, начинаем игру
        if len(table.player_manager.players) >= 2 and table.stage.name == "WAITING":
            success, message = table.start_hand()
            text += f"\n\n🎮 {message}"
            
            # Отправляем состояние игры
            for player in table.player_manager.players:
                try:
                    if player.is_admin:
                        await context.bot.send_message(
                            chat_id=player.user_id,
                            text=format_game_state(table),
                            reply_markup=get_admin_keyboard()
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=player.user_id,
                            text=format_game_state(table),
                            reply_markup=get_game_actions_keyboard()
                        )
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения игроку {player.user_id}: {e}")
    else:
        text = "❌ Вы уже присоединены к этому столу"
    
    # Отправляем ответ пользователю
    if is_admin:
        await query.edit_message_text(text, reply_markup=get_admin_keyboard())
    else:
        await query.edit_message_text(text, reply_markup=get_game_actions_keyboard())

async def create_private_table(query, context):
    """Создать приватный стол"""
    user = query.from_user
    text = "🔒 Функция приватных столов скоро будет доступна!"
    await query.edit_message_text(text, reply_markup=get_main_menu_keyboard())

async def show_stats(query, context, user_id: int):
    """Показать статистику игрока"""
    # Ищем игрока во всех столах
    player_stats = None
    for table in tables.values():
        player = table.player_manager.get_player(user_id)
        if player:
            player_stats = player
            break
    
    if player_stats:
        text = f"""
📊 Статистика {player_stats.username}:

🎯 Сыграно рук: {player_stats.hands_played}
🏆 Побед: {player_stats.hands_won}
📈 Процент побед: {player_stats.win_rate:.1f}%
💰 Самый большой выигрыш: ${player_stats.biggest_win}
💵 Текущий баланс: ${player_stats.chips}
        """
    else:
        text = "📊 У вас еще нет статистики. Сыграйте первую игру!"
    
    await query.edit_message_text(text, reply_markup=get_main_menu_keyboard())

async def show_rules(query, context):
    """Показать правила игры"""
    rules_text = """
📖 Правила Техасского Холдема:

🎯 Цель игры: Собрать лучшую покерную комбинацию из 5 карт.

🃏 Карты:
• Каждый игрок получает 2 карты в закрытую
• На стол выкладывается 5 общих карт

📈 Стадии игры:
1. Префлоп - раздаются карты игрокам
2. Флоп - выкладываются 3 общие карты
3. Тёрн - 4-я общая карта
4. Ривер - 5-я общая карта
5. Вскрытие - игроки показывают карты

⚡ Действия:
• Fold - сбросить карты, выйти из раздачи
• Check - пропустить ход (если не было ставок)
• Call - уравнять текущую ставку
• Raise - повысить ставку
• All-in - поставить все фишки

⏰ На ход дается 60 секунд!
    """
    await query.edit_message_text(rules_text, reply_markup=get_main_menu_keyboard())

async def handle_game_action(query, context, action: str):
    """Обработка игровых действий"""
    user_id = query.from_user.id
    
    # Находим стол с игроком
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        await query.edit_message_text("❌ Вы не в игре!", reply_markup=get_main_menu_keyboard())
        return
    
    player = table.player_manager.get_player(user_id)
    action_type = action.replace("action_", "").upper()
    
    if action_type == "FOLD":
        success, message = table.make_action(player, table.player_manager.players[0].__class__.PlayerAction.FOLD)
    elif action_type == "CHECK":
        success, message = table.make_action(player, table.player_manager.players[0].__class__.PlayerAction.CHECK)
    elif action_type == "CALL":
        success, message = table.make_action(player, table.player_manager.players[0].__class__.PlayerAction.CALL)
    elif action_type == "RAISE":
        # Здесь нужно запросить сумму рейза
        await query.edit_message_text("📈 Введите сумму рейза:")
        context.user_data['awaiting_raise'] = True
        context.user_data['current_table'] = table_key
        return
    elif action_type == "ALLIN":
        success, message = table.make_action(player, table.player_manager.players[0].__class__.PlayerAction.ALL_IN)
    elif action_type == "STATUS":
        await send_game_state(table, context, user_id)
        return
    
    if success:
        await query.edit_message_text(f"✅ {message}")
        await send_game_state(table, context)
    else:
        await query.edit_message_text(f"❌ {message}")

async def handle_admin_action(query, context, action: str, user_id: int):
    """Обработка админских действий"""
    # Проверяем права админа
    if user_id != context.bot_data.get('admin_id'):
        await query.answer("❌ У вас нет прав администратора!", show_alert=True)
        return
    
    action_type = action.replace("admin_", "")
    
    # Находим активный стол
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        await query.edit_message_text("❌ Вы не в игре!")
        return
    
    if action_type == "show_cards":
        all_cards = admin_tools.get_all_player_cards(table)
        text = "👁 Все карты игроков:\n"
        for player_name, cards in all_cards.items():
            text += f"\n{player_name}: {[str(card) for card in cards]}"
        
        await query.edit_message_text(text, reply_markup=get_admin_keyboard())
    
    elif action_type == "win_probs":
        probs = admin_tools.calculate_win_probabilities(table, simulations=1000)
        text = "📊 Вероятности победы:\n"
        for player_name, prob in probs.items():
            text += f"\n{player_name}: {prob:.1f}%"
        
        await query.edit_message_text(text, reply_markup=get_admin_keyboard())
    
    elif action_type == "chips":
        await query.edit_message_text("💰 Управление фишками скоро будет доступно!", reply_markup=get_admin_keyboard())
    
    elif action_type == "reset":
        success, message = admin_tools.reset_game(table, user_id)
        await query.edit_message_text(f"🔄 {message}", reply_markup=get_admin_keyboard())

async def send_game_state(table, context, specific_user_id=None):
    """Отправить состояние игры всем игрокам"""
    game_text = format_game_state(table)
    
    for player in table.player_manager.players:
        try:
            if specific_user_id and player.user_id != specific_user_id:
                continue
                
            if player.is_admin:
                await context.bot.send_message(
                    chat_id=player.user_id,
                    text=game_text,
                    reply_markup=get_admin_keyboard()
                )
            else:
                await context.bot.send_message(
                    chat_id=player.user_id,
                    text=game_text,
                    reply_markup=get_game_actions_keyboard()
                )
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения игроку {player.user_id}: {e}")

def format_game_state(table):
    """Форматирование состояния игры для отображения"""
    text = f"""
🎯 Стол ${table.limit} | {table.stage.name}

💵 Банк: ${table.pot}
📈 Текущая ставка: ${table.current_bet}

🃏 Общие карты: {[str(card) for card in table.community_cards]}

👥 Игроки:
"""
    
    for i, player in enumerate(table.player_manager.players):
        status = ""
        if player.folded:
            status = " 📤"
        elif player.all_in:
            status = " 🔥"
        elif i == table.current_player_index:
            status = " ⭐"
        
        text += f"\n{player.username}: ${player.chips} (ставка: ${player.current_bet}){status}"
    
    return text

async def start_callback(query, context):
    """Обработка кнопки назад в главное меню"""
    await query.edit_message_text("🔙 Возвращаемся в главное меню...", reply_markup=get_main_menu_keyboard())

# WebApp обработчики
async def webapp_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализация WebApp"""
    user_id = update.effective_user.id
    is_admin = (user_id == context.bot_data.get('admin_id'))
    
    webapp_url = "https://your-domain.com/webapp/index.html"  # Замени на реальный URL
    
    keyboard = [
        [InlineKeyboardButton("🎮 Открыть Poker Table", web_app=WebAppInfo(url=webapp_url))]
    ]
    
    await update.message.reply_text(
        "🎯 Откройте интерактивный покерный стол:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных от WebApp"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user_id = update.effective_user.id
        
        method = data.get('method')
        params = data.get('params', {})
        
        response = await process_webapp_request(user_id, method, params)
        
        # Отправляем ответ обратно в WebApp
        await update.effective_message.reply_text(
            f"✅ {response.get('message', 'Успешно')}",
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        logging.error(f"WebApp error: {e}")
        await update.effective_message.reply_text("❌ Ошибка обработки запроса")

async def process_webapp_request(user_id: int, method: str, params: dict) -> dict:
    """Обработка запросов от WebApp"""
    
    if method == 'join_table':
        return await webapp_join_table(user_id, params)
    elif method == 'get_game_state':
        return await webapp_get_game_state(user_id)
    elif method == 'player_action':
        return await webapp_player_action(user_id, params)
    elif method == 'admin_show_cards':
        return await webapp_admin_show_cards(user_id)
    elif method == 'admin_win_probabilities':
        return await webapp_admin_win_probabilities(user_id)
    elif method == 'admin_reset_game':
        return await webapp_admin_reset_game(user_id)
    else:
        return {'success': False, 'message': 'Неизвестный метод'}

async def webapp_join_table(user_id: int, params: dict) -> dict:
    """WebApp: присоединение к столу"""
    limit = params.get('limit', 100)
    table_key = f"quick_{limit}"
    
    if table_key not in tables:
        tables[table_key] = PokerTable(table_id=len(tables) + 1, limit=limit)
    
    table = tables[table_key]
    player = table.player_manager.get_player(user_id)
    
    if not player:
        # Добавляем игрока
        user = await get_user_info(user_id)  # Нужно реализовать получение информации о пользователе
        is_admin = (user_id == ADMIN_ID)
        table.player_manager.add_player(user_id, user.get('first_name', 'Player'), 1000, is_admin)
    
    return {'success': True, 'message': 'Присоединено к столу'}

async def webapp_get_game_state(user_id: int) -> dict:
    """WebApp: получение состояния игры"""
    # Находим стол с игроком
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        return {'success': False, 'message': 'Игрок не найден за столом'}
    
    # Форматируем состояние игры для WebApp
    game_state = {
        'stage': table.stage.name,
        'pot': table.pot,
        'current_bet': table.current_bet,
        'community_cards': [str(card) for card in table.community_cards],
        'players': []
    }
    
    for player in table.player_manager.players:
        player_data = {
            'username': player.username,
            'user_id': player.user_id,
            'chips': player.chips,
            'current_bet': player.current_bet,
            'folded': player.folded,
            'all_in': player.all_in,
            'is_admin': player.is_admin,
            'is_current': (table.player_manager.players[table.current_player_index].user_id == player.user_id),
            'hole_cards': [str(card) for card in player.hole_cards] if player.user_id == user_id else None
        }
        game_state['players'].append(player_data)
    
    return {'success': True, 'game_state': game_state}

async def webapp_player_action(user_id: int, params: dict) -> dict:
    """WebApp: действие игрока"""
    action = params.get('action')
    amount = params.get('amount', 0)
    
    # Находим стол с игроком
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        return {'success': False, 'message': 'Игрок не найден'}
    
    player = table.player_manager.get_player(user_id)
    
    # Выполняем действие
    if action == 'fold':
        success, message = table.make_action(player, PlayerAction.FOLD)
    elif action == 'check':
        success, message = table.make_action(player, PlayerAction.CHECK)
    elif action == 'call':
        success, message = table.make_action(player, PlayerAction.CALL)
    elif action == 'raise':
        success, message = table.make_action(player, PlayerAction.RAISE, amount)
    elif action == 'all_in':
        success, message = table.make_action(player, PlayerAction.ALL_IN)
    else:
        return {'success': False, 'message': 'Неизвестное действие'}
    
    return {'success': success, 'message': message}

async def webapp_admin_show_cards(user_id: int) -> dict:
    """WebApp: показать все карты (админ)"""
    if user_id != ADMIN_ID:
        return {'success': False, 'message': 'Нет прав'}
    
    # Находим стол с админом
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        return {'success': False, 'message': 'Админ не за столом'}
    
    all_cards = admin_tools.get_all_player_cards(table)
    cards_str = {name: [str(card) for card in cards] for name, cards in all_cards.items()}
    
    return {'success': True, 'cards': cards_str}

async def webapp_admin_win_probabilities(user_id: int) -> dict:
    """WebApp: вероятности победы (админ)"""
    if user_id != ADMIN_ID:
        return {'success': False, 'message': 'Нет прав'}
    
    # Находим стол с админом
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        return {'success': False, 'message': 'Админ не за столом'}
    
    probabilities = admin_tools.calculate_win_probabilities(table)
    prob_str = {name: f"{prob:.1f}" for name, prob in probabilities.items()}
    
    return {'success': True, 'probabilities': prob_str}

async def webapp_admin_reset_game(user_id: int) -> dict:
    """WebApp: сброс игры (админ)"""
    if user_id != ADMIN_ID:
        return {'success': False, 'message': 'Нет прав'}
    
    # Находим стол с админом
    table = None
    for t in tables.values():
        if t.player_manager.get_player(user_id):
            table = t
            break
    
    if not table:
        return {'success': False, 'message': 'Админ не за столом'}
    
    success, message = admin_tools.reset_game(table, user_id)
    return {'success': success, 'message': message}

async def get_user_info(user_id: int) -> dict:
    """Получение информации о пользователе (заглушка)"""
    # В реальной реализации здесь будет запрос к API Telegram
    return {'first_name': f'Player{user_id}'}