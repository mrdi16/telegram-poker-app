import logging
from typing import Dict, Tuple
from datetime import datetime

class ChipManager:
    def __init__(self):
        self.transaction_log = []
    
    def add_chips(self, player, amount: float, admin_id: int, reason: str = "") -> Tuple[bool, str]:
        """Добавить фишки игроку"""
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        
        player.chips += amount
        
        # Логируем операцию
        self._log_transaction(
            admin_id=admin_id,
            player_id=player.user_id,
            player_name=player.username,
            amount=amount,
            operation_type="ADD",
            reason=reason
        )
        
        return True, f"Игроку {player.username} добавлено {amount} фишек. Теперь у него: {player.chips}"
    
    def remove_chips(self, player, amount: float, admin_id: int, reason: str = "") -> Tuple[bool, str]:
        """Убрать фишки у игрока"""
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        
        if player.chips < amount:
            return False, f"Недостаточно фишек. У игрока: {player.chips}"
        
        player.chips -= amount
        
        # Логируем операцию
        self._log_transaction(
            admin_id=admin_id,
            player_id=player.user_id,
            player_name=player.username,
            amount=amount,
            operation_type="REMOVE",
            reason=reason
        )
        
        return True, f"У игрока {player.username} убрано {amount} фишек. Теперь у него: {player.chips}"
    
    def set_chips(self, player, new_amount: float, admin_id: int, reason: str = "") -> Tuple[bool, str]:
        """Установить точное количество фишек"""
        if new_amount < 0:
            return False, "Количество фишек не может быть отрицательным"
        
        old_amount = player.chips
        player.chips = new_amount
        
        # Логируем операцию
        self._log_transaction(
            admin_id=admin_id,
            player_id=player.user_id,
            player_name=player.username,
            amount=new_amount - old_amount,
            operation_type="SET",
            reason=f"{reason} (было: {old_amount}, стало: {new_amount})"
        )
        
        return True, f"Фишки игрока {player.username} установлены: {new_amount}"
    
    def transfer_chips(self, from_player, to_player, amount: float, admin_id: int, reason: str = "") -> Tuple[bool, str]:
        """Перевести фишки между игроками"""
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        
        if from_player.chips < amount:
            return False, f"У {from_player.username} недостаточно фишек"
        
        from_player.chips -= amount
        to_player.chips += amount
        
        # Логируем операцию
        self._log_transaction(
            admin_id=admin_id,
            player_id=from_player.user_id,
            player_name=from_player.username,
            amount=-amount,
            operation_type="TRANSFER_OUT",
            reason=f"Перевод {to_player.username}: {reason}"
        )
        
        self._log_transaction(
            admin_id=admin_id,
            player_id=to_player.user_id,
            player_name=to_player.username,
            amount=amount,
            operation_type="TRANSFER_IN",
            reason=f"Перевод от {from_player.username}: {reason}"
        )
        
        return True, f"Переведено {amount} фишек от {from_player.username} к {to_player.username}"
    
    def _log_transaction(self, admin_id: int, player_id: int, player_name: str, amount: float, operation_type: str, reason: str):
        """Логирование операций с фишками"""
        transaction = {
            'timestamp': datetime.now(),
            'admin_id': admin_id,
            'player_id': player_id,
            'player_name': player_name,
            'amount': amount,
            'operation_type': operation_type,
            'reason': reason,
            'new_balance': None  # Можно добавить если нужно
        }
        
        self.transaction_log.append(transaction)
        logging.info(f"CHIP_OPERATION: {operation_type} | Admin: {admin_id} | Player: {player_name} | Amount: {amount} | Reason: {reason}")
    
    def get_transaction_history(self, player_id: int = None, admin_id: int = None, limit: int = 50):
        """Получить историю операций"""
        filtered_log = self.transaction_log
        
        if player_id:
            filtered_log = [t for t in filtered_log if t['player_id'] == player_id]
        if admin_id:
            filtered_log = [t for t in filtered_log if t['admin_id'] == admin_id]
        
        return filtered_log[-limit:]